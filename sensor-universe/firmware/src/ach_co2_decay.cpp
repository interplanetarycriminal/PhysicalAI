/*
 * ach_co2_decay.cpp
 *
 * Fusion edge key : ach-co2-decay        ("CO2-decay ventilation meter")
 * Pattern         : temporal
 * Requires        : co2-concentration x1
 * Provides        : air-changes-hour  (EMERGENT — no catalog sensor claims it)
 * Atlas source    : sensor-universe/data/fusion.py, FUSION_EDGES
 *
 * math (verbatim from fusion.py):
 *   "ACH = ln((C₁−C_out)/(C₂−C_out)) / Δt[h], C_out ≈ 420 ppm, after the room
 *    empties"
 *
 * confound (verbatim from fusion.py):
 *   "Anyone re-entering mid-decay corrupts the fit (gate on presence);
 *    wind-driven infiltration makes ACH weather-dependent, so log the fits
 *    against wind and you get the infiltration curve as a bonus."
 *
 * example (verbatim from fusion.py):
 *   "One SCD41 and an empty meeting room: rate every room in the house in a
 *    weekend — Derived Quantities row 47, computed."
 *
 * ---------------------------------------------------------------------------
 * WIRING — 3V3, and budget the current. The SCD41 draws ~205 mA peaks during a
 * measurement. On a devkit whose 3V3 comes from an AMS1117 off USB-5V, put
 * 100 uF of bulk capacitance at the SCD41's VDD pin, or a measurement that
 * coincides with a Wi-Fi transmit will brown out the ESP32. A regulated
 * Qwiic/STEMMA breakout (Adafruit 5190, SparkFun Qwiic SCD41) accepts 3-5 V and
 * may instead be fed from the board's 5V/VUSB pin, keeping the peak off the
 * LDO. Pick one and be deliberate about it.
 * ---------------------------------------------------------------------------
 *
 * ESP32-S3 devkit (DevKitC-1 class)
 *   signal | S3 pin | SCD41 (0x62)
 *   -------+--------+---------------------
 *   SDA    | GPIO8  | SDA
 *   SCL    | GPIO9  | SCL
 *   3V3    | 3V3    | VDD  (+100 uF bulk)
 *   GND    | GND    | GND
 *   addr   | —      | fixed 0x62
 *
 * Classic ESP32 devkit (WROOM-32)
 *   signal | ESP32 pin | SCD41 (0x62)
 *   -------+-----------+---------------------
 *   SDA    | GPIO21    | SDA
 *   SCL    | GPIO22    | SCL
 *   3V3    | 3V3       | VDD  (+100 uF bulk)
 *   GND    | GND       | GND
 *   addr   | —         | fixed 0x62
 *
 * Bus runs at 100 kHz.
 *
 * The SCD41's own catalog record requires the ambient-pressure (or altitude)
 * register to be set at boot. With only this edge built there is no barometer,
 * so AMBIENT_PRESSURE_PA below is a constant you must set for your site.
 * Building the air-density-live edge alongside gives you the honest number
 * from the BME280 — that is the reason the atlas wants these three edges on
 * one bus.
 *
 * NOTHING IN THIS FILE HAS BEEN RUN ON HARDWARE. See ../README.md.
 */

#include <Arduino.h>
#include <Wire.h>

#include <SensirionI2cScd4x.h>

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

#define ADDR_SCD41 SCD41_I2C_ADDR_62 /* 0x62, fixed */

/** Site ambient pressure in Pa. Replace with your own, or feed it from a
 *  BME280 (see the air-density-live edge). 101325 Pa = sea level standard. */
#define AMBIENT_PRESSURE_PA 101325UL

/** The SCD41 in periodic mode produces one sample every 5 s. */
#define SAMPLE_PERIOD_MS 5000UL

/** Length of one decay window, seconds. 1200 s = 20 min = 0.333 h, comfortably
 *  above physlib::ACH_MIN_FIT_WINDOW_H (0.25 h). Shorten it and physlib will
 *  correctly flag the fit as too short — that is the detector working. */
#define ACH_WINDOW_SECONDS 1200UL

static SensirionI2cScd4x scd4x;
static bool sensor_ready = false;

/* Decay-window state */
static bool window_open = false;
static float c1_ppm = 0.0f;
static unsigned long window_start_ms = 0;

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
    Serial.println("# Check: 3V3, common GND, SDA/SCL not swapped, 100 uF at");
    Serial.println("# the SCD41's VDD, <30 cm of wire.");
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
    Serial.println("=== fusion edge: ach-co2-decay ===");
    Serial.println("provides: air-changes-hour (EMERGENT)");
    Serial.print("board: ");
    Serial.print(BOARD_NAME);
    Serial.print("  SDA=GPIO");
    Serial.print(PIN_I2C_SDA);
    Serial.print("  SCL=GPIO");
    Serial.print(PIN_I2C_SCL);
    Serial.println("  bus=100 kHz");

    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, I2C_HZ);

    if (!i2c_acks(ADDR_SCD41)) {
        fail_loudly("no ACK from the SCD41 at 0x62");
        return;
    }

    scd4x.begin(Wire, ADDR_SCD41);

    /* A sensor left in periodic mode across a reset ignores configuration
     * commands, so stop first and ignore the error if it was already idle. */
    (void)scd4x.stopPeriodicMeasurement();
    delay(500);

    uint64_t serial_no = 0;
    if (scd4x.getSerialNumber(serial_no) != 0) {
        fail_loudly("SCD41 ACKed but getSerialNumber() failed");
        return;
    }

    /* The record's `requires` field: set the ambient-pressure register at
     * boot, or the ppm figure drifts with the weather. */
    if (scd4x.setAmbientPressure(AMBIENT_PRESSURE_PA) != 0) {
        fail_loudly("setAmbientPressure() failed");
        return;
    }

    if (scd4x.startPeriodicMeasurement() != 0) {
        fail_loudly("startPeriodicMeasurement() failed");
        return;
    }

    sensor_ready = true;
    Serial.print("SCD41 ready. Ambient pressure register set to ");
    Serial.print((unsigned long)AMBIENT_PRESSURE_PA);
    Serial.println(" Pa.");
    Serial.print("Decay window: ");
    Serial.print((unsigned long)ACH_WINDOW_SECONDS);
    Serial.println(" s. Leave the room empty for the whole window.");
}

void loop() {
    if (!sensor_ready) {
        Serial.println("halted: SCD41 did not initialise (see above).");
        delay(5000);
        return;
    }

    bool data_ready = false;
    if (scd4x.getDataReadyStatus(data_ready) != 0 || !data_ready) {
        delay(500);
        return;
    }

    uint16_t co2_ppm_raw = 0;
    float t_c = 0.0f;
    float rh_pct = 0.0f;
    if (scd4x.readMeasurement(co2_ppm_raw, t_c, rh_pct) != 0) {
        fail_loudly("readMeasurement() failed mid-run");
        delay(SAMPLE_PERIOD_MS);
        return;
    }
    if (co2_ppm_raw == 0) {
        /* The SCD4x reports 0 ppm for an invalid sample. */
        Serial.println("sample invalid (0 ppm) — skipping.");
        delay(SAMPLE_PERIOD_MS);
        return;
    }

    const float co2_ppm = (float)co2_ppm_raw;
    const unsigned long now_ms = millis();

    if (!window_open) {
        window_open = true;
        c1_ppm = co2_ppm;
        window_start_ms = now_ms;
        Serial.println("---------------------------------------------");
        Serial.print("window opened at C1 = ");
        Serial.print(c1_ppm, 0);
        Serial.println(" ppm");
        delay(SAMPLE_PERIOD_MS);
        return;
    }

    const unsigned long elapsed_ms = now_ms - window_start_ms;
    Serial.print("  CO2 ");
    Serial.print(co2_ppm, 0);
    Serial.print(" ppm   T ");
    Serial.print(t_c, 1);
    Serial.print(" °C   RH ");
    Serial.print(rh_pct, 0);
    Serial.print(" %   t+");
    Serial.print(elapsed_ms / 1000UL);
    Serial.println(" s");

    if (elapsed_ms < ACH_WINDOW_SECONDS * 1000UL) {
        delay(SAMPLE_PERIOD_MS);
        return;
    }

    const float dt_hours = (float)elapsed_ms / 3600000.0f;
    const physlib::AchResult r = physlib::ach_co2_decay(
        c1_ppm, co2_ppm, dt_hours, physlib::CO2_OUTDOOR_DEFAULT_PPM);

    Serial.println("=============================================");
    Serial.print("  C1            : ");
    Serial.print(r.c1_ppm, 0);
    Serial.println(" ppm");
    Serial.print("  C2            : ");
    Serial.print(r.c2_ppm, 0);
    Serial.println(" ppm");
    Serial.print("  C_out         : ");
    Serial.print(r.c_out_ppm, 0);
    Serial.println(" ppm (atlas default)");
    Serial.print("  Δt            : ");
    Serial.print(r.dt_hours, 4);
    Serial.println(" h");

    if (r.ach.valid) {
        Serial.print("  ACH           : ");
        Serial.print(r.ach.value, 3);
        Serial.print(" ");
        Serial.println(r.ach.units);
    } else {
        Serial.print("  ACH           : INVALID — ");
        Serial.println(r.ach.invalid_reason);
    }
    print_confound(r.ach);

    /* Start the next window from this sample. */
    window_open = false;
    delay(SAMPLE_PERIOD_MS);
}
