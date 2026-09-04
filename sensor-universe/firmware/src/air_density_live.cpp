/*
 * air_density_live.cpp
 *
 * Fusion edge key : air-density-live        ("Live air-density computer")
 * Pattern         : compensation
 * Requires        : pressure-absolute x1, temperature-contact x1,
 *                   humidity-relative x1   (one BME280 covers all three)
 * Provides        : air-density  (EMERGENT — no catalog sensor claims it)
 * Atlas source    : sensor-universe/data/fusion.py, FUSION_EDGES
 *
 * math (verbatim from fusion.py):
 *   "ρ = (P_dry·M_d + P_vap·M_v)/(R·T); P_vap from RH × saturation pressure
 *    (Magnus)"
 *
 * confound (verbatim from fusion.py):
 *   "Sensor self-heating biases T by up to 1°C on combo boards (BME280's known
 *    flaw) — read fast, sleep long, or mount the thermometer separately."
 *
 * example (verbatim from fusion.py):
 *   "One BME280 = drone payload margin on a hot day, carburettor tuning truth,
 *    and the correction every anemometer in this catalog silently needs."
 *
 * ---------------------------------------------------------------------------
 * WIRING — 3V3 only. The BME280 runs 1.7-3.6 V; bare modules without a
 * regulator die on 5V.
 * ---------------------------------------------------------------------------
 *
 * ESP32-S3 devkit (DevKitC-1 class)
 *   signal | S3 pin | BME280 (0x76)
 *   -------+--------+-----------------------
 *   SDA    | GPIO8  | SDA / SDI
 *   SCL    | GPIO9  | SCL / SCK
 *   3V3    | 3V3    | VIN / VCC
 *   GND    | GND    | GND
 *   addr   | —      | SDO → GND ⇒ 0x76
 *
 * Classic ESP32 devkit (WROOM-32)
 *   signal | ESP32 pin | BME280 (0x76)
 *   -------+-----------+-----------------------
 *   SDA    | GPIO21    | SDA / SDI
 *   SCL    | GPIO22    | SCL / SCK
 *   3V3    | 3V3       | VIN / VCC
 *   GND    | GND       | GND
 *   addr   | —         | SDO → GND ⇒ 0x76
 *
 * Bus runs at 100 kHz. GY-BME280 modules default to 0x76; Adafruit boards
 * default to 0x77 — change ADDR_BME280 below if you have one of those.
 *
 * MANDATORY BRING-UP CHECK, from the catalog record's `fools` field:
 *   "A substantial fraction of $2 'BME280' boards carry a BMP280 die and
 *    report a fixed or zero humidity — read chip ID 0x60 or you are debugging
 *    a sensor that physically cannot do what you asked."
 * This firmware reads the chip ID and refuses to compute ρ on a 0x58 (BMP280).
 *
 * NOTHING IN THIS FILE HAS BEEN RUN ON HARDWARE. See ../README.md.
 */

#include <Arduino.h>
#include <Wire.h>

#include <Adafruit_BME280.h>

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

#define I2C_HZ 100000 /* 100 kHz */

#define ADDR_BME280 0x76 /* SDO → GND. Adafruit breakouts are 0x77. */

#define CHIP_ID_BME280 0x60 /* real BME280: has a humidity element    */
#define CHIP_ID_BMP280 0x58 /* BMP280 die: no humidity, cannot do this */

/** Read fast, sleep long — the confound's own remedy. */
#define SAMPLE_PERIOD_MS 30000UL

static Adafruit_BME280 bme;
static bool sensor_ready = false;

/** Cold-start temperature, captured on the first forced read after power-up
 *  before the board has had time to warm itself. It stands in for the
 *  "thermometer mounted separately" that the confound actually asks for: if
 *  the BME280's channel later sits more than 1 K above it, that drift is far
 *  more likely self-heating than the room warming. Honest limitation: a real
 *  ambient rise trips it too — put an SHT41 on a flying lead (the
 *  condensation-watch edge already has one) and pass its temperature here
 *  instead if you want the strict version. */
static float t_reference_c = PHYSLIB_INVALID;

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
    Serial.println("# SDO strapped for the address you configured.");
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
    Serial.println("=== fusion edge: air-density-live ===");
    Serial.println("provides: air-density (EMERGENT)");
    Serial.print("board: ");
    Serial.print(BOARD_NAME);
    Serial.print("  SDA=GPIO");
    Serial.print(PIN_I2C_SDA);
    Serial.print("  SCL=GPIO");
    Serial.print(PIN_I2C_SCL);
    Serial.println("  bus=100 kHz");

    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, I2C_HZ);

    if (!i2c_acks(ADDR_BME280)) {
        fail_loudly("no ACK from the BME280 at 0x76");
        Serial.println("# Many breakouts sit at 0x77 instead — try that.");
        return;
    }

    if (!bme.begin(ADDR_BME280, &Wire)) {
        fail_loudly("device ACKed but Adafruit_BME280::begin() failed");
        return;
    }

    const uint32_t chip_id = bme.sensorID();
    Serial.print("chip ID: 0x");
    Serial.println(chip_id, HEX);
    if (chip_id != CHIP_ID_BME280) {
        fail_loudly("this is not a BME280");
        if (chip_id == CHIP_ID_BMP280) {
            Serial.println("# Chip ID 0x58 = BMP280: no humidity element. This");
            Serial.println("# edge needs RH and the part physically has none.");
        }
        Serial.println("# Refusing to compute ρ from a fabricated humidity.");
        return;
    }

    /* Forced mode: one conversion on demand, then sleep. Filter off so a
     * single reading is a single reading, not an IIR tail. */
    bme.setSampling(Adafruit_BME280::MODE_FORCED, Adafruit_BME280::SAMPLING_X1,
                    Adafruit_BME280::SAMPLING_X1, Adafruit_BME280::SAMPLING_X1,
                    Adafruit_BME280::FILTER_OFF);

    if (bme.takeForcedMeasurement()) {
        t_reference_c = bme.readTemperature();
        Serial.print("cold-start reference temperature: ");
        Serial.print(t_reference_c, 2);
        Serial.println(" °C");
    }

    sensor_ready = true;
    Serial.println("BME280 ready (forced mode, read fast / sleep long).");
}

void loop() {
    if (!sensor_ready) {
        Serial.println("halted: BME280 did not initialise (see above).");
        delay(5000);
        return;
    }

    if (!bme.takeForcedMeasurement()) {
        fail_loudly("takeForcedMeasurement() failed mid-run");
        delay(SAMPLE_PERIOD_MS);
        return;
    }

    const float t_c = bme.readTemperature();
    const float p_pa = bme.readPressure();
    const float rh_pct = bme.readHumidity();

    const physlib::AirDensityResult r =
        physlib::air_density_live(p_pa, t_c, rh_pct, t_reference_c);

    Serial.println("---------------------------------------------");
    Serial.print("  P             : ");
    Serial.print(p_pa, 1);
    Serial.println(" Pa");
    Serial.print("  T             : ");
    Serial.print(t_c, 2);
    Serial.println(" °C");
    Serial.print("  RH            : ");
    Serial.print(rh_pct, 2);
    Serial.println(" %");

    if (r.rho.valid) {
        Serial.print("  P_vap         : ");
        Serial.print(r.p_vap_pa, 1);
        Serial.println(" Pa   (Magnus)");
        Serial.print("  P_dry         : ");
        Serial.print(r.p_dry_pa, 1);
        Serial.println(" Pa");
        Serial.print("  ρ air density : ");
        Serial.print(r.rho.value, 4);
        Serial.print(" ");
        Serial.println(r.rho.units);
    } else {
        Serial.print("  ρ air density : INVALID — ");
        Serial.println(r.rho.invalid_reason);
    }

    print_confound(r.rho);
    delay(SAMPLE_PERIOD_MS);
}
