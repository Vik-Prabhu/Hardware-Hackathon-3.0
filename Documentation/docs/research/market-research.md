# Green Node

### Precision Plant Intelligence — Anywhere Plants Grow

---

<div style="display: flex; gap: 2rem; margin: 2rem 0; flex-wrap: wrap;">
<div style="flex: 1; min-width: 150px; text-align: center;">
<strong style="font-size: 2rem; color: var(--vp-c-brand);">₹2,390</strong><br/>
<small>Full node hardware cost — deployable at scale without external capital</small>
</div>
<div style="flex: 1; min-width: 150px; text-align: center;">
<strong style="font-size: 2rem; color: var(--vp-c-brand);">75%</strong><br/>
<small>Reduction in daily inspection time through prioritised worker routes</small>
</div>
<div style="flex: 1; min-width: 150px; text-align: center;">
<strong style="font-size: 2rem; color: var(--vp-c-brand);">5 mo.</strong><br/>
<small>Hardware payback period at ₹500/node/month SaaS pricing</small>
</div>
</div>

---

## The Problem

Plant maintenance today runs on **fixed schedules** — not actual plant need. Workers water and inspect on a calendar, not on data. Whether it is a highway median, a nursery, or a university campus, the result is always the same:

- 🌡️ **Heat wave blindness** — Plants die during heat waves while contractors are "on schedule" — no real-time data triggers action
- 🚶 **Inefficient wandering** — Workers check plants in order of encounter, not urgency — wasting hours on healthy plants while stressed ones go unnoticed
- 💧 **Monsoon overwatering** — Irrigation runs on schedule during monsoon, causing root rot and water wastage with no feedback loop
- 🍄 **Disease spreads undetected** — Fungal infections and leaf stress are invisible until they've already caused irreversible damage

> *"Plants don't fail on schedule — so why does maintenance run on one?"*
>
> Whether it's a highway median, nursery, or university campus, the result is always the same: financial loss, safety hazards, and reputational damage from dead plants that data could have saved.
>
> Green Node puts an intelligent sensor node wherever plants grow. The hardware is under ₹2,400. The intelligence runs on the node itself.

---

## Where Green Node Works

Green Node is a general-purpose platform. The same hardware works across every deployment:

- **Highway Medians** — Replace tanker trips on NHAI / PWD greenery with data-driven irrigation
- **Commercial Nurseries** — Protect high-value plant stock and accrued labor investment
- **Urban Parks and Gardens** — Create accountability for municipal contractor maintenance
- **Campuses** — Schools, colleges, and hospitals with low staff overhead
- **Rooftop and Terrace Gardens** — Remote monitoring without on-site gardeners
- **Greenhouses** — Precision humidity and soil control for controlled environments

---

## What Green Node Measures

Each node carries a carefully selected sensor stack — no bloat, no missing pieces. Every component earns its place on the BOM.

| Sensor | Role |
|---|---|
| 🧠 **ESP32-C3 — The Brain** | Handles all logic, WiFi, BLE, and live OpenWeatherMap API calls. The intelligence hub of every node. |
| 📷 **ESP32-CAM — The Eyes** | Daily snapshots for visual leaf health analysis. HSV colour thresholds detect yellowing, browning, and dark patches on-device. |
| 🌡️ **DHT11 × 2 — Dual Temp** | Temperature and humidity at both canopy and soil level. Reveals actual thermal stress versus ambient air temperature. |
| ☀️ **LDR — Light Tracking** | Light intensity, shading detection, and day/night cycle. Flags plants under flyovers or shade nets before they fail. |
| 💧 **Soil Moisture Sensor** | The primary watering trigger. Combined with forecast data to eliminate pre-storm irrigation and catch post-sunny-week dryness. |
| 📡 **OTA Firmware Updates** | esp-serial-flasher integration lets you push updates over WiFi to any deployed node. No technician visits required. |

---

## What Green Node Can Do

### 01 — Smart Irrigation Decisions

Soil moisture data is combined with live weather forecasts from OpenWeatherMap. If soil is dry and no rain is forecast within 6 hours, an alert fires. If rain is incoming, the alert is suppressed. No more watering before a storm. No more dry plants the day after a sunny week.

> 🌧️ Rain-aware · 📊 Live API · 🔔 Smart Alerts

### 02 — Route Optimisation for Workers

This is one of the most overlooked problems in plant maintenance. Workers in large nurseries or long highway stretches **wander** — they check plants in the order they encounter them, not in the order of urgency. Green Node changes this.

Nodes continuously rank plant health across the entire deployment. When a worker starts their shift, the dashboard generates a **prioritised inspection route** — check plant 14 first (soil critically dry), then plant 7 (temperature stress flagged), skip plants 1 through 6 (all healthy). What used to take 3 hours of walking is compressed into a focused 45-minute route. That is a **75% reduction** in daily inspection time — without hiring more staff or buying more equipment.

> ⏱️ 75% time saved · 🗺️ Priority routing · 📋 Shift dashboard

### 03 — Visual Leaf Health Analysis

The ESP32-CAM captures daily canopy images. Rule-based HSV threshold detection — no cloud ML required — identifies issues on the node itself:

- 🟡 **Yellowing** → Nitrogen deficiency or overwatering
- 🟤 **Browning** → Heat stress or root rot
- ⚫ **Dark patches** → Early fungal infection

No cloud ML required at MVP. Rule-based detection works reliably and runs on the node itself.

### 04 — Microclimate Logging

Two DHT11 sensors — one at ground level, one at canopy height — reveal the actual thermal stress a plant experiences versus ambient air temperature. This localised data is far more accurate than any regional weather station and has genuine research value for urban heat island studies.

### 05 — Light Deprivation Detection

The LDR tracks daily light exposure. Plants under flyovers, shade nets, or building shadows that receive insufficient light are flagged before they fail — not after.

### 06 — Remote Firmware Updates

Deployed nodes in a highway or remote garden cannot always be physically accessed. The esp-serial-flasher integration lets you push firmware updates over WiFi to any node in the field. No technician visits required.

---

## What Green Node Cannot Do (Being Honest)

Green Node is a focused, low-cost system. Here is what it does not attempt:

- **Ethylene or CO₂ sensing** — Requires additional sensors not in the current build
- **Long-range mesh beyond 200m** — No LoRa module; ESP-NOW caps at ~200m outdoors
- **Continuous video streaming** — The CAM module captures snapshots, not live video
- **Heavy on-device ML** — The C3 has 400KB RAM; complex models need cloud inference

---

## SWOT Analysis

### Strengths

- **Extremely Low Hardware Cost** — Full node under ₹2,400. Deployable at scale without investor backing.
- **Weather API Is a Real Moat** — No competitor combines on-ground sensor data with forecast APIs for irrigation decisions. Genuinely differentiated and immediately implementable.
- **Route Optimisation Solves a Worker Problem** — Most IoT products solve a plant problem. Prioritised walk routes solve a *worker* problem — a far stronger sales argument to any facility manager or nursery owner.
- **General Purpose by Design** — One hardware unit works across highways, nurseries, campuses, and rooftops. No vertical-specific engineering needed.
- **Visual Health Monitoring at ₹350** — Leaf colour analysis via ESP32-CAM is something no existing municipal IoT product does at this price point.

### Weaknesses

- **DHT11 Long-Term Accuracy** — ±2°C / ±5% RH accuracy degrades in sustained high-humidity environments. Upgrade to DHT22 / SHT31 for production.
- **Single Soil Sensor Per Node** — One measurement point may miss variability across wider planting strips. Larger beds may need two sensors per node.
- **No Standalone Power Out of the Box** — Solar panel + battery add ~₹1,100 per node. Essential for any off-grid deployment.
- **ESP-NOW Range Limitation** — Caps at ~200m. Long highway corridors will need 4G relay modules or WiFi access point repeaters.

### Opportunities

- **NHAI Smart Highway Tenders** — Active government IoT procurement. No dedicated startup targeting highway horticulture.
- **Nursery Export Compliance** — EU/US phytosanitary documentation unlocks premium export pricing. Green Node automated logs serve as compliance evidence.
- **State PWD Contracts** — Karnataka, AP, Maharashtra have active urban greening budgets and green infrastructure mandates.
- **CSR/ESG Funding** — Highway-adjacent companies can fund a stretch of highway greenery in exchange for visibility through a sponsored-node model.
- **Research Data Licensing** — Microclimate corridor data has direct value for ISRO vegetation index ground-truthing, climate research, and urban planning consultancies.

### Threats

- **Municipal Procurement Timelines** — NHAI/PWD contracts take 12–18 months. Private nurseries are faster entry points.
- **Vandalism in Public Spaces** — IP65 enclosures + tamper-evident mounting are non-negotiable. ESP32-CAM can also log images of physical interference.
- **Connectivity Dead Zones** — Store-and-forward fallback essential. Data caches on C3's flash memory and uploads when signal returns.
- **Monsoon Hardware Stress** — Indian monsoons bring 85–95% RH for 4 months. Conformal coating required from day one.

---

## Revenue Streams

### Pilot Deployment — ₹2–5 Lakh

5 km highway stretch or 1-acre nursery pilot — 10 nodes, hardware, installation, and 6 months of dashboard access.

### Per-Node SaaS — ₹500–800/node/month

Dashboard access, alert management, and automated reports. 10 nodes generates ₹5,000–8,000 monthly recurring revenue.

### Compliance Reports — Premium Tier

Automated phytosanitary export documentation for nurseries targeting EU/US markets.

### Water Savings Performance Contract

Take 20% of proven water bill reduction. Aligns your incentive with the client's outcome.

### Annual Maintenance Plans

Calibration check-ups and node replacement service contracts for deployed sites.

---

## Cost Per Node

Full production BOM — under ₹2,400. Hardware cost recovered in under 5 months at ₹500/node SaaS pricing.

| Component | Role | Cost (₹) |
|---|---|---:|
| ESP32-C3 | Main MCU — WiFi, BLE, logic, API | 320 |
| ESP32-CAM | Daily image capture & leaf analysis | 350 |
| DHT11 × 2 | Temp + humidity, dual-level | 120 |
| Soil Moisture Sensor | Primary irrigation trigger | 80 |
| LDR | Light intensity + shading detection | 20 |
| Enclosure + PCB + wiring | IP65 housing, connectors, cables | 500 |
| Power (5V supply) | Regulated power delivery | 200 |
| Misc (LEDs, resistors, caps) | Supporting components | 100 |
| Solar + Battery (optional) | Off-grid deployment | +1,100 |
| **Total (grid-powered)** | | **₹1,690** |
| **Total (solar-ready)** | | **₹2,790** |

---

## 90-Day MVP Roadmap

### 🔧 Weeks 1–2 — Build & Validate Indoors

Assemble a single node. Validate DHT11, soil sensor, LDR, and weather API pipeline end-to-end. Test ESP32-CAM image capture and basic HSV leaf colour analysis.

### 🌿 Weeks 3–4 — Outdoor Field Test

Deploy on a campus garden or home terrace. Validate solar power operation, IP65 enclosure performance, and OTA firmware update via esp-serial-flasher.

### 📊 Weeks 5–8 — Real Deployment + Data Collection

Deploy 3–5 nodes on a real stretch — a nursery row, a campus median, or a garden. Build a basic web dashboard showing node health, soil percentage, temperature, and active alerts. Collect 30 continuous days of live sensor data.

### 💼 Weeks 9–12 — First Sales Conversations

Approach nursery owners, campus facilities managers, or highway horticulture contractors. Present real data. Document water savings against their previous schedule-based baseline. That 30-day proof is your sales pitch.

---

## Competitive Position

| Product | Approach | Weakness | Green Node Edge |
|---|---|---|---|
| **Fasal** | Farm-specific IoT | 10× the hardware cost, vertical-specific | General purpose · ₹2,400 |
| **CropIn** | Software-only platform | No on-ground sensors — estimations only | Actual sensor truth |
| **Manual Contractors** | Schedule-based inspection | Unaccountable, inefficient, expensive at scale | Data trail + route optimisation |
| **Green Node** | On-ground IoT + weather API + visual AI | Early stage — ESP-NOW range limitation | **Only system combining all three** |

---

## Conclusion

Green Node is a general-purpose plant intelligence platform that works wherever plants need monitoring. The hardware is affordable, proven, and already available. The differentiation is the intelligence layer on top — weather-adjusted irrigation decisions, visual health monitoring, and prioritised worker routes that turn scattered data into clear daily actions.

Start with one node. Get 30 days of real data. That data is your sales pitch.

---

*Green Node — Plant Intelligence for Every Green Space.*