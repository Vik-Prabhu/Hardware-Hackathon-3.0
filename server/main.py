"""
Green Node – Sensor Data API

FastAPI server that receives sensor readings from field nodes
and exposes history / status endpoints for the dashboard.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import aiohttp
from pydantic import BaseModel, Field
import os
import base64
import json
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import re

from database import get_connection, init_db

load_dotenv()
AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://192.168.236.84:8000")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")

PHOTOS_DIR = Path(__file__).parent / "photos"


def clean_advisory_response(advisory_json):
    """Post-process the AI server response to extract clean advisory JSON.
    
    The AI model sometimes returns the advisory JSON wrapped in markdown
    code fences (```json ... ```) inside the description field. This function
    detects that pattern and extracts the proper structured advisory.
    """
    if not isinstance(advisory_json, dict):
        return advisory_json
    
    # Dig into nested 'advisory' wrapper if present
    inner = advisory_json.get("advisory", advisory_json)
    if isinstance(inner, dict):
        desc = inner.get("description", "")
    else:
        return advisory_json
    
    # Check if description contains a JSON code block
    if isinstance(desc, str) and "```json" in desc:
        try:
            # Extract JSON from markdown code fences
            match = re.search(r'```json\s*([\s\S]*?)\s*```', desc)
            if match:
                parsed = json.loads(match.group(1))
                if isinstance(parsed, dict) and ("summary" in parsed or "problems" in parsed):
                    print(f"[AI Cleanup] Extracted structured advisory from markdown code block")
                    # Replace the inner advisory with the parsed one
                    if "advisory" in advisory_json and isinstance(advisory_json["advisory"], dict):
                        advisory_json["advisory"] = parsed
                    else:
                        advisory_json = parsed
        except (json.JSONDecodeError, Exception) as e:
            print(f"[AI Cleanup] Failed to parse JSON from description: {e}")
    
    return advisory_json

# Track the last known IP address for each node (dynamic IP support)
NODE_IPS = {}

# ── Pydantic models ─────────────────────────────────────────────────

class SensorPayload(BaseModel):
    moisture: float
    temperature: float
    humidity: float
    light: float
    battery: float
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO-8601 timestamp; defaults to server time if omitted",
    )


class SensorReading(BaseModel):
    id: int
    node_id: str
    moisture: float
    temperature: float
    humidity: float
    light: float
    battery: float
    timestamp: str


class NodePhoto(BaseModel):
    id: int
    node_id: str
    filename: str
    url: str
    captured_at: str


class RegisterPayload(BaseModel):
    ip: str


# ── App lifecycle ────────────────────────────────────────────────────

def seed_demo_photos():
    """Auto-register any images found in photos/N-01/ as demo captures."""
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM node_photos WHERE node_id = 'N-01'"
    ).fetchone()[0]
    if count == 0:
        photo_dir = PHOTOS_DIR / "N-01"
        if photo_dir.exists():
            imgs = sorted(
                f for f in photo_dir.iterdir()
                if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
            )
            base = datetime.utcnow()
            for i, img in enumerate(imgs):
                ts = (base - timedelta(minutes=15 * (len(imgs) - i))).isoformat()
                conn.execute(
                    "INSERT INTO node_photos (node_id, filename, captured_at) VALUES (?, ?, ?)",
                    ("N-01", img.name, ts),
                )
            conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    (PHOTOS_DIR / "N-01").mkdir(exist_ok=True)
    seed_demo_photos()
    
    # Start background scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_analyze_all, 'interval', minutes=5)
    scheduler.start()
    
    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(
    title="Green Node Sensor API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/photos", StaticFiles(directory=str(PHOTOS_DIR)), name="photos")


# ── Endpoints ────────────────────────────────────────────────────────

@app.post("/node/{node_id}/register")
def register_node(node_id: str, payload: RegisterPayload):
    """ESP32 calls this on boot to announce its IP address."""
    NODE_IPS[node_id] = payload.ip
    print(f"[REG] Node {node_id} registered at {payload.ip}")
    return {"status": "ok", "node_id": node_id, "ip": payload.ip}

@app.post("/node/{node_id}/sensor", response_model=SensorReading, status_code=201)
def create_reading(node_id: str, payload: SensorPayload, request: Request):
    """Store a new sensor reading from a node and record its IP."""
    # Remember the IP address the node used to contact us
    NODE_IPS[node_id] = request.client.host
    
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO sensor_readings (node_id, moisture, temperature, humidity, light, battery, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (node_id, payload.moisture, payload.temperature, payload.humidity, payload.light, payload.battery, payload.timestamp),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()

    return SensorReading(
        id=row_id,
        node_id=node_id,
        moisture=payload.moisture,
        temperature=payload.temperature,
        humidity=payload.humidity,
        light=payload.light,
        battery=payload.battery,
        timestamp=payload.timestamp,
    )


@app.get("/node/{node_id}/history", response_model=list[SensorReading])
def get_history(node_id: str):
    """Return the last 20 readings for a specific node (newest first)."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, node_id, moisture, temperature, humidity, light, battery, timestamp
        FROM sensor_readings
        WHERE node_id = ?
        ORDER BY timestamp DESC
        LIMIT 20
        """,
        (node_id,),
    ).fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No readings found for node '{node_id}'")

    return [SensorReading(**dict(r)) for r in rows]


@app.get("/nodes/all", response_model=list[SensorReading])
def get_all_latest():
    """Return the single most-recent reading for every known node."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT s.id, s.node_id, s.moisture, s.temperature, s.humidity, s.light, s.battery, s.timestamp
        FROM sensor_readings s
        INNER JOIN (
            SELECT node_id, MAX(timestamp) AS max_ts
            FROM sensor_readings
            GROUP BY node_id
        ) latest ON s.node_id = latest.node_id AND s.timestamp = latest.max_ts
        ORDER BY s.node_id
        """
    ).fetchall()
    conn.close()

    return [SensorReading(**dict(r)) for r in rows]


@app.get("/node/{node_id}/photos", response_model=list[NodePhoto])
def get_node_photos(node_id: str):
    """Return all photos captured by a node's camera (newest first)."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, node_id, filename, captured_at
        FROM node_photos
        WHERE node_id = ?
        ORDER BY captured_at DESC
        """,
        (node_id,),
    ).fetchall()
    conn.close()

    return [
        NodePhoto(
            id=r["id"],
            node_id=r["node_id"],
            filename=r["filename"],
            url=f"/photos/{r['node_id']}/{r['filename']}",
            captured_at=r["captured_at"],
        )
        for r in rows
    ]


@app.post("/node/{node_id}/photo", response_model=NodePhoto, status_code=201)
async def upload_photo(node_id: str, file: UploadFile = File(...)):
    """Accept a photo upload from a camera node (multipart/form-data)."""
    node_dir = PHOTOS_DIR / node_id
    node_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().isoformat()
    safe_name = file.filename or f"{node_id}_{ts}.jpg"
    dest = node_dir / safe_name
    contents = await file.read()
    dest.write_bytes(contents)

    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO node_photos (node_id, filename, captured_at) VALUES (?, ?, ?)",
        (node_id, safe_name, ts),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()

    return NodePhoto(
        id=row_id,
        node_id=node_id,
        filename=safe_name,
        url=f"/photos/{node_id}/{safe_name}",
        captured_at=ts,
    )


@app.post("/node/{node_id}/request-photo", response_model=NodePhoto)
async def request_photo_from_node(node_id: str):
    """Trigger the ESP32 to capture a photo + sensor data and pull it back."""
    ip = NODE_IPS.get(node_id)
    if not ip:
        raise HTTPException(
            status_code=404,
            detail=f"No known IP for node {node_id}. It hasn't registered yet."
        )

    url = f"http://{ip}/capture"
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=resp.status, detail="Failed to capture from node")
                contents = await resp.read()

                # Extract sensor data from response headers
                moisture = float(resp.headers.get("X-Moisture", 0))
                temperature = float(resp.headers.get("X-Temperature", 0))
                humidity = float(resp.headers.get("X-Humidity", 0))
                light = float(resp.headers.get("X-Light", 0))
                battery = float(resp.headers.get("X-Battery", 0))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reaching node at {ip}: {str(e)}")

    ts = datetime.utcnow().isoformat()

    # Save sensor reading
    conn = get_connection()
    conn.execute(
        "INSERT INTO sensor_readings (node_id, moisture, temperature, humidity, light, battery, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (node_id, moisture, temperature, humidity, light, battery, ts),
    )
    conn.commit()
    conn.close()
    print(f"[CAP] {node_id}: photo + sensors (m={moisture}, t={temperature}, h={humidity}, l={light}, b={battery})")

    # Save photo
    node_dir = PHOTOS_DIR / node_id
    node_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{node_id}_{ts}.jpg".replace(":", "-")
    dest = node_dir / safe_name
    dest.write_bytes(contents)

    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO node_photos (node_id, filename, captured_at) VALUES (?, ?, ?)",
        (node_id, safe_name, ts),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()

    return NodePhoto(
        id=row_id,
        node_id=node_id,
        filename=safe_name,
        url=f"/photos/{node_id}/{safe_name}",
        captured_at=ts,
    )


@app.get("/demo/photos")
def demo_photos():
    """Return 5 hardcoded mock photo entries for UI validation."""
    base = datetime.utcnow()
    return [
        {
            "filename": f"demo_{i+1}.jpg",
            "timestamp": (base - timedelta(minutes=15 * (5 - i))).isoformat(),
            "url": f"https://picsum.photos/seed/plant{i+1}/400/300",
            "captured_at": (base - timedelta(minutes=15 * (5 - i))).isoformat(),
        }
        for i in range(5)
    ]


# ── Analysis Endpoints ───────────────────────────────────────────────

@app.post("/api/analyze")
async def analyze_form_data(
    node_id: str = Form(...),
    temperature: float = Form(...),
    humidity: float = Form(...),
    soil_moisture: float = Form(...),
    light_level: float = Form(...),
    image: UploadFile = File(None)
):
    """Directly accept FormData, call AI service, and return JSON."""
    sensor_data = {
        "node_id": node_id,
        "temperature": temperature,
        "humidity": humidity,
        "soil_moisture": soil_moisture,
        "light_level": light_level,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    image_b64 = None
    if image and image.filename:
        try:
            contents = await image.read()
            image_b64 = base64.b64encode(contents).decode("utf-8")
        except Exception as e:
            print(f"[AI Proxy Error] Failed to encode uploaded image: {e}")
            
    try:
        timeout = aiohttp.ClientTimeout(total=300)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            if image_b64:
                # Use multipart FormData to forward the image
                form_data = aiohttp.FormData()
                form_data.add_field('node_id', str(node_id))
                form_data.add_field('temperature', str(int(float(sensor_data.get('temperature', 0)))))
                form_data.add_field('humidity', str(int(float(sensor_data.get('humidity', 0)))))
                form_data.add_field('soil_moisture', str(int(float(sensor_data.get('soil_moisture', 0)))))
                form_data.add_field('light_level', str(int(float(sensor_data.get('light_level', 0)))))
                # Re-read the image from the upload
                await image.seek(0)
                img_bytes = await image.read()
                # Generate filename in the format: N-01_2026-04-11T09-44-12.480248.jpg
                ts_str = datetime.utcnow().isoformat().replace(":", "-")
                img_filename = f"{node_id}_{ts_str}.jpg"
                form_data.add_field('image', img_bytes, filename=img_filename, content_type='image/jpeg')
                print(f"[AI Proxy] Sending analysis for {node_id} WITH image ({len(img_bytes)} bytes) as {img_filename}")
                async with session.post(f"{AI_SERVER_URL}/api/analyze", data=form_data) as resp:
                    if resp.status == 422:
                        print("[AI Proxy] 422 Error Details:", await resp.text())
                    resp.raise_for_status()
                    advisory_json = await resp.json()
            else:
                # No image — use simple url-encoded form data
                payload = {
                    'node_id': str(node_id),
                    'temperature': str(int(float(sensor_data.get('temperature', 0)))),
                    'humidity': str(int(float(sensor_data.get('humidity', 0)))),
                    'soil_moisture': str(int(float(sensor_data.get('soil_moisture', 0)))),
                    'light_level': str(int(float(sensor_data.get('light_level', 0))))
                }
                print(f"[AI Proxy] Sending analysis for {node_id} without image")
                async with session.post(f"{AI_SERVER_URL}/api/analyze", data=payload) as resp:
                    if resp.status == 422:
                        print("[AI Proxy] 422 Error Details:", await resp.text())
                    resp.raise_for_status()
                    advisory_json = await resp.json()
    except Exception as e:
        print(f"[AI Server Error] Proxying for {node_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # Clean up: extract JSON from markdown code fences if needed
    advisory_json = clean_advisory_response(advisory_json)
        
    # Save the advisory
    ts = sensor_data["timestamp"]
    conn = get_connection()
    conn.execute(
        "INSERT INTO advisories (node_id, advisory, timestamp) VALUES (?, ?, ?)",
        (node_id, json.dumps(advisory_json), ts)
    )
    conn.commit()
    conn.close()
    
    return {"status": "done", "advisory": advisory_json}


@app.post("/api/analyze/{node_id}")
async def run_node_analysis(node_id: str):
    """Fetch latest sensor reading/photo and call AI microservice."""
    conn = get_connection()
    reading = conn.execute(
        """
        SELECT moisture, temperature, humidity, light, battery, timestamp
        FROM sensor_readings
        WHERE node_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        (node_id,)
    ).fetchone()
    
    if not reading:
        conn.close()
        raise HTTPException(status_code=404, detail=f"No sensor readings found for {node_id}")
        
    sensor_data = dict(reading)
    sensor_data['node_id'] = node_id
    
    photo = conn.execute(
        """
        SELECT filename
        FROM node_photos
        WHERE node_id = ?
        ORDER BY captured_at DESC
        LIMIT 1
        """,
        (node_id,)
    ).fetchone()
    conn.close()
    
    advisory_json = None
    ts = datetime.utcnow().isoformat()
    
    try:
        timeout = aiohttp.ClientTimeout(total=300)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            payload = {
                'node_id': str(node_id),
                'temperature': str(int(float(sensor_data.get('temperature', 0)))),
                'humidity': str(int(float(sensor_data.get('humidity', 0)))),
                'soil_moisture': str(int(float(sensor_data.get('moisture', 0)))),
                'light_level': str(int(float(sensor_data.get('light', 0))))
            }
            
            async with session.post(f"{AI_SERVER_URL}/api/analyze", data=payload) as resp:
                if resp.status == 422:
                    print("[AI Proxy] 422 Error Details:", await resp.text())
                resp.raise_for_status()
                advisory_json = await resp.json()
    except Exception as e:
        print(f"[AI Server Error] Node {node_id}: {e}")
        advisory_json = {"status": "error", "message": str(e)}
    
    # Clean up: extract JSON from markdown code fences if needed
    advisory_json = clean_advisory_response(advisory_json)
        
    # Save advisory to DB
    conn = get_connection()
    conn.execute(
        "INSERT INTO advisories (node_id, advisory, timestamp) VALUES (?, ?, ?)",
        (node_id, json.dumps(advisory_json), ts)
    )
    conn.commit()
    conn.close()
    
    # Write to archive.jsonl
    try:
        with open("archive.jsonl", "a") as f:
            f.write(json.dumps({
                "node_id": node_id,
                "timestamp": ts,
                "sensor_data": sensor_data,
                "advisory": advisory_json
            }) + "\n")
    except Exception as e:
        print(f"[AI Server Error] Failed to write archive.jsonl: {e}")
        
    return {"status": "done", "advisory": advisory_json}


@app.post("/api/analyze/all")
async def scheduled_analyze_all():
    """Run analysis for all nodes in the background."""
    conn = get_connection()
    unique_nodes = conn.execute("SELECT DISTINCT node_id FROM sensor_readings").fetchall()
    conn.close()
    
    results = {}
    for row in unique_nodes:
        node_id = row["node_id"]
        try:
            res = await run_node_analysis(node_id)
            results[node_id] = res
        except Exception as e:
            print(f"[Analyze All Error] Node {node_id}: {e}")
            results[node_id] = {"status": "error", "message": str(e)}
            
    return results


@app.get("/node/{node_id}/advisory")
def get_node_advisory(node_id: str):
    """Retrieve the latest advisory for a specific node."""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT advisory, timestamp
        FROM advisories
        WHERE node_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        (node_id,)
    ).fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="No advisory found")
        
    try:
        data = json.loads(row["advisory"])
        data["_timestamp"] = row["timestamp"] # Include DB timestamp for convenience
        return data
    except json.JSONDecodeError:
        return {"raw": row["advisory"], "_timestamp": row["timestamp"]}


# ── Daily Plan & Sarvam AI Endpoints ─────────────────────────────────

@app.get("/api/daily-plan")
def get_daily_plan():
    """Aggregate the latest advisory from each node into one consolidated daily plan."""
    conn = get_connection()
    # Fetch latest advisory for every node
    rows = conn.execute(
        """
        SELECT a.node_id, a.advisory, a.timestamp
        FROM advisories a
        INNER JOIN (
            SELECT node_id, MAX(timestamp) AS max_ts
            FROM advisories
            GROUP BY node_id
        ) latest ON a.node_id = latest.node_id AND a.timestamp = latest.max_ts
        ORDER BY a.node_id
        """
    ).fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No advisories found. Run AI analysis first.")

    node_summaries = []
    all_problems = []
    all_solutions = []
    all_predictions_short = []
    all_predictions_long = []
    severity_counts = {"critical": 0, "warning": 0, "info": 0, "healthy": 0}

    for row in rows:
        node_id = row["node_id"]
        try:
            adv_data = json.loads(row["advisory"])
        except json.JSONDecodeError:
            continue

        # Unwrap nested advisory
        inner = adv_data
        for _ in range(5):
            if isinstance(inner, dict) and "advisory" in inner and isinstance(inner["advisory"], dict):
                inner = inner["advisory"]
            else:
                break

        # Extract clean advisory from markdown code blocks in description
        if isinstance(inner, dict) and isinstance(inner.get("description", ""), str) and "```json" in inner.get("description", ""):
            try:
                match = re.search(r'```json\s*([\s\S]*?)\s*```', inner["description"])
                if match:
                    parsed = json.loads(match.group(1))
                    if isinstance(parsed, dict) and ("summary" in parsed or "problems" in parsed):
                        inner = parsed
            except Exception:
                pass

        summary = inner.get("summary", "No analysis available")
        severity = inner.get("overall_severity", "info")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        node_summaries.append({
            "node_id": node_id,
            "summary": summary,
            "severity": severity,
            "timestamp": row["timestamp"]
        })

        # Collect problems
        for p in inner.get("problems", []):
            all_problems.append({
                "node_id": node_id,
                "issue": p.get("issue", "Unknown"),
                "details": p.get("details", ""),
                "severity": p.get("severity", "info")
            })

        # Collect solutions
        for s in inner.get("solutions", []):
            all_solutions.append({
                "node_id": node_id,
                "action": s.get("action", "Unknown"),
                "details": s.get("details", ""),
                "urgency": s.get("urgency", "monitor")
            })

        # Collect predictions
        preds = inner.get("predictions", {})
        if preds.get("short_term") and preds["short_term"] != "N/A":
            all_predictions_short.append(f"{node_id}: {preds['short_term']}")
        if preds.get("long_term") and preds["long_term"] != "N/A":
            all_predictions_long.append(f"{node_id}: {preds['long_term']}")

    # Sort solutions by urgency priority
    urgency_order = {"immediate": 0, "within_24h": 1, "monitor": 2}
    all_solutions.sort(key=lambda s: urgency_order.get(s["urgency"], 3))

    # Build a single cohesive paragraph report instead of a list
    paragraph = f"Here is your Daily Plantation Report for {datetime.utcnow().strftime('%B %d, %Y')}. "
    
    if severity_counts.get("critical", 0) > 0:
        paragraph += f"The overall condition is CRITICAL with {severity_counts['critical']} node(s) requiring immediate attention. "
    elif severity_counts.get("warning", 0) > 0:
        paragraph += f"The overall condition needs monitoring as {severity_counts['warning']} node(s) show warning signs. "
    else:
        paragraph += "The plantation is overall HEALTHY with no pressing issues. "

    urgent_issues = [f"{p['issue'].lower()} around node {p['node_id']}" for p in all_problems if p['severity'] in ['critical', 'warning']]
    if urgent_issues:
        paragraph += f"The main issues identified are {', '.join(urgent_issues)}. "

    urgent_actions = [f"{s['action'].lower()} at node {s['node_id']}" for s in all_solutions if s['urgency'] in ['immediate', 'within_24h']]
    if urgent_actions:
        paragraph += f"It is highly recommended to perform the following actions today: {', '.join(urgent_actions)}. "
    elif all_solutions:
        paragraph += "There are some minor maintenance tasks suggested, but no urgent actions are required today. "

    if all_predictions_short:
        paragraph += "If ignored, these issues may lead to reduced plant health or crop failure in the near term. "

    paragraph += "Please review the individual node dashboards for detailed sensor readings and localized advice."

    plan_text = paragraph

    return {
        "plan_text": plan_text,
        "nodes": node_summaries,
        "problems": all_problems,
        "solutions": all_solutions,
        "severity_counts": severity_counts,
        "generated_at": datetime.utcnow().isoformat()
    }


class TranslateRequest(BaseModel):
    text: str
    target_language_code: str
    source_language_code: str = "en-IN"


@app.post("/api/translate")
async def translate_text(payload: TranslateRequest):
    """Proxy translation through Sarvam AI's /translate endpoint, with chunking for large text."""
    if not SARVAM_API_KEY or SARVAM_API_KEY == "your_sarvam_api_key_here":
        raise HTTPException(status_code=500, detail="SARVAM_API_KEY not configured in .env")

    def chunk_text_func(text: str, max_len: int = 1900):
        chunks = []
        current_chunk = []
        current_len = 0
        for line in text.split('\n'):
            line_len = len(line) + 1
            if current_len + line_len > max_len and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_len = line_len
            else:
                current_chunk.append(line)
                current_len += line_len
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        return chunks

    chunks = chunk_text_func(payload.text)
    translated_chunks = []

    try:
        timeout = aiohttp.ClientTimeout(total=90)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for chunk in chunks:
                if not chunk.strip():
                    translated_chunks.append("")
                    continue
                
                async with session.post(
                    "https://api.sarvam.ai/translate",
                    headers={
                        "Content-Type": "application/json",
                        "api-subscription-key": SARVAM_API_KEY
                    },
                    json={
                        "input": chunk,
                        "source_language_code": payload.source_language_code,
                        "target_language_code": payload.target_language_code,
                        "model": "sarvam-translate:v1",
                        "mode": "formal"
                    }
                ) as resp:
                    if resp.status != 200:
                        err_text = await resp.text()
                        print(f"[Sarvam Translate Error] {resp.status}: {err_text}")
                        raise HTTPException(status_code=resp.status, detail=f"Sarvam API error: {err_text}")
                    data = await resp.json()
                    translated_chunks.append(data.get("translated_text", ""))
                    
            return {
                "translated_text": "\n".join(translated_chunks),
                "source_language_code": payload.source_language_code
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Sarvam Translate Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))


class TranslateBatchRequest(BaseModel):
    texts: list[str]
    target_language_code: str
    source_language_code: str = "en-IN"


@app.post("/api/translate-batch")
async def translate_batch(payload: TranslateBatchRequest):
    """Proxy batch translation for structured data fields concurrently."""
    if not SARVAM_API_KEY or SARVAM_API_KEY == "your_sarvam_api_key_here":
        raise HTTPException(status_code=500, detail="SARVAM_API_KEY not configured in .env")

    sem = asyncio.Semaphore(5)

    async def fetch_translation(session, text):
        if not text or not text.strip():
            return text
        async with sem:
            try:
                async with session.post(
                    "https://api.sarvam.ai/translate",
                    headers={
                        "Content-Type": "application/json",
                        "api-subscription-key": SARVAM_API_KEY
                    },
                    json={
                        "input": text[:2000],
                        "source_language_code": payload.source_language_code,
                        "target_language_code": payload.target_language_code,
                        "model": "sarvam-translate:v1",
                        "mode": "formal"
                    }
                ) as resp:
                    if resp.status == 200:
                        d = await resp.json()
                        return d.get("translated_text", text)
                    else:
                        err = await resp.text()
                        print(f"[Sarvam Translate Batch Error] {resp.status}: {err}")
                        return text
            except Exception as e:
                print(f"[Fetch Exception]: {str(e)}")
                return text

    try:
        timeout = aiohttp.ClientTimeout(total=45)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = [fetch_translation(session, text) for text in payload.texts]
            translated = await asyncio.gather(*tasks)
            return {"translated_texts": translated}
    except Exception as e:
        print(f"[Sarvam Translate Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))


class TTSRequest(BaseModel):
    text: str
    target_language_code: str


@app.post("/api/tts")
async def text_to_speech(payload: TTSRequest):
    """Proxy TTS through Sarvam AI's /text-to-speech endpoint."""
    if not SARVAM_API_KEY or SARVAM_API_KEY == "your_sarvam_api_key_here":
        raise HTTPException(status_code=500, detail="SARVAM_API_KEY not configured in .env")

    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "https://api.sarvam.ai/text-to-speech",
                headers={
                    "Content-Type": "application/json",
                    "api-subscription-key": SARVAM_API_KEY
                },
                json={
                    "inputs": [payload.text[:500]],
                    "target_language_code": payload.target_language_code,
                    "speaker": "shubh",
                    "model": "bulbul:v3"
                }
            ) as resp:
                if resp.status != 200:
                    err_text = await resp.text()
                    print(f"[Sarvam TTS Error] {resp.status}: {err_text}")
                    raise HTTPException(status_code=resp.status, detail=f"Sarvam TTS error: {err_text}")
                data = await resp.json()
                audios = data.get("audios", [])
                if not audios:
                    raise HTTPException(status_code=500, detail="No audio returned from Sarvam")
                return {"audio_base64": audios[0]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Sarvam TTS Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Run directly ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
