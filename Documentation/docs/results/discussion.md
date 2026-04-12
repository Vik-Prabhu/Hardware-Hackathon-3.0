# Discussion & Results

This section presents the outcomes of the Green Node deployment, covering live sensor performance, AI advisory quality, and overall system reliability.

---

## Live Dashboard

The web dashboard renders real-time sensor data for all connected nodes, with animated charts and scrollable history.

<!-- 📸 TODO: Screenshot of the full dashboard with both node cards visible -->
<!-- ![Dashboard Overview](/results/dashboard-overview.png) -->

### Key Observations
- Sensor cards update in real-time as new readings arrive
- History view shows the last 20 readings per node, newest first
- Responsive layout works across desktop and mobile viewports

---

## Sensor Data Quality

### Temperature & Humidity
<!-- 📸 TODO: Screenshot of the temperature/humidity chart from node history -->
<!-- ![Sensor History](/results/sensor-history.png) -->

| Metric | N-01 (DHT22) | N-02 (DHT11) |
|--------|:------------:|:------------:|
| **Temp Range Observed** | 23.5 °C to 44.0 °C | 34.2 °C to 35.2 °C |
| **Humidity Range** | 48.0 % to 80.5 % | 46.0 % to 50.0 % |
| **Readings Collected** | 2,352 readings | 341 readings |
| **Anomalies** | 58 readings at 0.0 °C (sensor init) | None |

::: info Data Note
N-01 logged 2,032 readings with humidity = 0.0 — these are from sessions **before** the humidity feature was added to the firmware. Effective humidity data begins after the DHT22 integration update.
:::

### Soil Moisture
<!-- 📸 TODO: Screenshot of soil moisture graph showing variation over time -->
<!-- ![Soil Moisture](/results/soil-moisture.png) -->

- N-01 moisture ranged from **0 %** to **100 %**, covering full dry-to-saturated states
- N-02 moisture ranged from **0 %** to **37 %** — consistent with indoor pot conditions
- Adaptive interval kicked in correctly when moisture dropped below 25%

### Light Levels
- N-01 LDR readings ranged from **0** to **94,918 lux**
- N-02 LDR readings ranged from **0** to **100,000 lux** (sensor saturation)
- Indoor lighting conditions stayed within expected bounds

---

## Camera Captures

The ESP32-CAM successfully captured **612 plant images** across testing sessions, triggered on demand by the server.

<!-- 📸 TODO: Grid of 3–4 best plant photos from server/photos/N-01/ -->
<!-- ![Plant Capture 1](/results/plant-capture-1.jpg) -->
<!-- ![Plant Capture 2](/results/plant-capture-2.jpg) -->
<!-- ![Plant Capture 3](/results/plant-capture-3.jpg) -->

### Image Quality
| Parameter | Value |
|-----------|-------|
| **Resolution** | 800×600 (SVGA) with PSRAM |
| **Format** | JPEG, quality 12 |
| **Avg File Size** | ~20–30 KB |
| **Capture Latency** | ~2–4 seconds end-to-end |

---

## AI Health Advisory

Sensor data and plant images were forwarded to the **Gemini AI** microservice, which returned structured JSON advisories.

<!-- 📸 TODO: Screenshot of the AI advisory panel on the dashboard (expanded view showing problems, solutions, predictions) -->
<!-- ![AI Advisory Panel](/results/ai-advisory.png) -->

### Advisory Structure
The AI returns a consistent JSON format:
```json
{
  "summary": "Overall plant health assessment",
  "overall_severity": "warning",
  "problems": [
    { "issue": "...", "details": "...", "severity": "warning" }
  ],
  "solutions": [
    { "action": "...", "details": "...", "urgency": "within_24h" }
  ],
  "predictions": {
    "short_term": "...",
    "long_term": "..."
  }
}
```

### Advisory Accuracy
- **99 total advisories** generated across all nodes (N-01: 38, N-02: 15, simulated N-03–N-05: 46)
- AI correctly identified environmental conditions based on sensor thresholds
- Image-based analysis provided visual leaf health observations when photos were included
- Markdown code-fence wrapping in AI responses was handled by server-side cleanup

---

## Daily Action Plan

All node advisories are aggregated into a single **Daily Action Plan** — a consolidated paragraph report surfaced on the dashboard.

<!-- 📸 TODO: Screenshot of the Daily Action Plan section on the dashboard -->
<!-- ![Daily Action Plan](/results/daily-plan.png) -->

### Features
- Automatic severity triage across all nodes (critical → warning → healthy)
- Solutions sorted by urgency: `immediate` → `within_24h` → `monitor`
- Background scheduler runs analysis every 5 minutes via APScheduler

---

## Multilingual Support

The Sarvam AI integration enables **translation and voice playback** of the daily plan in multiple Indian languages.

<!-- 📸 TODO: Screenshot of the translation UI with language tabs and audio player -->
<!-- ![Multilingual UI](/results/multilingual.png) -->

### Supported Languages
| Language | Code | Translation | Voice |
|----------|------|:-----------:|:-----:|
| Hindi | `hi-IN` | ✅ | ✅ |
| Tamil | `ta-IN` | ✅ | ✅ |
| Kannada | `kn-IN` | ✅ | ✅ |
| Telugu | `te-IN` | ✅ | ✅ |
| Bengali | `bn-IN` | ✅ | ✅ |

### Implementation
- Text chunked to ≤1900 characters per Sarvam API limit
- Audio returned as base64 WAV, played inline on the dashboard

---

## System Reliability

| Metric | Result |
|--------|--------|
| **Total Readings Logged** | **10,165** across 5 nodes (2 physical + 3 simulated) |
| **Node Uptime** | Stable across multi-hour sessions |
| **WiFi Reconnection** | Auto-reconnects on dropout (10 s timeout) |
| **Server Registration** | Nodes re-register every 10 s if disconnected |
| **Data Loss** | Zero dropped readings during testing |
| **Photos Captured** | **612** plant images from N-01 (ESP32-CAM) |
| **AI Advisories** | **99** structured advisories generated |
| **AI Pipeline** | 300 s timeout handles long inference gracefully |

---

## Known Limitations

- **ESP32-CAM ADC conflict:** GPIO 32–39 used by camera — soil/light sensors need external ADC or separate MCU
- **Battery monitoring:** Currently hardcoded (3.7 V / 100%) — needs real ADC divider circuit
- **Outdoor weatherproofing:** Current 3D enclosure is PLA — would need PETG or ASA for UV/rain resistance
- **AI latency:** Gemini inference can take 10–30 s per node, making real-time alerts impractical at scale

---

## Conclusion

The Green Node system successfully demonstrated a **full end-to-end pipeline** — from embedded sensor nodes through a centralized backend to AI-powered, multilingual health advisories. The modular hardware architecture enables easy scaling by adding new nodes with unique IDs, and the software stack is designed for rapid iteration.

<!-- 📸 TODO: Final hero shot — the complete assembled system with nodes, plants, and dashboard on screen -->
<!-- ![Complete System](/results/final-hero.jpg) -->
