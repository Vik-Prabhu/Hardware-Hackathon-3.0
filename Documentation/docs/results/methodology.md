# Methodology

This section outlines how the **Green Node** system was tested end-to-end — from physical sensor deployment to AI-driven advisory generation.

---

## Test Environment

The system was deployed in a live bonsai nursery setup to validate real-world performance.

- **Location:** Indoor bonsai workstation with natural and artificial lighting
- **Duration:** Multi-session testing across April 11–12, 2026
- **Network:** Local Wi-Fi hotspot with mDNS-based node discovery

<!-- 📸 TODO: Add a photo of the physical test setup (nodes placed near plants) -->
<!-- ![Test Setup](/results/test-setup.jpg) -->

---

## Node Deployment

Two nodes were deployed simultaneously to test both sensor-only and camera-enabled workflows.

### Node N-01 — Camera + Environment Node
| Parameter | Value |
|-----------|-------|
| **MCU** | ESP32-CAM (AI-Thinker) |
| **Sensor** | DHT22 (temperature + humidity) |
| **Camera** | OV2640, SVGA 800×600 |
| **Mode** | Trigger-based — server pulls data on demand |
| **mDNS** | `green-node-01.local` |

### Node N-02 — GlyphC3 Sensor Node
| Parameter | Value |
|-----------|-------|
| **MCU** | ESP32-C3 (RISC-V) |
| **Sensors** | DHT11, Capacitive Soil Moisture, LDR |
| **Mode** | Continuous push — 30 s interval (5 s when soil is critical) |
| **mDNS** | `green-node-02.local` |

<!-- 📸 TODO: Add a photo of each node (close-up of the assembled hardware) -->
<!-- ![Node N-01](/results/node-n01.jpg) -->
<!-- ![Node N-02](/results/node-n02.jpg) -->

---

## Data Collection

### Sensor Telemetry
- N-02 pushed readings every **30 seconds** over HTTP POST to the FastAPI server
- Adaptive interval: drops to **5 seconds** when soil moisture falls below 25%
- All readings logged to SQLite with ISO-8601 timestamps

### Image Capture
- N-01 captured **49 plant photos** across multiple test sessions
- Server triggered captures via `GET /capture` on the node's local web server
- Images stored as timestamped JPEGs: `N-01_YYYY-MM-DDTHH-MM-SS.ffffff.jpg`

<!-- 📸 TODO: Add a screenshot of the serial monitor showing successful POST and capture logs -->
<!-- ![Serial Monitor Output](/results/serial-output.png) -->

---

## Software Pipeline Validation

Each stage of the data pipeline was validated independently before end-to-end testing.

| Stage | Test Method | Status |
|-------|-------------|:------:|
| **Sensor Read** | Serial monitor — verify temp, humidity, moisture, light values | ✅ |
| **WiFi + mDNS** | Ping `green-node-XX.local` from server | ✅ |
| **HTTP POST** | Confirm 201 response on `/node/{id}/sensor` | ✅ |
| **Photo Capture** | Trigger `/capture`, verify JPEG + sensor headers | ✅ |
| **Database Storage** | Query SQLite for latest readings per node | ✅ |
| **Dashboard Render** | Open dashboard, verify live cards + history charts | ✅ |
| **AI Analysis** | Send sensor data + image to Gemini, verify structured JSON | ✅ |
| **Translation** | Sarvam AI translate endpoint with chunked text | ✅ |
| **TTS Playback** | Voice playback of translated advisory | ✅ |

---

## Tools Used

| Tool | Purpose |
|------|---------|
| Arduino IDE | Firmware upload to ESP32-C3 and ESP32-CAM |
| FastAPI + Uvicorn | Backend server |
| SQLite | Sensor data persistence |
| Browser DevTools | Dashboard debugging and network inspection |
| KiCad 9.0.3 | PCB schematic design |
| Fusion 360 / CAD | 3D enclosure modelling |
