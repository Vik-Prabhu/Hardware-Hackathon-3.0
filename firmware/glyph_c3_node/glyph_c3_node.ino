/* 
 * 🌿 Plantation Monitoring Node — GlyphC3 (ESP32-C3)
 * Board: GlyphC3 by PCBCupid
 * 
 * Features:
 * - Ultra-Low Power Deep Sleep Architecture
 * - RTC-backed Fast WiFi Connect
 * - Adaptive Sleep Intervals (Local & Server Override)
 * - Auto Sensor Power Switching via MOSFET
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <esp_sleep.h>

// ==========================================
// PIN CONFIG BLOCK (Clearly labelled)
// ==========================================
#define PIN_SOIL_MOISTURE   4    // analog ADC pin
#define PIN_LDR             3    // analog ADC pin  
#define PIN_DHT             5    // digital pin
#define SENSOR_POWER_PIN    2    // GPIO that powers all sensors via MOSFET
#define DHT_TYPE            DHT11

// ==========================================
// SLEEP CONFIG BLOCK
// ==========================================
#define SLEEP_NORMAL_MIN    30   // minutes between reads in normal state
#define SLEEP_CRITICAL_MIN  5    // minutes if sensor value is critical
#define MOISTURE_CRITICAL   25   // below this = critical (%), sleep less

// ==========================================
// NETWORK CONFIG BLOCK 
// ==========================================
#define WIFI_SSID           "your_ssid"
#define WIFI_PASSWORD       "your_password"
#define SERVER_IP           "192.168.x.x"
#define SERVER_PORT         8000
#define NODE_ID             "N-02"

// Constraints
const unsigned long MAX_AWAKE_MS  = 20000; // Never stay awake > 20s
const unsigned long HTTP_TIMEOUT  = 5000;
unsigned long bootTime = 0;

// ==========================================
// RTC MEMORY (Preserved in deep sleep)
// ==========================================
RTC_DATA_ATTR int rtc_wifi_channel = 0;
RTC_DATA_ATTR uint8_t rtc_bssid[6] = {0};
RTC_DATA_ATTR bool rtc_has_wifi_data = false;

// ==========================================
// GLOBALS
// ==========================================
DHT dht(PIN_DHT, DHT_TYPE);

struct SensorData {
  float temperature;
  float humidity;
  int moisture;
  int light;
  int battery;
};

// ==========================================
// UTILS
// ==========================================
void goToSleep(int minutes) {
  unsigned long awakeTime = millis() - bootTime;
  Serial.printf("\n[POWER] Awake time: %lu ms\n", awakeTime);
  Serial.printf("[POWER] 💤 Going to deep sleep for %d minutes...\n", minutes);
  
  WiFi.disconnect(true);
  
  uint64_t sleepTime_us = (uint64_t)minutes * 60 * 1000000ULL;
  esp_sleep_enable_timer_wakeup(sleepTime_us);
  esp_deep_sleep_start();
}

void checkTimeout() {
  if (millis() - bootTime >= MAX_AWAKE_MS) {
    Serial.println("\n[POWER] ⏰ Max awake time reached (20s). Forcing sleep!");
    goToSleep(SLEEP_NORMAL_MIN); // Fallback to normal if timed out
  }
}

// ==========================================
// LOGIC
// ==========================================

void printWakeReason() {
  esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
  Serial.print("[POWER] Wakeup Reason: ");
  switch(wakeup_reason) {
    case ESP_SLEEP_WAKEUP_TIMER: Serial.println("Timer"); break;
    default: Serial.println("Power-on / Other"); break;
  }
}

SensorData readSensors() {
  SensorData data;

  Serial.println("[SENSOR] Powering ON sensors...");
  digitalWrite(SENSOR_POWER_PIN, HIGH);
  
  // Wait 1 second for sensor stabilisation
  delay(1000); 

  // Initialize DHT here after power is on
  dht.begin();
  
  data.humidity = dht.readHumidity();
  data.temperature = dht.readTemperature();
  if (isnan(data.humidity)) data.humidity = 0;
  if (isnan(data.temperature)) data.temperature = 0;

  // Read analog value (ESP32-C3 ADC is 12-bit max 4095)
  int rawSoil = analogRead(PIN_SOIL_MOISTURE);
  data.moisture = map(rawSoil, 4095, 0, 0, 100);
  data.moisture = constrain(data.moisture, 0, 100);

  int rawLDR = analogRead(PIN_LDR);
  data.light = map(rawLDR, 4095, 0, 0, 100);
  data.light = constrain(data.light, 0, 100);

  data.battery = 100; // Hardcoded fallback

  Serial.println("[SENSOR] Powering OFF sensors immediately.");
  digitalWrite(SENSOR_POWER_PIN, LOW); // Save power instantly
  
  Serial.printf("[SENSOR] Temp: %.1fC | Hum: %.1f%% | Soil: %d%% | Light: %d%%\n",
                data.temperature, data.humidity, data.moisture, data.light);

  return data;
}

bool connectWiFiFast() {
  Serial.print("[WIFI] Connecting");
  
  WiFi.mode(WIFI_STA);

  if (rtc_has_wifi_data) {
    Serial.printf(" (Fast Connect CH: %d BSSID: %02X:%02X:%02X:%02X:%02X:%02X)\n", 
                  rtc_wifi_channel, rtc_bssid[0], rtc_bssid[1], rtc_bssid[2], 
                  rtc_bssid[3], rtc_bssid[4], rtc_bssid[5]);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD, rtc_wifi_channel, rtc_bssid);
  } else {
    Serial.println(" (Full Scan)");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  }

  unsigned long wifiStart = millis();
  while (WiFi.status() != WL_CONNECTED) {
    checkTimeout();
    if (millis() - wifiStart > 10000) {
      Serial.println("\n[WIFI] ✘ Connection timeout (10s)");
      return false; // Failed
    }
    delay(100);
    Serial.print(".");
  }

  Serial.println("\n[WIFI] ✔ Connected!");
  
  // Save credentials to RTC if we didn't have them
  if (!rtc_has_wifi_data) {
    rtc_wifi_channel = WiFi.channel();
    memcpy(rtc_bssid, WiFi.BSSID(), 6);
    rtc_has_wifi_data = true;
    Serial.println("[WIFI] ✔ Saved BSSID/Channel to RTC memory.");
  }
  
  return true;
}

int sendDataAndGetSleepParam(SensorData data) {
  HTTPClient http;
  String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/node/" + String(NODE_ID) + "/sensor";
  int nextSleepOverride = -1;
  
  http.begin(url);
  http.setTimeout(HTTP_TIMEOUT);
  http.addHeader("Content-Type", "application/json");

  // Construct JSON
  String payload = "{";
  payload += "\"moisture\":" + String(data.moisture) + ",";
  payload += "\"temperature\":" + String(data.temperature) + ",";
  payload += "\"humidity\":" + String(data.humidity) + ",";
  payload += "\"light\":" + String(data.light) + ",";
  payload += "\"battery\":" + String(data.battery) + ",";
  payload += "\"timestamp\":" + String(millis());
  payload += "}";

  Serial.printf("[HTTP] POSTing to %s\n", url.c_str());
  
  int httpCode = http.POST(payload);
  
  if (httpCode > 0) {
    Serial.printf("[HTTP] ✔ Response Code: %d\n", httpCode);
    
    // Check for next_sleep_min directive
    String response = http.getString();
    
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, response);
    
    if (!error && doc.containsKey("next_sleep_min")) {
      nextSleepOverride = doc["next_sleep_min"].as<int>();
      Serial.printf("[HTTP] 📡 Server requested sleep override: %d mins\n", nextSleepOverride);
    }
  } else {
    Serial.printf("[HTTP] ✘ POST failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
  return nextSleepOverride;
}


// ==========================================
// MAIN BOOT SEQUENCE
// ==========================================
void setup() {
  bootTime = millis();
  
  Serial.begin(115200);
  delay(100); // Give serial time to attach
  Serial.println("\n\n==========================================");
  Serial.println("  GlyphC3 Ultra-Low Power Node Booting  ");
  Serial.println("==========================================");

  // 1. PIN SETUP & WAKE REASON
  pinMode(SENSOR_POWER_PIN, OUTPUT);
  digitalWrite(SENSOR_POWER_PIN, LOW); // ensure off initially
  analogReadResolution(12);
  
  printWakeReason();
  
  // 2. READ SENSORS
  SensorData sd = readSensors();
  checkTimeout();
  
  // 3. CONNECT WIFI
  bool wifiConnected = connectWiFiFast();
  checkTimeout();
  
  // 4. SEND DATA & CALCULATE NEXT SLEEP
  int sleepDuration = SLEEP_NORMAL_MIN;
  
  if (sd.moisture < MOISTURE_CRITICAL) {
     sleepDuration = SLEEP_CRITICAL_MIN;
     Serial.printf("[LOGIC] Moisture critical (%d%%). Using short sleep interval.\n", sd.moisture);
  }
  
  if (wifiConnected) {
    int serverSleepOverride = sendDataAndGetSleepParam(sd);
    
    // Handle HTTP Retry (once)
    if (serverSleepOverride == -1) {
       Serial.println("[HTTP] Retry attempt in 1 second...");
       delay(1000); // short wait before retry
       checkTimeout();
       serverSleepOverride = sendDataAndGetSleepParam(sd);
    }
    
    if (serverSleepOverride > 0) {
       sleepDuration = serverSleepOverride;
    }
  } else {
    Serial.println("[LOGIC] Skipping POST due to WiFi failure.");
  }

  // 5. GO TO DEEP SLEEP (Disconnects WiFi automatically)
  goToSleep(sleepDuration);
}

void loop() {
  // Empty - Node goes to deep sleep at the end of setup()
}
