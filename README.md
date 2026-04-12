# 🌿 Green Node - Hardware Hackathon 3.0

> **Engineering innovation through modular hardware and intelligent software.** <br/>
> A low-cost, scalable plant health monitoring system for farmers, nurseries, and smart cities.

Green Node is a fully integrated ecosystem designed to solve the largest problem in precision agriculture: actionable intelligence without overwhelming cost. By fusing cheap ESP32 microcontrollers with AI-based leaf pattern recognition, Green Node provides a robust "ground truth" to farmers, stopping diseases before they ruin crops. 

This project was built for the **Hardware Hackathon 3.0**. 

## 🏆 Key Features
* **Dual-Node Architecture:** Separates high-power AI vision (ESP32-CAM) from continuous low-power soil and climate indexing (ESP32-C3).
* **AI Disease Detection:** Automatically identifies early signs of afflictions like Late Blight, delivering hyper-specific instructions ("Inspect Row 4"). 
* **Dynamic Node Polling:** Sensor nodes change reporting frequency dynamically based on immediate urgency (e.g. accelerating ping rates from 30s to 5s during severe moisture drops).
* **Local Connectivity:** Fully bypasses expensive subscription LTE modules via accessible HTTP API routing over localized WiFi setups.
* **Tough Enclosures:** Custom CAD designed, bottom-pegged direct probing shells ensuring complete protection from monsoons (IP65).

---

## 🛠️ Tech Stack & Hardware Components
### Hardware
- **ESP32-C3 Dev Module** (Soil Continuous Monitor)
- **AI-Thinker ESP32-CAM** (Visual Capture Node)
- **Sensors:** DHT11/DHT22 (Ambience), Analog Resistive Moisture Probe, GL5528 LDR 
- **Power:** Grid-powered or Solar-Ready with built in Pull-Down circuitry 

### Software Ecosystem
- **MCU Firmware:** C++ (Arduino Framework)
- **Central Core:** Python (FastAPI/Flask-based)
- **Database:** SQLite
- **Dashboard:** Vitepress / Vue.js Web System 
- **Machine Learning:** Computer Vision pre-trained model for leaf analysis

---

## ⚙️ How It Works (The Workflow)
1. Both nodes power up, synchronize their UTC time with standard NTP servers, and register onto the local central Python Hub.
2. The **Soil Node** aggressively tracks metrics. It sends JSON payloads encompassing temperature, light, and soil moisture asynchronously. 
3. Upon server trigger or scheduled insight mapping, the Python Hub executes an HTTP `GET` to the **Camera Node**. 
4. The ESP32-CAM gathers high-res JPEGs while appending structural header-data containing immediate localized humidity.
5. The Hub evaluates the image through the AI model, records the event into an SQLite database, and populates the dashboard displaying critical actions the farmer must undertake immediately.

---

## 📁 Repository Structure

```text
├── Documentation/     # System architectural research, market-validation, and vitepress docs
├── firmware/          # C++ scripts for ESP32-C3 (Soil node) and ESP32-CAM
├── server/            # Python core engine, SQLite databases, and ML inference logic
└── README.md          # You are here!
```

---

## 🚀 Getting Started

**Central Server Setup**
```bash
cd server/
pip install -r requirements.txt
python main.py
```
*Ensure mDNS is active on your host machine to allow nodes to resolve `.local` endpoints.*

**Firmware Flashing**
- Utilize the `Arduino IDE` with the `esp32` board manager. 
- Required Libraries: `<DHT sensor library>`, `<ArduinoJson>`. 
- **ESP32-C3:** Native USB, flash normally. 
- **ESP32-CAM:** Requires FTDI FT232RL bridging. Ground `IO0` on boot to deploy. 

---

*This is an open repository built specifically for Hardware Hackathon 3.0. Please refer to `Documentation_Report.md` for our 13-point grading structure report.*
