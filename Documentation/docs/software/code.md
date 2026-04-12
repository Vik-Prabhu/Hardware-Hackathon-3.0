# Software & Firmware

> **Node Documentation** | ESP32-CAM & Soil Sensor Nodes
> 
> *Distributed passive system communicating via HTTP to a central Python server.*

---

# Software & Firmware

Two independent firmware builds run on two dedicated nodes. Both are passive — they respond
to the central Python server rather than pushing data on their own schedule.

**Camera Node** (AI-Thinker ESP32-CAM) — captures leaf images and ambient DHT22 readings on server trigger.

**Soil Node** (ESP32-C3) — continuously measures soil moisture, temperature, humidity, and light,
posting readings to the server on a dynamic interval.

---

## Part 1 — Camera Node (AI-Thinker ESP32-CAM)

### How It Works

The node connects to WiFi, registers its IP with the server, then idles — the loop only
handles incoming HTTP requests and retries registration if needed.

On `GET /capture` the node reads the DHT22, grabs a JPEG from the OV2640, streams the image
back as `image/jpeg`, and attaches sensor values as custom response headers.
No push, no polling loop — the server decides when to trigger.

### Configuration

```cpp
#define WIFI_SSID          "Vik"
#define WIFI_PASSWORD      "qwertyui"
#define SERVER_HOST        "vikram-Vivobook-Go.local"
#define SERVER_PORT        8000
#define NODE_ID            "N-01"
#define WIFI_CONNECT_TIMEOUT  20000
#define REGISTER_RETRY_DELAY  10000
```

`SERVER_HOST` is resolved via mDNS — the server machine must run Avahi (Linux) or Bonjour (macOS/Windows).

### GPIO Constraints

The OV2640 occupies GPIOs 0, 5, 18, 19, 21–27, 32, 34–36, 39 on the AI-Thinker board.
GPIOs 34–39 are also the ESP32's ADC1 pins, so **`analogRead()` cannot be used for any
analog sensor on this board.** The only free pin for an external sensor is **GPIO 13**,
used by the DHT22.

> Soil moisture and battery voltage require a separate node (Part 2) or an external
> I2C ADC (e.g. ADS1115). Currently `moisture` is aliased to DHT humidity and `battery`
> is hardcoded to `100.0`.

### DHT22 — GPIO 13

```cpp
#define DHT_PIN   13
#define DHT_TYPE  DHT22

float temperature = dht.readTemperature();
float humidity    = dht.readHumidity();

if (isnan(temperature)) temperature = 0.0;
if (isnan(humidity))    humidity    = 0.0;
```

Readings are taken synchronously inside `/capture`. The DHT22's 2-second minimum sample
interval is naturally respected since captures are server-triggered, not continuous.

### Camera Initialisation

Resolution and buffer count are chosen at runtime based on PSRAM availability:

```cpp
if (psramFound()) {
    config.frame_size   = FRAMESIZE_SVGA;   // 800×600
    config.jpeg_quality = 12;
    config.fb_count     = 2;
} else {
    config.frame_size   = FRAMESIZE_VGA;    // 640×480
    config.jpeg_quality = 14;
    config.fb_count     = 1;
}
```

SVGA is preferred over UXGA — higher resolutions cause allocation failures on this board
without PSRAM. Clock is set to 10 MHz (default is 20 MHz) to reduce heat on the module.

After init, auto-exposure, auto-gain, and auto-white-balance are enabled via the sensor register
API. Five warm-up frames are then discarded to let AEC and AWB settle.

### HTTP Endpoints

#### `GET /capture`

1. Returns `503` immediately if a capture is already in progress
2. Reads DHT22
3. Calls `esp_camera_fb_get()` — retries once with a 500 ms delay on failure
4. Sends JPEG with sensor data as response headers
5. Returns frame buffer and clears the `capturing` flag

```cpp
localServer.sendHeader("X-Moisture",    String(moisture, 1));
localServer.sendHeader("X-Temperature", String(temperature, 1));
localServer.sendHeader("X-Battery",     String(battery, 1));
localServer.sendHeader("X-Node-ID",     NODE_ID);
```

Image is streamed in 4096-byte chunks to avoid stalling the WiFi stack.

Possible responses: `200 image/jpeg` on success, `500` if the camera failed, `503` if busy.

#### `GET /health`

Liveness check — no capture triggered. Returns:

```json
{
  "node_id": "N-01",
  "camera": true,
  "capturing": false,
  "uptime": 3742,
  "free_heap": 186432,
  "ip": "192.168.1.105"
}
```

### Server Registration

On boot (and every 10 s while unregistered), the node POSTs its IP:

```
POST http://vikram-Vivobook-Go.local:8000/node/N-01/register
{"ip": "192.168.1.105"}
```

If the server is offline at boot, the node retries silently until it responds.
WiFi drops also reset `registered = false`, triggering re-registration after reconnect.

### Flashing

**Arduino IDE dependencies:** `esp32` board package (Espressif, v2.0.x+),
`DHT sensor library` by Adafruit, `Adafruit Unified Sensor`.

**Board settings:** AI Thinker ESP32-CAM · Upload Speed 115200 · Partition: Huge APP (3MB No OTA).

The ESP32-CAM has no onboard USB. Wire an FTDI FT232RL adapter:

```
FTDI 3.3V  →  ESP32-CAM 3.3V
FTDI GND   →  ESP32-CAM GND
FTDI TX    →  GPIO 3  (U0R)
FTDI RX    →  GPIO 1  (U0T)
FTDI GND   →  IO0     ← hold LOW during flash only
```

Hold IO0 low → press reset → upload → disconnect IO0 → press reset to run.

---

## Part 2 — Soil Sensor Node (ESP32-C3)

### How It Works

Unlike the camera node, the soil node is **push-based** — it wakes on a timer, reads all
four sensors, and POSTs a JSON payload to the server. The send interval is dynamic:
30 seconds under normal conditions, dropping to 5 seconds when soil moisture goes critical.
The server can also override the interval by returning a `next_sleep_min` field in its response.

### Configuration

```cpp
#define PIN_SOIL_MOISTURE   3
#define PIN_LDR             2
#define PIN_DHT             9
#define DHT_TYPE            DHT11

#define SEND_INTERVAL_NORMAL_MS    (30UL * 1000)
#define SEND_INTERVAL_CRITICAL_MS  (5UL  * 1000)
#define MOISTURE_CRITICAL          25

#define WIFI_SSID     "Vik"
#define WIFI_PASSWORD "qwertyui"
#define SERVER_HOST   "vikram-Vivobook-Go.local"
#define SERVER_PORT   8000
#define NODE_ID       "N-02"
```

### Sensors

#### Soil Moisture — GPIO 3 (analog)

Raw ADC output (0–4095) is mapped to a 0–100% scale and inverted — higher raw value
means drier soil on a resistive sensor:

```cpp
int rawSoil   = analogRead(PIN_SOIL_MOISTURE);
data.moisture = (float)constrain(map(rawSoil, 4095, 0, 0, 100), 0, 100);
```

#### Temperature & Humidity — DHT11 on GPIO 9

```cpp
data.humidity    = dht.readHumidity();
data.temperature = dht.readTemperature();
if (isnan(data.humidity))    data.humidity    = 0.0;
if (isnan(data.temperature)) data.temperature = 0.0;
```

Note: DHT11 is used here (not DHT22) — ±2°C and ±5% RH accuracy. Upgrade to DHT22 for
tighter tolerances.

#### Light — LDR on GPIO 2 (analog, GL5528-style)

The LDR sits in a voltage divider with a 100 kΩ pull-down resistor. The ADC reading is
converted to lux through three steps:

```cpp
// 1. ADC counts → voltage at the ADC pin
float v_adc = rawLDR * (LDR_SUPPLY_V / 4095.0f);

// 2. Voltage divider → LDR resistance (LDR between VCC and ADC pin)
float r_ldr = (v_adc > 0.01f)
              ? LDR_PULLDOWN_OHM * (LDR_SUPPLY_V - v_adc) / v_adc
              : 1000000.0f;  // clamp in total darkness

// 3. Power-law model → Lux
// GL5528 characteristic: R_ldr = A × lux^B  →  lux = (R_ldr / A)^(1/B)
float lux = pow(r_ldr / LDR_A, 1.0f / LDR_B);
lux = constrain(lux, 0.0f, 100000.0f);
data.light = (int)lux;
```

Power-law constants used:

```cpp
#define LDR_A  32017.558f   // resistance at reference illuminance (Ω)
#define LDR_B  -0.7f        // slope exponent (negative: more light = less resistance)
```

These are fit to a GL5528 characteristic curve. Recalibrate `LDR_A` and `LDR_B` against
a reference lux meter if accuracy matters.

#### Battery

Currently hardcoded to `100`. Replace with a real ADC read through a resistor divider
when a battery circuit is added.

### Dynamic Send Interval

After every read, the node checks moisture against the critical threshold and adjusts
its interval before posting:

```cpp
sendIntervalMs = (sd.moisture < MOISTURE_CRITICAL)
                 ? SEND_INTERVAL_CRITICAL_MS    // 5 s
                 : SEND_INTERVAL_NORMAL_MS;     // 30 s
```

The server can also push an interval override in the POST response:

```json
{ "next_sleep_min": 10 }
```

If present, `next_sleep_min` (in minutes) overrides the local calculation for the next cycle.

### HTTP POST — `/node/N-02/sensor`

```json
{
  "moisture":    45.0,
  "temperature": 26.2,
  "humidity":    60.0,
  "light":       3200,
  "battery":     100.0,
  "timestamp":   "2026-04-11T12:00:00Z"
}
```

`timestamp` is an ISO 8601 UTC string generated from NTP-synced system time.
If the POST fails, the node retries once after 1 second before moving on.

### NTP Time Sync

The node syncs its clock immediately after WiFi connects in `setup()`:

```cpp
configTime(0, 0, "pool.ntp.org", "time.nist.gov");
```

Timestamps are formatted as ISO 8601 UTC:

```cpp
char buf[25];
strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &t);
```

If NTP fails (10-second timeout), timestamps fall back to `"1970-01-01T00:00:00Z"`.

### Main Loop

```cpp
void loop() {
  if (millis() < nextSendTime) return;  // idle until interval expires

  ensureWiFiConnected();
  SensorData sd = readSensors();

  // pick interval based on moisture level
  sendIntervalMs = (sd.moisture < MOISTURE_CRITICAL)
                   ? SEND_INTERVAL_CRITICAL_MS
                   : SEND_INTERVAL_NORMAL_MS;

  long serverInterval = sendData(sd);
  if (serverInterval == -1) {          // retry once on failure
    delay(1000);
    serverInterval = sendData(sd);
  }
  if (serverInterval > 0)
    sendIntervalMs = (unsigned long)serverInterval;

  nextSendTime = millis() + sendIntervalMs;
}
```

The loop body runs only when `millis()` reaches `nextSendTime` — no `delay()` blocking,
no RTOS tasks. WiFi reconnection is handled inline before every read cycle.

### Flashing

**Arduino IDE dependencies:** `esp32` board package (Espressif), `DHT sensor library` by Adafruit,
`Adafruit Unified Sensor`, `ArduinoJson` by Benoit Blanchon.

**Board settings:** ESP32C3 Dev Module · Upload Speed 115200 · USB CDC On Boot: Enabled.

The ESP32-C3 has a native USB-Serial bridge — no FTDI adapter needed. Connect via USB,
select the correct COM port, and upload directly.