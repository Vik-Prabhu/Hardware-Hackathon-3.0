"""
Node Simulator — mimics 4 ESP32 sensor nodes posting to the FastAPI server.

N-01 is a camera node: it sends sensor readings like the others and also
uploads a photo from demo_photos/ every 2 minutes (scaled by --speed).

Usage:
    python simulator.py                  # normal mode (30s intervals)
    python simulator.py --speed 2        # fast mode  (2s intervals)
    python simulator.py --speed 5 --url http://192.168.1.10:8000   # custom server
"""

import argparse
import asyncio
import random
from datetime import datetime, timezone
from pathlib import Path

import aiohttp

# ── Config ───────────────────────────────────────────────────────────

NODE_IDS = ["N-01", "N-03", "N-04", "N-05"]
CAMERA_NODE = "N-01"
DEMO_PHOTOS_DIR = Path(__file__).parent / "demo_photos"

DEFAULT_INTERVAL = 30  # seconds between readings
PHOTO_INTERVAL = 120   # seconds between photo uploads (2 minutes)
DEFAULT_URL = "http://localhost:8000"


# ── Sensor model ─────────────────────────────────────────────────────

class SensorNode:
    """Simulates a single sensor node with drifting values."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        # random baselines
        self.moisture = random.uniform(40, 70)
        self.temperature = random.uniform(28, 35)
        self.battery = random.uniform(60, 90)

    def tick(self):
        """Drift values to simulate real-world behaviour."""
        # Moisture: trends downward (evaporation), occasional small bump (watering)
        self.moisture += random.gauss(-0.4, 0.6)
        self.moisture = max(10, min(95, self.moisture))

        # Temperature: random walk around current value
        self.temperature += random.gauss(0, 0.3)
        self.temperature = max(20, min(45, self.temperature))

        # Battery: very slow drain
        self.battery -= random.uniform(0.02, 0.08)
        self.battery = max(0, min(100, self.battery))

    def payload(self) -> dict:
        return {
            "moisture": round(self.moisture, 1),
            "temperature": round(self.temperature, 1),
            "battery": round(self.battery, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ── Worker coroutines ────────────────────────────────────────────────

async def run_node(session: aiohttp.ClientSession, node: SensorNode,
                   base_url: str, interval: float):
    """Continuously post sensor data for one node."""
    url = f"{base_url}/node/{node.node_id}/sensor"
    print(f"  🌱 {node.node_id}  baseline → "
          f"moisture={node.moisture:.1f}%  "
          f"temp={node.temperature:.1f}°C  "
          f"battery={node.battery:.1f}%")

    while True:
        node.tick()
        data = node.payload()
        try:
            async with session.post(url, json=data) as resp:
                if resp.status == 201:
                    print(f"  ✅ {node.node_id}  "
                          f"m={data['moisture']}%  "
                          f"t={data['temperature']}°C  "
                          f"b={data['battery']}%")
                else:
                    body = await resp.text()
                    print(f"  ⚠️ {node.node_id}  HTTP {resp.status}: {body}")
        except aiohttp.ClientError as exc:
            print(f"  ❌ {node.node_id}  connection error: {exc}")

        await asyncio.sleep(interval)


async def run_camera(session: aiohttp.ClientSession, node_id: str,
                     base_url: str, interval: float):
    """Periodically upload a random demo photo for the camera node."""
    url = f"{base_url}/node/{node_id}/photo"

    # Collect available demo images
    if not DEMO_PHOTOS_DIR.exists():
        print(f"  ⚠️ {node_id}  demo_photos/ not found — camera disabled")
        return

    images = sorted(
        f for f in DEMO_PHOTOS_DIR.iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
    )
    if not images:
        print(f"  ⚠️ {node_id}  no images in demo_photos/ — camera disabled")
        return

    print(f"  📸 {node_id}  camera active — {len(images)} demo images, "
          f"uploading every {interval:.0f}s")

    while True:
        await asyncio.sleep(interval)

        photo = random.choice(images)
        try:
            data = aiohttp.FormData()
            data.add_field(
                "file",
                open(photo, "rb"),
                filename=photo.name,
                content_type="image/jpeg",
            )
            async with session.post(url, data=data) as resp:
                if resp.status == 201:
                    print(f"  📸 {node_id}  uploaded {photo.name}")
                else:
                    body = await resp.text()
                    print(f"  ⚠️ {node_id}  photo HTTP {resp.status}: {body}")
        except aiohttp.ClientError as exc:
            print(f"  ❌ {node_id}  photo upload error: {exc}")


# ── Main ─────────────────────────────────────────────────────────────

async def main(interval: float, base_url: str):
    # Scale the photo interval by the same ratio as the sensor interval
    # e.g. --speed 2 → sensor every 2s, photos every 8s  (120/30 * 2)
    photo_ivl = PHOTO_INTERVAL * (interval / DEFAULT_INTERVAL)

    print(f"\n{'═' * 56}")
    print(f"  🚀 Green Node Simulator")
    print(f"     Nodes  : {', '.join(NODE_IDS)}")
    print(f"     Camera : {CAMERA_NODE} (photo every {photo_ivl:.0f}s)")
    print(f"     Server : {base_url}")
    print(f"     Interval: {interval}s")
    print(f"{'═' * 56}\n")

    nodes = [SensorNode(nid) for nid in NODE_IDS]

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(run_node(session, node, base_url, interval))
            for node in nodes
        ]
        # Add the camera upload task for N-01
        tasks.append(
            asyncio.create_task(run_camera(session, CAMERA_NODE, base_url, photo_ivl))
        )
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate ESP32 sensor nodes")
    parser.add_argument("--speed", type=float, default=DEFAULT_INTERVAL,
                        help=f"Seconds between readings (default: {DEFAULT_INTERVAL})")
    parser.add_argument("--url", type=str, default=DEFAULT_URL,
                        help=f"Server base URL (default: {DEFAULT_URL})")
    args = parser.parse_args()

    try:
        asyncio.run(main(interval=args.speed, base_url=args.url))
    except KeyboardInterrupt:
        print("\n\n  🛑 Simulator stopped.\n")
