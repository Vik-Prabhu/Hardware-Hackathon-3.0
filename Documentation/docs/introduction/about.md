# About Our Project: Green Node

Welcome to **Green Node**, an advanced, open-source plantation monitoring system built for the Hardware Hackathon 3.0. We are building a comprehensive ecosystem that merges robust hardware edge nodes with a sophisticated AI advisory pipeline to bring state-of-the-art agricultural monitoring to your fingertips.

## Project Showcase

Our solution is divided into distinct, seamlessly integrated components:

### 1. Hardware Edge Nodes
At the core of the Green Node system are our custom-designed hardware nodes, leveraging reliable microcontrollers for real-world deployment:
- **GlyphC3 Sensor Nodes (ESP32-C3):** Engineered for continuous environmental tracking, these nodes gather precise temperature and humidity metrics using minimal power.
- **Vision Nodes (ESP32-CAM):** Equipped with camera modules, these nodes capture visual data of the plantation to enable visual health assessments.

### 2. Comprehensive Data Backend
Built with FastAPI and an SQLite embedded database, the robust backend architecture handles data ingestion from multiple distributed nodes via Wi-Fi network and HTTP. It offers a fully-featured RESTful API to manage the continuous stream of sensor metrics and images.

### 3. AI Health Advisory Pipeline
We integrate leading AI models to analyze the plantation's status:
- Using image and sensor data context, we generate a daily **AI Health Advisory** for the plantation.
- **Multilingual Support:** Powered by the Sarvam AI API, the dashboard provides a daily action plan translated into multiple regional languages, complete with integrated text-to-speech (TTS) playback to make the advisory accessible to every farmer.

### 4. Earthy Editorial Dashboard
All this data is visualized through our beautifully designed Green Node dashboard. Built with an earthy, modern, and editorial design language, the dashboard features:
- Interactive live sensor data
- Scroll-triggered animations and a premium glassmorphic UI
- Actionable AI-driven insights directly in the interface

We are passionate about bringing modern technology to agriculture efficiently, reliably, and elegantly. Explore the rest of the documentation to dive deeper into our hardware architecture, software stack, and implementation methodology!
