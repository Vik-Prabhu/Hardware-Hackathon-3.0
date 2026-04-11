#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <time.h>              // ← added for NTP
#include <ESPmDNS.h>

// ==========================================
// PIN CONFIG BLOCK
// ==========================================
#define PIN_SOIL_MOISTURE   3
#define PIN_LDR             2
#define PIN_DHT             9
#define DHT_TYPE            DHT11

// ==========================================
// SEND INTERVAL CONFIG
// ==========================================
#define SEND_INTERVAL_NORMAL_MS    (30UL * 1000)
#define SEND_INTERVAL_CRITICAL_MS  (5UL  * 1000)
#define MOISTURE_CRITICAL          25

// ==========================================
// NETWORK CONFIG
// ==========================================
#define WIFI_SSID     "Vik"
#define WIFI_PASSWORD "qwertyui"
#define SERVER_HOST   "vikram-Vivobook-Go.local"
#define SERVER_PORT   8000
#define NODE_ID       "N-02"

const unsigned long HTTP_TIMEOUT = 5000;

// ==========================================
// GLOBALS
// ==========================================
DHT dht(PIN_DHT, DHT_TYPE);
unsigned long nextSendTime   = 0;
unsigned long sendIntervalMs = SEND_INTERVAL_NORMAL_MS;

struct SensorData {
  float temperature;
  float humidity;
  float moisture;   // ← now float
  float light;      // ← now float (lux)
  float battery;    // ← now float (voltage)
};

// ==========================================
// NTP
// ==========================================
void syncTime() {
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  Serial.print("[TIME] Syncing NTP");
  struct tm t;
  unsigned long start = millis();
  while (!getLocalTime(&t)) {
    if (millis() - start > 10000) {
      Serial.println("\n[TIME] ✘ NTP sync failed.");
      return;
    }
    delay(200);
    Serial.print(".");
  }
  Serial.println("\n[TIME] ✔ Time synced.");
}

// Returns ISO 8601 string e.g. "2026-04-11T12:00:00Z"
String getISOTimestamp() {
  struct tm t;
  if (!getLocalTime(&t)) return "1970-01-01T00:00:00Z"; // fallback
  char buf[25];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &t);
  return String(buf);
}

// ==========================================
// WiFi
// ==========================================
void ensureWiFiConnected() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.print("[WIFI] (Re)connecting");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start > 10000) {
      Serial.println("\n[WIFI] ✘ Timeout — will retry next cycle.");
      return;
    }
    delay(200);
    Serial.print(".");
  }
  Serial.printf("\n[WIFI] ✔ Connected! IP: %s\n", WiFi.localIP().toString().c_str());
}

// ==========================================
// SENSORS
// ==========================================
SensorData readSensors() {
  SensorData data;

  data.humidity    = dht.readHumidity();
  data.temperature = dht.readTemperature();
  if (isnan(data.humidity))    data.humidity    = 0.0;
  if (isnan(data.temperature)) data.temperature = 0.0;

  int rawSoil   = analogRead(PIN_SOIL_MOISTURE);
  data.moisture = (float)constrain(map(rawSoil, 4095, 0, 0, 100), 0, 100); // ← cast to float

  int rawLDR  = analogRead(PIN_LDR);
  // Map LDR to dummy lux range (0 to 100,000)
  data.light  = (float)constrain(map(rawLDR, 4095, 0, 0, 100000), 0, 100000);

  data.battery = 3.7; // ← hardcoded voltage; swap with real ADC read if you have a divider

  Serial.printf("[SENSOR] Temp: %.1f°C | Hum: %.1f%% | Soil: %.1f%% | Light: %.0flx\n",
                data.temperature, data.humidity, data.moisture, data.light);
  return data;
}

// ==========================================
// HTTP POST
// ==========================================
long sendData(SensorData data) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP] ✘ No WiFi, skipping POST.");
    return -1;
  }

  HTTPClient http;
  String url = "http://" + String(SERVER_HOST) + ":" + String(SERVER_PORT)
               + "/node/" + String(NODE_ID) + "/sensor";

  http.begin(url);
  http.setTimeout(HTTP_TIMEOUT);
  http.addHeader("Content-Type", "application/json");

  // Build payload matching server schema exactly
  String payload = "{";
  payload += "\"moisture\":"    + String(data.moisture, 1)    + ",";  // e.g. 45.0
  payload += "\"temperature\":" + String(data.temperature, 1) + ",";  // e.g. 26.2
  payload += "\"humidity\":"    + String(data.humidity, 1)    + ",";  // e.g. 60.0
  payload += "\"light\":"       + String(data.light, 1)       + ",";  // e.g. 10000.0
  payload += "\"battery\":"     + String(data.battery, 1)     + ",";  // e.g. 3.7
  payload += "\"timestamp\":\""  + getISOTimestamp()          + "\""; // ← ISO string
  payload += "}";

  Serial.printf("[HTTP] Payload: %s\n", payload.c_str());
  int httpCode = http.POST(payload);

  long serverIntervalMs = -1;

  if (httpCode > 0) {
    Serial.printf("[HTTP] ✔ Response: %d\n", httpCode);
    String response = http.getString();

    JsonDocument doc;
    if (!deserializeJson(doc, response) && doc.containsKey("next_sleep_min")) {
      int mins = doc["next_sleep_min"].as<int>();
      serverIntervalMs = (long)mins * 60 * 1000;
      Serial.printf("[HTTP] 📡 Server interval override: %d min\n", mins);
    }
  } else {
    Serial.printf("[HTTP] ✘ POST failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
  return serverIntervalMs;
}

// ==========================================
// SETUP
// ==========================================
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("\n==========================================");
  Serial.println("  GlyphC3 Continuous Monitoring Node     ");
  Serial.println("==========================================");

  analogReadResolution(12);
  dht.begin();

  ensureWiFiConnected();
  
  // Set up mDNS so we can resolve the server's .local hostname
  if (MDNS.begin("green-node-02")) {
    Serial.println("[mDNS] ✔ Responder started: green-node-02.local");
  } else {
    Serial.println("[mDNS] ✘ failed to start");
  }

  syncTime();               // ← sync clock right after WiFi connects
}

// ==========================================
// LOOP
// ==========================================
void loop() {
  if (millis() < nextSendTime) return;

  ensureWiFiConnected();

  SensorData sd = readSensors();

  sendIntervalMs = (sd.moisture < MOISTURE_CRITICAL)
                   ? SEND_INTERVAL_CRITICAL_MS
                   : SEND_INTERVAL_NORMAL_MS;

  if (sd.moisture < MOISTURE_CRITICAL)
    Serial.printf("[LOGIC] ⚠ Moisture critical (%.1f%%). Fast interval active.\n", sd.moisture);

  long serverInterval = sendData(sd);

  if (serverInterval == -1) {
    Serial.println("[HTTP] Retrying in 1s...");
    delay(1000);
    serverInterval = sendData(sd);
  }

  if (serverInterval > 0)
    sendIntervalMs = (unsigned long)serverInterval;

  nextSendTime = millis() + sendIntervalMs;
  Serial.printf("[LOOP] Next send in %lu seconds.\n\n", sendIntervalMs / 1000);
}