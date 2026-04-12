# Electronics & Schematics

The Green Node PCB was designed in **KiCad 9.0.3** as a single-sheet schematic (`hh3.0.kicad_sch`) housing two independent sensor modules on one board. The design prioritises minimal component count, through-hole assembly, and modular sensor connectors.

## Full Schematic

![Green Node PCB Schematic — Rev v1](/schematic.jpeg)

---

## ESP C3 Module (Node N-02)

The upper section of the schematic is built around **U1 — GLYPH-C3**, an ESP32-C3 RISC-V module. It handles continuous soil, light, temperature, and humidity monitoring.

### Pin Assignments

| GLYPH-C3 Pin | Net | Connected To |
|:---:|---|---|
| D8 | `dB` | Status LED D3 via R5 (current-limiting) |
| D9 (dht_data_c3) | `dht_data_c3` | **J5** — DHT11 sensor, pin 2 (data) |
| A0 (soil) | `soil` | **J6** — Capacitive Soil Moisture Sensor, pin 1 (analog out) |
| A1 (ldr) | `ldr` | **R1 (LDR03)** — LDR voltage divider mid-point |
| D+ / D− | USB | On-board USB-C for programming |
| 3V3 | `+3.3V` | Regulated 3.3 V rail |
| GND | `GND` | Common ground |
| BAT | — | Battery input (unused in current revision) |

### Sensor Circuits

#### DHT11 — Temperature & Humidity (J5)
- **Connector:** 3-pin header (J5)
  - Pin 1 → `+3.3V`
  - Pin 2 → `dht_data_c3` (GPIO 9)
  - Pin 3 → `GND`
- **Pull-up:** R3 (10 kΩ) from data line to VCC

#### LDR — Ambient Light (R1)
- **R1 (LDR03)** forms a voltage divider with **R2** (10 kΩ fixed) between `+3.3V` and `GND`
- Mid-point tap connects to **A1** (GPIO 2) for analog read
- ADC maps the 0–3.3 V range to a 12-bit value (0–4095)

#### Capacitive Soil Moisture Sensor (J6)
- **Connector:** 4-pin header (J6)
  - Pin 1 → analog signal → `soil` (GPIO 3)
  - Pin 2 → `GND`
  - Pin 3 → `GND`
  - Pin 4 → `+3.5V` (sensor power)
- Corrosion-resistant capacitive probe; no direct soil contact on electrodes

#### Status LEDs (D1, D3)
- **D1** and **D3** are indicator LEDs driven through current-limiting resistors **R3** and **R5**
- Connected to GPIO `dB` for visual status feedback

### Power
- **powerjump1** — 2-pin power header providing `VCC` and `GND` from external supply
- **Jumper switch** at the top of the sheet controls main power to the C3 module
- The on-board LDO regulates input down to `+3.3V` for the MCU and sensors

---

## CAM Module (Node N-01)

The lower section is built around **U2 — ESP32-CAM** (AI-Thinker). It captures plant images on demand and reads ambient temperature via a DHT22 sensor.

### Pin Assignments

| ESP32-CAM Pin | Net | Connected To |
|:---:|---|---|
| 5V | `+5V` | External power input |
| GND | `GND1` | Common ground |
| 3.3V | `+3V0` | Regulated 3.3 V output |
| GPIO16 | `dht_data` | **J7** — DHT22 sensor, pin 2 (data) |
| GPIO0 | — | Boot mode select (active-low for flash) |
| U0R / U0T | UART | Serial programming via FTDI adapter |
| GPIO12–15, GPIO2, GPIO4 | — | Directly to camera data bus (active only on high-density header internally to the ESP32-CAM) |

### Sensor Circuits

#### DHT22 — Temperature & Humidity (J7)
- **Connector:** 3-pin header (J7)
  - Pin 1 → `GND1`
  - Pin 2 → `dht_data` (GPIO 16 → routed to GPIO 13 in firmware via internal mapping)
  - Pin 3 → `+3V0`
- **Pull-up:** R4 (10 kΩ) from data line to `+3V0`

#### Status LED (D2)
- Single indicator LED tied to `+3V0` through a current-limiting resistor
- Provides visual power-on feedback

### Power
- **powerjump2** — 2-pin Conn_01x02 header providing `+BATT` and `GND` from an external source
- The ESP32-CAM's on-board AMS1117 regulates 5 V input down to 3.3 V for the MCU and camera

::: warning Camera Pin Conflict
On the AI-Thinker ESP32-CAM, GPIOs 32–39 are **all consumed** by the OV2640 camera data bus. Analog sensors (soil moisture, LDR) cannot share this module and require an external I²C ADC (e.g. ADS1115) or a dedicated MCU like the GlyphC3 above.
:::

---

## Design Notes

| Parameter | Detail |
|-----------|--------|
| **EDA Tool** | KiCad E.D.A. 9.0.3 |
| **Schematic File** | `hh3.0.kicad_sch` |
| **Sheet** | 1/1 (single sheet) |
| **Board Size** | A4 |
| **Revision** | v1 |
| **Date** | 2026-04-12 |
| **Designed by** | Dikshith K B, Prahadeesh TN, Vikram Prabhu, Adwait Pattar |

### Key Design Decisions
- **Modular sensor connectors (J5, J6, J7):** All sensors use standard pin headers so they can be swapped, replaced, or upgraded without rework
- **Separate power domains:** The C3 module runs on 3.3 V while the CAM module accepts 5 V, each with independent power jumpers for isolation during debugging
- **Through-hole assembly:** All connectors and passives are through-hole for ease of hand-soldering during rapid prototyping
- **Status LEDs on each module:** D1/D3 on the C3 side and D2 on the CAM side provide immediate visual feedback without requiring serial monitor access
