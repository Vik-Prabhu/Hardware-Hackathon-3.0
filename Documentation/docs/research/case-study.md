---
title: From Prototype to Product
description: How we evaluated our plant health monitoring system against a real-world product framework
sidebar_position: 3
---

# From Prototype to Product

Building something that works in a hackathon and building something that works in a field
for a paying customer are very different problems. This section documents how we stress-tested
our system against a structured product thinking framework — to be honest about what we've
built, what it's missing, and how it could scale.

---

## The Three Lenses

We evaluated the system through three lenses before calling it a product.

**Customer Lens** — Does it actually help the user succeed?
Our target users are farmers and greenhouse managers who don't have time for manual
crop inspection. The system needs to surface the right information at the right time,
without requiring the user to interpret raw sensor data themselves.

**System Lens** — Does it work reliably in the real world?
Because the hardware lives outdoors in soil and weather, reliability is non-negotiable.
A sensor that fails after two rain cycles is worse than no sensor — it creates false confidence.
Every design decision around enclosures, waterproofing, and sensor selection traces back to this.

**Business Lens** — Will users pay for it, and keep paying?
An AI insight that replaces a single agronomist visit has clear economic value.
We need to make sure the system delivers that value consistently enough that it becomes
a recurring part of how a farm operates, not a one-time experiment.

---

## What We're Actually Selling (Kotler's Product Model)

Mapping the system to Kotler's three-layer model forced us to be precise about
where our differentiation actually sits.

**Core Benefit**
Plant survival, optimal yield, and early disease prevention. This is the need we're selling
against — not hardware, not software.

**Expected Product**
At minimum, buyers expect the physical nodes to reliably capture soil moisture, temperature,
humidity, and light data. This is table stakes — any competitor can offer this.

**Augmented Product — our actual differentiator**
The camera node feeding leaf images into a pre-trained AI disease detection model is what
moves us out of the commodity tier. Instead of telling a farmer "humidity is 78%",
we tell them "Node 3 has early signs of Late Blight — inspect row 4."
That specificity is what justifies a price premium and creates switching costs.

---

## Architecture for Scale

We designed the system in three tiers so it can grow without a full rebuild.

**Tier 1 — Smart Connected Product**
Individual sensor nodes and camera nodes gathering real-time soil and plant data.
This is what we've built and what the MVP ships.

**Tier 2 — Product System**
A centralised platform where data from multiple nodes and the AI model aggregate
into a single farm health dashboard. Multiple farms, multiple node clusters,
unified view — this is the next 6-month target.

**Tier 3 — System of Systems (future)**
Integration with external data sources: weather APIs, automated irrigation controllers,
ERP systems used by large agricultural operations. The soil moisture reading triggers
a watering event. The disease detection flags a spray order. At this tier, the system
becomes infrastructure rather than a product.

---

## MVP Scope — MoSCoW Prioritisation

We used MoSCoW to define what Day 1 of a real deployment must include vs. what can wait.

**Must Have**
Soil moisture sensing accurate enough to trigger meaningful alerts.
AI leaf analysis that correctly identifies the most common disease classes.
A server that stores readings and surfaces alerts — even if the dashboard is basic.
Nodes that survive rain and outdoor temperatures for at least one growing season.

**Should Have**
Ambient humidity and light sensing for richer context around moisture readings.
NTP-synced timestamps so data aligns across multiple nodes.
Dynamic send intervals so the system reports more frequently when conditions are critical.

**Could Have**
Predictive disease modelling using time-series soil data, not just snapshot leaf images.
Battery voltage monitoring and low-battery alerts.
OTA firmware updates so deployed nodes don't need physical access to update.

**Won't Have (this iteration)**
LoRa or cellular connectivity — the current system requires local WiFi.
Automated irrigation actuation — we send alerts, we don't yet trigger hardware responses.
Full regulatory certification (CE, FCC) required for commercial distribution.

---

## Hardware Reality

Because we're shipping physical nodes, not just software, the manufacturing constraints
are part of the product definition — not an afterthought.

Components were chosen for immediate availability on standard supplier catalogues
(LCSC, Mouser, DFRobot) so the BOM can be sourced without long lead times.
The AI-Thinker ESP32-CAM and ESP32-C3 are both in mass production with stable supply.

For future commercial distribution, wireless modules operating in the 2.4 GHz and
sub-GHz bands require regional certification — CE for Europe, FCC for North America,
WPC for India. This is planned for after the MVP validation phase, once the core product
has been tested across at least two growing seasons in real field conditions.