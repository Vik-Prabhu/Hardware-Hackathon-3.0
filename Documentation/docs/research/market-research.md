# Green Node

### Precision Plant Intelligence — Anywhere Plants Grow

---

## The Problem

Plant maintenance today runs on **fixed schedules** — not actual plant need. Workers water and inspect on a calendar, not on data. Whether it is a highway median, a nursery, or a university campus, the result is always the same:

- Plants die during heat waves while contractors are "on schedule"
- Workers wander inefficiently through large green spaces with no priority system — wasting hours checking healthy plants while stressed ones go unnoticed
- Overwatering during monsoon causes root rot and water wastage
- Disease spreads undetected before anyone notices
- Dead plants mean financial loss, safety hazards, and reputational damage

**Green Node** puts an intelligent sensor node wherever plants grow. Each node watches, measures, and reports — so maintenance happens when and where it is actually needed.

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

Each node carries a carefully selected sensor stack:

- **ESP32-C3** — The brain. Handles all logic, WiFi, BLE, and live weather API calls
- **ESP32-CAM** — The eyes. Daily snapshots for visual leaf health analysis
- **DHT11 × 2** — Temperature and humidity at both canopy and soil level
- **LDR** — Light intensity, shading detection, and day/night cycle tracking
- **Soil Moisture Sensor** — The primary watering trigger
- **Green and Red LEDs** — Instant on-site visual status for any worker passing by
- **esp-serial-flasher** — Remote firmware updates without physically touching the node

---

## What Green Node Can Do

### Smart Irrigation Decisions

Soil moisture data is combined with live weather forecast from OpenWeatherMap. If the soil is dry and no rain is forecast within 6 hours, the red LED fires and an alert goes to the maintenance team. If rain is incoming, the alert is suppressed. No more watering before a storm. No more dry plants the day after a sunny week.

### Route Optimization for Maintenance Workers

This is one of the most overlooked problems in plant maintenance. Workers in large nurseries or long highway stretches **wander** — they check plants in the order they encounter them, not in the order of urgency. Green Node changes this.

Nodes continuously rank plant health across the entire deployment. When a worker starts their shift, the dashboard generates a **prioritized inspection route** — check plant 14 first (soil critically dry), then plant 7 (temperature stress flagged), skip plants 1 through 6 (all healthy). What used to take 3 hours of walking is compressed into a focused 45-minute route. That is a 75% reduction in daily inspection time — without hiring more staff or buying more equipment.

### Visual Leaf Health

The ESP32-CAM captures daily images of the plant canopy. Basic colour analysis using HSV thresholds detects:

- Yellowing → nitrogen deficiency or overwatering
- Browning → heat stress or root rot
- Dark patches → early fungal infection

No cloud ML required at MVP. Rule-based detection works reliably and runs on the node itself.

### Microclimate Logging

Two DHT11 sensors — one at ground level, one at canopy height — reveal the actual thermal stress a plant experiences versus ambient air temperature. This localised data is far more accurate than any regional weather station and has genuine research value for urban heat island studies.

### Light Deprivation Detection

The LDR tracks daily light exposure. Plants under flyovers, shade nets, or building shadows that receive insufficient light are flagged before they fail — not after.

### Remote Firmware Updates

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

**Extremely Low Hardware Cost**
The full node comes in under ₹2,400. This is deployable at scale without external capital or investor backing.

**Weather API Is a Real Moat**
No competitor in municipal or nursery IoT is combining live on-ground sensor data with forecast APIs for irrigation decisions. This is genuinely differentiated and immediately implementable.

**Route Optimization Solves a Human Problem**
Most IoT products solve a plant problem. The prioritized walk route solves a *worker* problem — and that is a far stronger sales argument to any facility manager or nursery owner.

**General Purpose by Design**
One hardware unit works for highways, nurseries, campuses, and rooftops. No vertical-specific engineering needed to enter a new market.

**Visual Health Monitoring at ₹350**
Leaf colour analysis via ESP32-CAM is something no existing municipal IoT product does at this price point.

---

### Weaknesses

**DHT11 Long-Term Accuracy**
Plus or minus 2°C and plus or minus 5% RH, with degradation in sustained high-humidity environments. Acceptable for prototyping and pilots. Production units should upgrade to DHT22 or SHT31.

**Single Soil Sensor Per Node**
One measurement point may miss moisture variability across wider planting strips. Larger beds may need two sensors per node in production.

**No Standalone Power Out of the Box**
Highway medians and remote gardens have no power infrastructure. A solar panel and battery add approximately ₹1,100 per node and are essential for any real-world deployment.

**ESP-NOW Range Limitation**
Without LoRa, node-to-node communication caps at around 200 metres. Long highway corridors will need 4G/GPRS relay modules or WiFi access point repeaters at intervals.

---

### Opportunities

**NHAI Smart Highway Tenders**
Active government procurement for IoT infrastructure monitoring exists on national highways. Highway horticulture is an adjacent category with no dedicated startup targeting it.

**Nursery Export Compliance**
Indian nurseries exporting to EU or US markets must provide documented, traceable plant health records. Green Node automated logs can serve as phytosanitary compliance evidence, unlocking premium export pricing.

**State PWD Contracts**
Every state Public Works Department maintains roadside plantations. Karnataka, Andhra Pradesh, and Maharashtra have active urban greening budgets and green infrastructure mandates.

**CSR and ESG Funding**
Highway-adjacent companies (logistics, fuel, hospitality) have CSR mandates around green infrastructure. A sponsored-node model lets them fund a stretch of highway greenery in exchange for visibility.

**Research Data Licensing**
Corridor microclimate data — temperature, humidity, light along a 10km stretch — has direct value for ISRO vegetation index ground-truthing, climate research, and urban planning consultancies.

---

### Threats

**Municipal Procurement Timelines**
NHAI and PWD contracts take 12 to 18 months to close. Private sector entry points — commercial nurseries, campus facilities teams — are faster routes to initial paid pilots.

**Vandalism in Public Spaces**
Highway and park nodes are unguarded. IP65 enclosures and tamper-evident mounting are non-negotiable. The ESP32-CAM can also log images of any physical interference with the node.

**Connectivity Dead Zones**
Remote highway stretches have patchy 4G coverage. Weather API calls need a store-and-forward fallback — data caches on the C3's flash memory and uploads when signal returns.

**Monsoon Hardware Stress**
Indian monsoons bring 85 to 95 percent relative humidity for four months. DHT11 and LDR components need conformal coating applied before first deployment. This must be factored into the BOM from day one.

---

## Revenue Streams

**Pilot Contract**
₹2 to 5 lakh for a 5 km highway stretch or 1-acre nursery pilot covering 10 nodes. Includes hardware, installation, and six months of dashboard access.

**Per-Node SaaS**
₹500 to 800 per node per month for dashboard access, alert management, and automated reports. Ten nodes generates ₹5,000 to 8,000 monthly recurring revenue.

**Water Savings Performance Contract**
Take 20% of proven water bill reduction. Aligns your incentive with the client's outcome.

**Compliance Report Generation**
Automated phytosanitary export documentation as a premium tier for nurseries targeting EU/US markets.

**Annual Maintenance Plans**
Calibration check-ups and node replacement service contracts for deployed sites.

---

## Cost Per Node

The full production bill of materials comes in at approximately **₹2,390 per node**:

- ESP32-C3 module — ₹220
- ESP32-CAM — ₹350
- DHT11 sensors × 2 — ₹60
- LDR — ₹10
- Soil moisture sensor — ₹80
- LEDs × 4 — ₹20
- IP65 weatherproof enclosure — ₹300
- PCB and connectors — ₹150
- Solar panel 5V / 1W — ₹900
- Li-ion battery and TP4056 charger — ₹200
- Miscellaneous — ₹100

At ₹500 per node per month SaaS pricing, the hardware cost per node is recovered in **under 5 months**.

---

## 90-Day MVP Roadmap

**Weeks 1 and 2 — Build and Validate Indoors**
Assemble a single node. Validate the DHT11, soil sensor, LDR, and weather API pipeline end-to-end. Test ESP32-CAM image capture and basic HSV leaf colour analysis.

**Weeks 3 and 4 — Outdoor Field Test**
Deploy in a college campus garden or home terrace. Validate solar power operation, IP65 enclosure performance, and OTA firmware update via esp-serial-flasher.

**Weeks 5 to 8 — Real Deployment and Data Collection**
Deploy 3 to 5 nodes on a real stretch — a nursery row, a campus median, or a garden. Build a basic web dashboard showing node health, soil percentage, temperature, and active alerts. Collect 30 continuous days of data.

**Weeks 9 to 12 — First Sales Conversations**
Approach a nursery owner, campus facilities manager, or state highway horticulture contractor. Present real data. Document water savings against their previous schedule-based baseline. That proof is your sales pitch.

---

## Competitive Position

**vs. Fasal**
Farm-specific IoT at 10× the hardware cost. Green Node is general purpose and deployable by a single engineer.

**vs. CropIn**
Software-only platform with no on-ground hardware. Green Node provides actual sensor truth, not estimations.

**vs. Generic DHT11 Kits**
Commodity sensors with no intelligence layer, no weather integration, no camera, and no route optimization. Green Node adds the decision-making layer on top.

**vs. Manual Contractors**
Schedule-based, unaccountable, and expensive at scale. Green Node creates a data trail that makes performance measurable and disputes impossible to ignore.

---

## Conclusion

Green Node is a general-purpose plant intelligence platform that works wherever plants need monitoring. The hardware is affordable, proven, and already available. The differentiation is the intelligence layer on top — weather-adjusted irrigation decisions, visual health monitoring, and prioritized worker routes that turn scattered data into clear daily actions.

Start with one node. Get 30 days of real data. That data is your sales pitch.

---

*Green Node — Plant Intelligence for Every Green Space.*