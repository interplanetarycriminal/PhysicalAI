/*
 * condensation_watch.cpp
 *
 * Fusion edge key : condensation-watch      ("Condensation forecaster")
 * Pattern         : differential
 * Requires        : dew-point x1, temperature-remote x1
 * Provides        : condensation-risk  (EMERGENT — no catalog sensor claims it)
 * Atlas source    : sensor-universe/data/fusion.py, FUSION_EDGES
 *
 * math (verbatim from fusion.py):
 *   "Risk when T_surface − T_dew < 1.5°C (T_dew via Magnus:
 *    γ = ln(RH/100) + 17.62·T/(243.12+T))"
 *
 * confound (verbatim from fusion.py):
 *   "Emissivity: a shiny surface lies to the IR thermometer by 20×
 *    (Anti-Catalog II). Put a strip of matt tape at the cold spot and aim at
 *    that."
 *
 * example (verbatim from fusion.py):
 *   "SHT41 for dew point + MLX90614 aimed at the bathroom's coldest corner →
 *    alert BEFORE the wall sweats, which is the mould sentinel working a week
 *    early."
 *
 * ---------------------------------------------------------------------------
 * WIRING — 3V3 ONLY on both parts. The MLX90614 module is NOT 5V-logic-safe:
 * a 5V-fed GY-906 puts 5 V on SDA/SCL and on the ESP32's GPIOs.
 * ---------------------------------------------------------------------------
 *
 * ESP32-S3 devkit (DevKitC-1 class)
 *   signal | S3 pin  | SHT41 (0x44)  | MLX90614 GY-906 (0x5A)
 *   -------+---------+---------------+------------------------
 *   SDA    | GPIO8   | SDA           | SDA
 *   SCL    | GPIO9   | SCL           | SCL
 *   3V3    | 3V3     | VIN / VDD     | VIN  (NOT 5V)
 *   GND    | GND     | GND           | GND
 *   addr   | —       | fixed 0x44    | fixed 0x5A (EEPROM-changeable)
 *
 * Classic ESP32 devkit (WROOM-32)
 *   signal | ESP32 pin | SHT41 (0x44) | MLX90614 GY-906 (0x5A)
 *   -------+-----------+--------------+------------------------
 *   SDA    | GPIO21    | SDA          | SDA
 *   SCL    | GPIO22    | SCL          | SCL
 *   3V3    | 3V3       | VIN / VDD    | VIN  (NOT 5V)
 *   GND    | GND       | GND          | GND
 *   addr   | —         | fixed 0x44   | fixed 0x5A
 *
 * Bus runs at 100 kHz: the MLX90614 speaks SMBus, not plain I2C, and behaves
 * badly next to parts that stretch SCL. Two breakouts in parallel is fine with
 * their stock 4.7k pull-ups; do not add more without removing some.
 *
 * Placement: mount the SHT41 on a flying lead away from the ESP32 and the
 * regulator. Its own catalog record warns that a nearby ESP32 raises the
 * temperature channel 1-3°C, and RH is computed against that temperature, so
 * 1°C of error is roughly 6 points of RH — i.e. a wrong dew point.
 *
 * NOTHING IN THIS FILE HAS BEEN RUN ON HARDWARE. See ../README.md.
 */

#include <Arduino.h>
#include <Wire.h>

#include <Adafruit_MLX90614.h>
#include <Adafruit_SHT4x.h>

#include "physlib.h"

/* --- I2C pins, defined explicitly rather than trusting the variant ------- */
#if CONFIG_IDF_TARGET_ESP32S3
#define PIN_I2C_SDA 8
#define PIN_I2C_SCL 9
#define BOARD_NAME "ESP32-S3"
#else /* classic ESP32 / WROOM-32 */
#define PIN_I2C_SDA 21
#define PIN_I2C_SCL 22
#define BOARD_NAME "ESP32 (classic)"
#endif

#define I2C_HZ 100000 /* 100 kHz — the MLX90614 is an SMBus part */

#define ADDR_SHT41 0x44
#define ADDR_MLX90614 0x5A

#define SAMPLE_PERIOD_MS 5000UL

static Adafruit_SHT4x sht4;
static Adafruit_MLX90614 mlx;

static bool sensors_ready = false;

/** Does a device ACK its address on the bus? */
static bool i2c_acks(uint8_t addr) {
    Wire.beginTransmission(addr);
    return Wire.endTransmission() == 0;
}

static void fail_loudly(const char *what) {
    Serial.println();
    Serial.println("################################################");
    Serial.print("# BRING-UP FAILURE: ");
    Serial.println(what);
    Serial.println("# Check: 3V3 (never 5V), SDA/SCL not swapped, common GND,");
    Serial.println("# pull-ups present on at most two breakouts, <30 cm of wire.");
    Serial.println("################################################");
}

static void print_confound(const physlib::EdgeResult &r) {
    Serial.print("  confound      : ");
    Serial.println(r.confound == physlib::ConfoundState::Detected
                       ? "DETECTED — do not trust this reading as it stands"
                       : "standing (always applies, nothing detected)");
    Serial.print("    always      : ");
    Serial.println(r.confound_text);
    if (r.confound_detail != nullptr) {
        Serial.print("    detected    : ");
        Serial.println(r.confound_detail);
    }
}

void setup() {
    Serial.begin(115200);
    delay(300);
    Serial.println();
    Serial.println("=== fusion edge: condensation-watch ===");
    Serial.println("provides: condensation-risk (EMERGENT)");
    Serial.print("board: ");
    Serial.print(BOARD_NAME);
    Serial.print("  SDA=GPIO");
    Serial.print(PIN_I2C_SDA);
    Serial.print("  SCL=GPIO");
    Serial.print(PIN_I2C_SCL);
    Serial.println("  bus=100 kHz");

    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, I2C_HZ);

    bool ok = true;
    if (!i2c_acks(ADDR_SHT41)) {
        fail_loudly("no ACK from the SHT41 at 0x44");
        ok = false;
    }
    if (!i2c_acks(ADDR_MLX90614)) {
        fail_loudly("no ACK from the MLX90614 at 0x5A");
        Serial.println("# If 0x44 answers alone but both together do not, the");
        Serial.println("# MLX90614 is disturbing the bus — move it to Wire1.");
        ok = false;
    }
    if (ok && !sht4.begin(&Wire)) {
        fail_loudly("SHT41 ACKed but Adafruit_SHT4x::begin() failed");
        ok = false;
    }
    if (ok && !mlx.begin(ADDR_MLX90614, &Wire)) {
        fail_loudly("MLX90614 ACKed but Adafruit_MLX90614::begin() failed");
        ok = false;
    }

    if (ok) {
        sht4.setPrecision(SHT4X_HIGH_PRECISION);
        sht4.setHeater(SHT4X_NO_HEATER); /* the heater would poison the RH */
        sensors_ready = true;
        Serial.println("both sensors ACKed and initialised.");
    }
}

void loop() {
    if (!sensors_ready) {
        Serial.println("halted: sensors did not initialise (see above).");
        delay(5000);
        return;
    }

    sensors_event_t humidity;
    sensors_event_t temp;
    if (!sht4.getEvent(&humidity, &temp)) {
        fail_loudly("SHT41 read failed mid-run");
        delay(SAMPLE_PERIOD_MS);
        return;
    }

    const float t_air_c = temp.temperature;
    const float rh_pct = humidity.relative_humidity;
    const float t_surface_c = (float)mlx.readObjectTempC();

    const physlib::CondensationResult r =
        physlib::condensation_watch(t_air_c, rh_pct, t_surface_c);

    Serial.println("---------------------------------------------");
    Serial.print("  T_air         : ");
    Serial.print(t_air_c, 2);
    Serial.println(" °C   (SHT41)");
    Serial.print("  RH            : ");
    Serial.print(rh_pct, 2);
    Serial.println(" %    (SHT41)");
    Serial.print("  T_surface     : ");
    Serial.print(t_surface_c, 2);
    Serial.println(" °C   (MLX90614)");

    if (physlib::is_valid(r.t_dew_c)) {
        Serial.print("  T_dew         : ");
        Serial.print(r.t_dew_c, 2);
        Serial.println(" °C   (Magnus)");
    } else {
        Serial.println("  T_dew         : INVALID");
    }

    if (r.margin.valid) {
        Serial.print("  ΔT margin     : ");
        Serial.print(r.margin.value, 2);
        Serial.print(" ");
        Serial.println(r.margin.units);
        Serial.print("  condensation  : ");
        Serial.println(r.risk ? "RISK (ΔT < 1.5 K)" : "clear");
    } else {
        Serial.print("  ΔT margin     : INVALID — ");
        Serial.println(r.margin.invalid_reason);
        Serial.println("  condensation  : unknown (refusing to guess)");
    }

    print_confound(r.margin);
    delay(SAMPLE_PERIOD_MS);
}
