/*
 * ═══════════════════════════════════════════════════════════════════
 *  Green Node — ESP32-CAM Firmware (Trigger Mode)
 *
 *  Does NOTHING until the server requests data.
 *  On trigger: captures photo + reads DHT22 sensor, sends back.
 *
 *  NOTE: On AI-Thinker ESP32-CAM, GPIO32-39 are ALL used by the
 *  camera module, so analog sensors (moisture, battery) need an
 *  external I2C ADC or a separate ESP32. Only DHT22 on GPIO13 works.
 * ═══════════════════════════════════════════════════════════════════
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include "esp_camera.h"
#include "DHT.h"

// ═══════════════════════════════════════════════════════════════════
//  CONFIGURATION
// ═══════════════════════════════════════════════════════════════════

#define WIFI_SSID          "Vik"
#define WIFI_PASSWORD      "qwertyui"

#define SERVER_HOST        "vikram-Vivobook-Go.local"
#define SERVER_PORT        8000
#define NODE_ID            "N-01"

#define WIFI_CONNECT_TIMEOUT 20000
#define REGISTER_RETRY_DELAY 10000

// ═══════════════════════════════════════════════════════════════════
//  SENSOR PIN  (only DHT22 — analog pins conflict with camera!)
// ═══════════════════════════════════════════════════════════════════

#define DHT_PIN            13
#define DHT_TYPE           DHT22

// GPIO34 = Camera Y8, GPIO35 = Camera Y9 — CANNOT use for analogRead!
// GPIO36/39 = Camera Y6/Y7 — also camera pins.
// Moisture & battery require external I2C ADC (ADS1115) or separate MCU.

// ═══════════════════════════════════════════════════════════════════
//  AI-THINKER ESP32-CAM PIN CONFIG
// ═══════════════════════════════════════════════════════════════════

#define PWDN_GPIO_NUM      32
#define RESET_GPIO_NUM     -1
#define XCLK_GPIO_NUM       0
#define SIOD_GPIO_NUM      26
#define SIOC_GPIO_NUM      27
#define Y9_GPIO_NUM        35
#define Y8_GPIO_NUM        34
#define Y7_GPIO_NUM        39
#define Y6_GPIO_NUM        36
#define Y5_GPIO_NUM        21
#define Y4_GPIO_NUM        19
#define Y3_GPIO_NUM        18
#define Y2_GPIO_NUM         5
#define VSYNC_GPIO_NUM     25
#define HREF_GPIO_NUM      23
#define PCLK_GPIO_NUM      22

// ═══════════════════════════════════════════════════════════════════
//  GLOBALS
// ═══════════════════════════════════════════════════════════════════

DHT dht(DHT_PIN, DHT_TYPE);
WebServer localServer(80);
bool cameraReady = false;
bool registered = false;
bool capturing = false;

// ═══════════════════════════════════════════════════════════════════
//  WiFi
// ═══════════════════════════════════════════════════════════════════

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;
  Serial.printf("[WiFi] Connecting to %s", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start > WIFI_CONNECT_TIMEOUT) {
      Serial.println("\n[WiFi] ✘ Connection timeout");
      return;
    }
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\n[WiFi] ✔ Connected — IP: %s\n", WiFi.localIP().toString().c_str());
}

bool ensureWiFi() {
  if (WiFi.status() == WL_CONNECTED) return true;
  connectWiFi();
  return WiFi.status() == WL_CONNECTED;
}

// ═══════════════════════════════════════════════════════════════════
//  REGISTER
// ═══════════════════════════════════════════════════════════════════

void registerWithServer() {
  if (!ensureWiFi()) return;

  String url = "http://" + String(SERVER_HOST) + ":" + String(SERVER_PORT)
             + "/node/" + NODE_ID + "/register";
  String json = "{\"ip\":\"" + WiFi.localIP().toString() + "\"}";

  HTTPClient http;
  http.begin(url);
  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(json);
  if (code == 200) {
    Serial.printf("[REG]  ✔ Registered with server\n");
    registered = true;
  } else {
    Serial.printf("[REG]  ✘ Failed (HTTP %d)\n", code);
  }
  http.end();
}

// ═══════════════════════════════════════════════════════════════════
//  /capture — Triggered by server. Returns photo + sensor headers.
// ═══════════════════════════════════════════════════════════════════

void handleCapture() {
  if (capturing) {
    localServer.send(503, "text/plain", "Capture already in progress");
    return;
  }
  capturing = true;

  Serial.println("\n[TRIG] ═══════════════════════════════════");
  Serial.println("[TRIG] 📡 Capture requested by server!");

  // --- Read DHT22 sensor (safe — GPIO13 is not a camera pin) ---
  float temperature = dht.readTemperature();
  float humidity    = dht.readHumidity();

  if (isnan(temperature)) temperature = 0.0;
  if (isnan(humidity))    humidity = 0.0;

  // Moisture, light, & battery are placeholders until external ADC is wired
  float moisture = humidity;   // Use DHT humidity as a proxy for now
  float light    = 10000.0;    // Dummy lux value
  float battery  = 100.0;     // No ADC available — hardcode

  Serial.printf("[SENS] temp=%.1f°C  hum=%.1f%%  light=%.0flx  (bat=%.0f%% placeholder)\n",
                temperature, humidity, light, battery);

  // --- Capture photo ---
  if (!cameraReady) {
    Serial.println("[CAM]  ✘ Camera not ready");
    localServer.send(500, "text/plain", "Camera not initialized");
    capturing = false;
    return;
  }

  // Grab a fresh frame
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[CAM]  ✘ First grab failed — retrying...");
    delay(500);
    fb = esp_camera_fb_get();
  }

  if (!fb) {
    Serial.println("[CAM]  ✘ Capture failed after retry");
    localServer.send(500, "text/plain", "Frame capture failed");
    capturing = false;
    return;
  }

  Serial.printf("[CAM]  📸 Captured %u bytes (%dx%d)\n", fb->len, fb->width, fb->height);

  // --- Send response ---
  localServer.sendHeader("Access-Control-Allow-Origin", "*");
  localServer.sendHeader("Access-Control-Expose-Headers",
                         "X-Moisture, X-Temperature, X-Humidity, X-Light, X-Battery, X-Node-ID");
  localServer.sendHeader("X-Moisture", String(moisture, 1));
  localServer.sendHeader("X-Temperature", String(temperature, 1));
  localServer.sendHeader("X-Humidity", String(humidity, 1));
  localServer.sendHeader("X-Light", String(light, 1));
  localServer.sendHeader("X-Battery", String(battery, 1));
  localServer.sendHeader("X-Node-ID", NODE_ID);

  localServer.setContentLength(fb->len);
  localServer.send(200, "image/jpeg", "");

  WiFiClient client = localServer.client();

  // Send in chunks
  size_t sent = 0;
  const size_t CHUNK = 4096;
  while (sent < fb->len) {
    size_t toSend = min(CHUNK, fb->len - sent);
    client.write(fb->buf + sent, toSend);
    sent += toSend;
  }

  Serial.printf("[TRIG] ✔ Sent %u bytes to server\n", sent);

  // --- Cleanup ---
  esp_camera_fb_return(fb);
  fb = NULL;

  delay(100);
  capturing = false;
  Serial.println("[TRIG] ✔ Ready for next request");
  Serial.println("[TRIG] ═══════════════════════════════════\n");
}

// ═══════════════════════════════════════════════════════════════════
//  /health
// ═══════════════════════════════════════════════════════════════════

void handleHealth() {
  String json = "{\"node_id\":\"" + String(NODE_ID) + "\","
                "\"camera\":" + String(cameraReady ? "true" : "false") + ","
                "\"capturing\":" + String(capturing ? "true" : "false") + ","
                "\"uptime\":" + String(millis() / 1000) + ","
                "\"free_heap\":" + String(ESP.getFreeHeap()) + ","
                "\"ip\":\"" + WiFi.localIP().toString() + "\"}";
  localServer.sendHeader("Access-Control-Allow-Origin", "*");
  localServer.send(200, "application/json", json);
}

// ═══════════════════════════════════════════════════════════════════
//  CAMERA INIT
// ═══════════════════════════════════════════════════════════════════

bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;

  config.xclk_freq_hz = 10000000;     // 10MHz — lower heat
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode    = CAMERA_GRAB_LATEST;

  if (psramFound()) {
    config.frame_size   = FRAMESIZE_SVGA;    // 800x600 — reliable
    config.jpeg_quality = 12;
    config.fb_count     = 2;
    Serial.println("[CAM]  PSRAM found — using SVGA (800x600)");
  } else {
    config.frame_size   = FRAMESIZE_VGA;     // 640x480
    config.jpeg_quality = 14;
    config.fb_count     = 1;
    Serial.println("[CAM]  No PSRAM — using VGA (640x480)");
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[CAM]  ✘ Init failed: 0x%x\n", err);
    return false;
  }

  sensor_t *s = esp_camera_sensor_get();
  if (s) {
    s->set_brightness(s, 1);
    s->set_saturation(s, 1);
    s->set_whitebal(s, 1);
    s->set_awb_gain(s, 1);
    s->set_exposure_ctrl(s, 1);
    s->set_aec2(s, 1);
    s->set_gain_ctrl(s, 1);
  }

  // Warm up — discard first few frames
  Serial.println("[CAM]  Warming up...");
  for (int i = 0; i < 5; i++) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (fb) esp_camera_fb_return(fb);
    delay(100);
  }

  Serial.println("[CAM]  ✔ Camera ready");
  return true;
}

// ═══════════════════════════════════════════════════════════════════
//  SETUP
// ═══════════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("═══════════════════════════════════════════");
  Serial.println("  🌿 Green Node — Trigger Mode");
  Serial.printf("     Node: %s\n", NODE_ID);
  Serial.printf("     Server: %s:%d\n", SERVER_HOST, SERVER_PORT);
  Serial.println("     Mode: IDLE until triggered");
  Serial.println("═══════════════════════════════════════════");

  dht.begin();
  
  cameraReady = initCamera();
  connectWiFi();

  // Initialize mDNS
  if (MDNS.begin("green-node-01")) {
    Serial.println("[mDNS] ✔ Responder started: green-node-01.local");
  }

  localServer.on("/capture", HTTP_GET, handleCapture);
  localServer.on("/health",  HTTP_GET, handleHealth);
  localServer.begin();
  Serial.println("[SRV]  ✔ Web server started on port 80");

  registerWithServer();

  Serial.println("\n[IDLE] 💤 Waiting for capture trigger...\n");
}

// ═══════════════════════════════════════════════════════════════════
//  MAIN LOOP — Just listen
// ═══════════════════════════════════════════════════════════════════

unsigned long lastRegRetry = 0;

void loop() {
  localServer.handleClient();

  if (!registered && millis() - lastRegRetry > REGISTER_RETRY_DELAY) {
    lastRegRetry = millis();
    registerWithServer();
  }

  if (WiFi.status() != WL_CONNECTED) {
    registered = false;
    connectWiFi();
  }

  delay(10);
}