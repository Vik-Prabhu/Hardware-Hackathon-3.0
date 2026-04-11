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

from database import get_connection, init_db

load_dotenv()
AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://192.168.236.84:8000")

PHOTOS_DIR = Path(__file__).parent / "photos"

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
            # We use a standard dictionary to accurately mimic `requests.post(url, data=data)`
            payload = {
                'node_id': str(node_id),
                'temperature': str(int(float(sensor_data.get('temperature', 0)))),
                'humidity': str(int(float(sensor_data.get('humidity', 0)))),
                'soil_moisture': str(int(float(sensor_data.get('soil_moisture', 0)))),
                'light_level': str(int(float(sensor_data.get('light_level', 0))))
            }
            
            async with session.post(f"{AI_SERVER_URL}/api/analyze", data=payload) as resp:
                if resp.status == 422:
                    # Log the exact validation error the friend's laptop throws
                    print("[AI Proxy] 422 Error Details:", await resp.text())
                resp.raise_for_status()
                advisory_json = await resp.json()
    except Exception as e:
        print(f"[AI Server Error] Proxying for {node_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    # Save the advisory logic if you want to track it
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


# ── Run directly ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
