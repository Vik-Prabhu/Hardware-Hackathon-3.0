# Setup & Installation

Welcome to the comprehensive implementation guide. This section details how to set up the entire project—covering the Software (Backend and AI), Firmware (ESP32 Sensor Nodes), and Frontend Dashboard components.

## 📝 Prerequisites
Ensure you have the following installed on your local machine:
- **Python 3.10+**: For running the FastAPI backend.
- **Node.js (v18+) & npm**: For the VitePress frontend dashboard.
- **Arduino IDE / PlatformIO**: For flashing the microcontrollers.
- **ESP32 Board Support**: Installed in your Arduino IDE/PlatformIO.
- **Microcontrollers**: ESP32-C3 (Sensor Node) and ESP32-CAM (Vision Node), along with their respective sensors (DHT11, Soil Moisture, LDR, etc.).

---

## 🖥️ 1. Software Setup: Backend Server & AI

The backend is built with FastAPI. It handles sensor data, image uploads, AI advisory proxying, and acts as the central hub for the monitoring system.

### Step 1: Install Dependencies
Navigate to the `server` directory and install the required Python packages:

```bash
cd server
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Inside the `server` directory, create a `.env` file (if not already present). *Do not hardcode or commit actual API keys or IP addresses to public repositories.*

Create an `.env` file referencing the layout below:
```ini
# Environment Variables Configuration
AI_SERVER_URL=http://<YOUR_AI_MICROSERVICE_IP>:<PORT>
SARVAM_API_KEY=your_sarvam_api_key_here
```
> **Note**: Replace `<YOUR_AI_MICROSERVICE_IP>` with the local or public IP address of your AI endpoint, and provide your Sarvam API Key for multilingual support.

### Step 3: Run the Server
Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The server will initialize the SQLite database automatically upon startup and start listening to incoming node data.

---

## 🤖 2. Firmware Setup: ESP32 Nodes

The project uses two generic types of nodes: the `esp32cam_node` for vision/camera capabilities and the `glyph_c3_node` for environmental sensing.

### Step 1: Prepare the IDE
1. Open the Arduino IDE.
2. In Board Manager, ensure you have the `esp32` package by Expressif Systems installed.
3. Install necessary libraries (e.g., DHT sensor libraries) via the Library Manager.

### Step 2: Configure Node Credentials
Before flashing, you must update the firmware code with your network specifics. Open the respective `.ino` or header config files in the `firmware/esp32cam_node/` and `firmware/glyph_c3_node/` directories.

Look for the configuration section and update it:
```cpp
// General Network Configuration (DO NOT commit your actual credentials)
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server Endpoint Setup
const char* serverUrl = "http://<YOUR_BACKEND_SERVER_IP>:8000"; 
```
> **Important**: Replace `<YOUR_BACKEND_SERVER_IP>` with the IPv4 address of the machine running your FastAPI server. Make sure your nodes and the server are on the same network.

### Step 3: Flash the Firmware
1. Connect the ESP32 node to your PC.
2. Select the correct board and COM port in the IDE. 
   - For ESP32-CAM: Use `AI Thinker ESP32-CAM`.
   - For ESP32-C3: Use `ESP32C3 Dev Module`.
3. Click **Upload**. Wait for the process to complete and confirm via the Serial Monitor (Baud rate typically `115200`) that the node successfully connects to WiFi and registers with your server.

---

## 📊 3. Frontend Setup: Dashboard & Docs

The UI and project documentation are built seamlessly into a single web application using VitePress.

### Step 1: Install Node Dependencies
Open a new terminal window, navigate to the `Documentation` directory, and install the NPM packages:

```bash
cd Documentation
npm install
```

### Step 2: Start the Development Server
Launch the VitePress site, which hosts your immersive dashboard and documentation.

```bash
npx vitepress dev docs
```

The application will typically be accessible at `http://localhost:5173`. Open this URL in your browser to view your live, highly dynamic dashboard displaying the inbound sensor data and AI-driven plant advisories.

---

## 🛡️ Security Best Practices
As an open-source project, please strictly follow these guidelines:
- **Never push secrets**: Ensure `.env` files and `firmware/` configuration files with hardcoded Wi-Fi passwords or API keys are added to your `.gitignore`.
- **Use local IPs for testing**: Rely on local or private IP ranges (`192.168.x.x` or `10.x.x.x`) for inter-device communication during development.
- **Rotate leaked keys**: If you accidentally leak an API token or password, revoke it immediately from the service provider and generate a new one.
