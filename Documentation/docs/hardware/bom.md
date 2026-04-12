# Bill of Materials

A complete list of components required to build the **Green Node** plantation monitoring system. The BOM is organized by node type and shared infrastructure.

---

## Node N-01 — Camera + Environment Node

This node uses an **ESP32-CAM (AI-Thinker)** as its MCU. It captures plant images for AI-powered health analysis and reads ambient temperature & humidity via a DHT22 sensor.

| # | Component | Specification | Qty | Purpose |
|---|-----------|---------------|:---:|---------|
| 1 | ESP32-CAM (AI-Thinker) | ESP32-S, OV2640 camera, 4 MB PSRAM | 1 | MCU + image capture |
| 2 | OV2640 Camera Module | 2 MP, SVGA (800×600) / VGA (640×480) | 1 | Plant health imaging *(included with ESP32-CAM board)* |
| 3 | DHT22 (AM2302) | Digital temp & humidity sensor, ±0.5 °C / ±2 % RH | 1 | Ambient temperature & humidity on GPIO 13 |
| 4 | FTDI / USB-TTL Adapter | 3.3 V logic, CP2102 or CH340 | 1 | Programming (ESP32-CAM has no on-board USB) |
| 5 | 5 V Power Supply / USB Cable | 5 V ≥ 500 mA | 1 | Board power |
| 6 | 10 kΩ Resistor | ¼ W, through-hole | 1 | DHT22 pull-up on data line |
| 7 | Jumper Wires | Male-to-Female, assorted | ~6 | Signal wiring |
| 8 | Breadboard / Perfboard | Half-size or full-size | 1 | Prototyping base |

> **Note:** On the AI-Thinker ESP32-CAM, GPIO 32–39 are consumed by the camera data bus. Analog sensors (soil moisture, LDR) require an external I²C ADC (e.g. ADS1115) or a separate MCU if added to this node.

---

## Node N-02 — GlyphC3 Sensor Node

This node uses an **ESP32-C3** (RISC-V) as its MCU. It continuously reads soil moisture, ambient light, temperature, and humidity, then transmits readings over Wi-Fi to the backend server.

| # | Component | Specification | Qty | Purpose |
|---|-----------|---------------|:---:|---------|
| 1 | ESP32-C3 Dev Board | RISC-V single-core, Wi-Fi, 12-bit ADC | 1 | MCU + wireless comms |
| 2 | DHT11 | Digital temp & humidity sensor, ±2 °C / ±5 % RH | 1 | Temperature & humidity on GPIO 9 |
| 3 | Capacitive Soil Moisture Sensor v1.2 | Analog output, corrosion-resistant | 1 | Soil moisture on GPIO 3 (ADC) |
| 4 | LDR (Light-Dependent Resistor) | 5 mm, CdS photoresistor | 1 | Ambient light level on GPIO 2 (ADC) |
| 5 | 10 kΩ Resistor | ¼ W, through-hole | 2 | LDR voltage divider + DHT11 pull-up |
| 6 | USB-C Cable | Data + power | 1 | Programming & power supply |
| 7 | Jumper Wires | Male-to-Female, assorted | ~8 | Signal wiring |
| 8 | Breadboard / Perfboard | Half-size | 1 | Prototyping base |

---

## 3D-Printed Enclosure

Custom housing designed to protect the electronics while exposing sensors to the environment. See the [Mechanical Design](/hardware/mechanical) page for the full CAD render.

| # | Component | Specification | Qty | Purpose |
|---|-----------|---------------|:---:|---------|
| 1 | 3D-Printed Enclosure Body | PLA / PETG, branded "GREEN NODE" | 1 per node | Weatherproof housing |
| 2 | Side Port Cover | PLA / PETG, snap-fit | 1 per node | DHT sensor access slot |
| 3 | M3 × 8 mm Screws | Stainless steel, Phillips | 4 per node | Enclosure assembly |

---

## Shared Infrastructure / Server

The backend runs on a local machine (e.g. laptop) and hosts the FastAPI server, SQLite database, dashboard, and AI analysis pipeline.

| # | Component | Specification | Qty | Purpose |
|---|-----------|---------------|:---:|---------|
| 1 | Server Machine | Any laptop/PC running Python 3.10+, Wi-Fi enabled | 1 | FastAPI backend + dashboard host |
| 2 | Wi-Fi Router / Hotspot | 2.4 GHz, WPA2 | 1 | Local network for node–server comms |
| 3 | AI Processing Server *(optional)* | GPU-enabled machine with Gemini API access | 1 | Runs the plant health advisory model |

---

## Summary & Cost Estimate

| Assembly | Key Components | Est. Cost (₹) |
|----------|---------------|---------------:|
| **N-01** — Camera Node | ESP32-CAM, DHT22, FTDI adapter | ~₹750 |
| **N-02** — Sensor Node | ESP32-C3, DHT11, Soil Moisture, LDR | ~₹550 |
| **Enclosure** (per node) | 3D print filament + fasteners | ~₹100 |
| **Infrastructure** | Wi-Fi router, server laptop | *Existing* |
| | **Total (2-node system)** | **~₹1,500** |

::: tip Scalability
Additional sensor nodes can be added by flashing the GlyphC3 firmware with a unique `NODE_ID` (e.g. `N-03`, `N-04`, …). Each new node costs approximately **₹550–₹650** including the enclosure.
:::
