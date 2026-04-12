# Communication Protocols

This document outlines the architecture, data flows, and security mechanisms of the communication protocols utilized in the Hardware Hackathon system.

## 📡 Core Protocol Architecture

The system operates primarily on **HTTP/1.1** over IPv4 TCP/IP, broadcasted over an IEEE 802.11 (WiFi) local network. We chose standard HTTP for its simplicity, ease of debugging, and strong compatibility with the FastAPI backend and ESP32 `WebServer` / `HTTPClient` frameworks.

In addition to HTTP, **mDNS (Multicast DNS)** is optionally configured for localized server-node discovery without hardcoding dynamic IPs.

### Protocol Breakdown

#### 1. Node-to-Server Data Transmission (HTTP POST)
- **Data Format**: JSON Payload
- **Role**: ESP32 nodes periodically acquire sensor data (temperature, humidity, moisture, light) and serialize it.
- **Endpoint**: `/node/{node_id}/sensor`
- **Mechanism**: The ESP32 node acts as an HTTP client, making asynchronous `POST` requests to the FastAPI backend. Nodes also announce their presence via a periodic `/node/{node_id}/register` ping so the server can track dynamic local IP assignments.

#### 2. Server-to-Node Polling (HTTP GET)
- **Data Format**: Image stream (JPEG/Multipart) & Metadata in Custom HTTP Headers
- **Role**: The backend server can remotely trigger a photo capture for vision-enabled nodes (`esp32cam_node`).
- **Endpoint (on Node)**: `http://{node_ip}/capture`
- **Mechanism**: The FastAPI server acts as an HTTP Client, sending requests to the embedded WebServer concurrently running on the ESP32. The node replies with a raw JPEG byte stream. Essential sensor metadata is bundled directly into the outbound `HTTP Headers` (e.g., `X-Moisture`, `X-Temperature`) to save bandwidth and simplify parsing.

#### 3. Client-to-Server Dashboard API (HTTP)
- **Data Format**: RESTful JSON API
- **Role**: The VitePress front-end dashboard fetches historical logs, AI advisories, real-time alerts, and captures.
- **Mechanism**: Standard `GET` and `POST` requests utilizing browser-native `fetch`.

#### 4. Server-to-AI Microservices (HTTP / HTTPS)
- **Data Format**: JSON & Multipart Form Data
- **Role**: Offloads logic to heavier deep-learning models for image/sensor analysis and multi-lingual translation.
- **Mechanism**:
  - **Internal AI API**: The backend forwards hardware requests to the local `AI_SERVER_URL` via proxy requests.
  - **External Cloud API**: Sarvam AI text translations are sent securely over the Wide Area Network (WAN) via `HTTPS` (`https://api.sarvam.ai/translate`).

---

## 🔒 Security & Safety Mechanisms

Given the constraints of Internet of Things (IoT) environments, network safety requires a combination of boundary fortification and internal resilience. Because this project is designed as an open-source, edge-computing blueprint deployed on private spaces, we prioritize internal segmentation and logical boundaries.

### 1. Isolated Network Topology
The sensor nodes are **never** exposed directly to the public internet. All nodes communicate *only* with the local Gateway (FastAPI server). The backend proxy acts as a firewall and orchestrator, shielding the microcontrollers from external attacks, port scanning, or malicious polling.

### 2. Transport Layer Security (HTTPS vs. HTTP)
- **Local Network**: Inter-node communication (ESP32 ↔ Local Server) uses plain `HTTP`. In heavily constrained devices (like standard ESP32 boards), encrypting every localized TCP packet payload incurs significant computational overhead, which drains battery and introduces latency. We mitigate the risk by relying entirely on the base **WPA2/WPA3 Wi-Fi encryption**. Packet-sniffing requires first circumventing the wireless router's security layer.
- **Outbound Traffic**: Any communication leaving the local edge network to hit external endpoints (e.g., the Sarvam AI Language API) is fully secured using **HTTPS (TLS 1.2/1.3)** to prevent MiTM (Man in the Middle) interception.

### 3. Rate Limiting and Resilience
- **Node Side (Non-Blocking)**: The firmware leverages a hardware timer & `millis()` architecture rather than `delay()`. If the server drops offline or an HTTP timeout occurs, the node gracefully abandons the connection and continues acquiring hardware metrics without freezing the execution loop.
- **Server Side (Asynchronous)**: The FastAPI server applies decoupled asynchronous handlers (`aiohttp`) with strict lifecycle bounds (e.g., local `ClientTimeout`). If an ESP32 node hangs mid-transmission due to signal attenuation, the server proactively drops the connection, preventing resource exhaustion and blocking.

### 4. Codebase Credential Hardening
- Platform secrets—like the `SARVAM_API_KEY` and remote endpoints `AI_SERVER_URL`—are kept strictly decoupled via environment variables (`.env`).
- Environment templates are inherently shielded. `git` enforces ignorance of `.env` files, prohibiting source-code credential leakage to GitHub. No sensitive token is embedded into the compiled Arduino binaries either.

---

## 📝 Network Flow Diagram

![Network Flowchart](/simple_flowchart.png)
