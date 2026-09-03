"""Authored ESP32 interface fields, keyed by stable part ID.

GENERATED FILE — do not hand-edit. `tools/gen_enrich_iface.py` builds it from
the authored `iface_data_*.json` files and rewrites it wholesale; anything typed
in here by hand is lost on the next run. Edit the JSON, then regenerate.

This is the fourth and last overlay the loader merges, so a value here beats
`enrich_core`, `enrich`, `enrich_manual` and every derivation in
`data/iface_derive.py`. Author only what you have checked against a datasheet or
a real driver; leave the rest out and let the derivation (or an explicit None)
stand. An explicit None here means "checked, could not verify".
"""

ENRICH_IFACE: dict[str, dict] = {
"S001": {
    "i_peak_ua": 1500.0,
    "esp32_driver": "OneWire + DallasTemperature (Arduino-ESP32); ESP-IDF onewire_bus "
                    "component (RMT-backed); ESPHome dallas_temp",
    "driver_status": "Verified",
},
"S002": {
    "esp32_driver": "Adafruit_TMP117 (Arduino-ESP32); SparkFun_TMP117_Arduino_Library",
    "driver_status": "Verified",
},
"S003": {
    "esp32_driver": "Adafruit_MCP9808 (Arduino-ESP32); ESPHome mcp9808",
    "driver_status": "Verified",
},
"S004": {
    "esp32_driver": "Adafruit_MAX31855 (Arduino-ESP32); ESPHome max31855",
    "driver_status": "Verified",
},
"S005": {
    "esp32_driver": "Adafruit_MAX31865 (Arduino-ESP32); ESPHome max31865",
    "driver_status": "Verified",
},
"S006": {
    "esp32_driver": "ESP-IDF adc_oneshot / Arduino-ESP32 analogRead + Steinhart-Hart math (no "
                    "driver needed); ESPHome adc + ntc",
    "driver_status": "Generic",
},
"S007": {
    "esp32_driver": "Adafruit_MLX90614 (Arduino-ESP32); ESPHome mlx90614",
    "driver_status": "Verified",
},
"S008": {
    "esp32_driver": "SparkFun_MLX90632_Arduino_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S009": {
    "esp32_driver": "ESP-IDF adc_oneshot / analogRead + linear scaling (no driver needed); "
                    "ESPHome adc",
    "driver_status": "Generic",
},
"S010": {
    "esp32_driver": "Adafruit_MCP9600 (Arduino-ESP32); ESPHome mcp9600",
    "driver_status": "Verified",
},
"S011": {
    "esp32_driver": "Adafruit DHT sensor library (Arduino-ESP32); ESPHome dht",
    "driver_status": "Verified",
},
"S012": {
    "esp32_driver": "Adafruit_SHT4x (Arduino-ESP32); Sensirion arduino-i2c-sht4x; ESPHome "
                    "sht4x",
    "driver_status": "Verified",
},
"S013": {
    "esp32_driver": "Adafruit_BME280 (Arduino-ESP32); ESPHome bme280_i2c",
    "driver_status": "Verified",
},
"S014": {
    "esp32_driver": "Adafruit_HDC302x (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S015": {
    "esp32_driver": "Adafruit_SHT31 (Arduino-ESP32); ESPHome sht3xd",
    "driver_status": "Verified",
},
"S016": {
    "esp32_driver": "Adafruit_BMP3XX (Arduino-ESP32); ESPHome bmp3xx",
    "driver_status": "Verified",
},
"S017": {
    "esp32_driver": "Adafruit_DPS310 (Arduino-ESP32); ESPHome dps310",
    "driver_status": "Verified",
},
"S018": {
    "esp32_driver": "RobTillaart/MS5611 (Arduino-ESP32); ESPHome ms5611",
    "driver_status": "Verified",
},
"S019": {
    "esp32_driver": "Adafruit_LPS2X (Arduino-ESP32); SparkFun_LPS28DFW_Arduino_Library",
    "driver_status": "Verified",
},
"S020": {
    "esp32_driver": "Sensirion arduino-i2c-sdp (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S021": {
    "esp32_driver": "Adafruit_MPRLS (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S022": {
    "esp32_driver": "fanfanlatulipe26/XGZP6897D (Arduino-ESP32); stickbreaker/XGZP_6867 is an "
                    "ESP32-specific alternative",
    "driver_status": "Verified",
},
"S023": {
    "esp32_driver": "Bosch BSEC2 Arduino library (Arduino-ESP32, pre-compiled blob per core); "
                    "Adafruit_BME680 for raw mode; ESPHome bme68x_bsec2_i2c",
    "driver_status": "Verified",
},
"S024": {
    "esp32_driver": "Adafruit_SGP40 (Arduino-ESP32) + Sensirion Gas Index Algorithm; ESPHome "
                    "sgp4x",
    "driver_status": "Verified",
},
"S025": {
    "i_peak_ua": 29000.0,
    "esp32_driver": "sciosense/ENS160_driver (Arduino-ESP32); ESPHome ens160_i2c",
    "driver_status": "Verified",
},
"S026": {
    "level_shift": "Divider",
    "i_peak_ua": 150000.0,
    "esp32_driver": "ESP-IDF adc_oneshot / analogRead (no driver needed); MQUnifiedsensor for "
                    "the ppm curve fit",
    "driver_status": "Generic",
},
"S027": {
    "level_shift": "Divider",
    "i_peak_ua": 150000.0,
    "esp32_driver": "ESP-IDF adc_oneshot / analogRead (no driver needed); MQUnifiedsensor for "
                    "the ppm curve fit",
    "driver_status": "Generic",
},
"S028": {
    "level_shift": "Divider",
    "i_peak_ua": 150000.0,
    "esp32_driver": "LEDC PWM for the heater cycle + ESP-IDF adc_oneshot (no driver needed); "
                    "MQUnifiedsensor for the ppm curve fit",
    "driver_status": "Generic",
},
"S029": {
    "level_shift": "Divider",
    "i_peak_ua": 150000.0,
    "esp32_driver": "ESP-IDF adc_oneshot / analogRead (no driver needed); MQUnifiedsensor for "
                    "the ppm curve fit",
    "driver_status": "Generic",
},
"S030": {
    "i_peak_ua": 32000.0,
    "esp32_driver": "ESP-IDF adc_oneshot / analogRead + GPIO-driven EN pin for heater "
                    "duty-cycling (no driver needed)",
    "driver_status": "Generic",
},
"S031": {
    "esp32_driver": "eNBeWe/MiCS6814-I2C-Library (Arduino-ESP32) for the Grove/DFRobot "
                    "I2C-bridged module; the bare analog part is three ADC channels with no "
                    "driver",
    "driver_status": "Community",
},
"S032": {
    "i_peak_ua": 48000.0,
    "esp32_driver": "Adafruit_SGP30 (Arduino-ESP32); ESPHome sgp30",
    "driver_status": "Verified",
},
"S033": {
    "level_shift": "Analog-front-end",
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S034": {
    "esp32_driver": "DFRobot/DFRobotHCHOSensor (Arduino-ESP32) for the ZE08-CH2O-based "
                    "Gravity SEN0231; otherwise a plain UART frame parse",
    "driver_status": "Community",
},
"S035": {
    "i_peak_ua": 60000.0,
    "esp32_driver": "ESP-IDF uart_driver / HardwareSerial frame parse per the Winsen "
                    "datasheet (no library needed)",
    "driver_status": "Generic",
},
"S036": {
    "i_peak_ua": 205000.0,
    "esp32_driver": "Sensirion arduino-i2c-scd4x (Arduino-ESP32); Adafruit_SCD4x; ESPHome "
                    "scd4x",
    "driver_status": "Verified",
},
"S037": {
    "i_peak_ua": 75000.0,
    "esp32_driver": "Adafruit_SCD30 (Arduino-ESP32); Sensirion arduino-i2c-scd30; ESPHome "
                    "scd30",
    "driver_status": "Verified",
},
"S038": {
    "i_peak_ua": 150000.0,
    "esp32_driver": "WifWaf/MH-Z19 (Arduino-ESP32); ESPHome mhz19",
    "driver_status": "Verified",
},
"S039": {
    "i_peak_ua": 300000.0,
    "esp32_driver": "jcomas/S8_UART (Arduino-ESP32); ESPHome senseair",
    "driver_status": "Verified",
},
"S040": {
    "i_peak_ua": 100000.0,
    "esp32_driver": "Adafruit_PM25AQI (Arduino-ESP32, covers both PMS5003 UART and PMSA003I "
                    "I2C); ESPHome pmsx003",
    "driver_status": "Verified",
},
"S041": {
    "i_peak_ua": 80000.0,
    "esp32_driver": "Sensirion arduino-sps / paulvha SPS30 (Arduino-ESP32); ESPHome sps30",
    "driver_status": "Verified",
},
"S042": {
    "i_peak_ua": 220000.0,
    "esp32_driver": "nettigo/esp_sds011 (Arduino-ESP32, written specifically for "
                    "ESP8266/ESP32); ESPHome sds011",
    "driver_status": "Verified",
},
"S043": {
    "esp32_driver": "ESPHome pm1006 component (RX-only UART); Arduino-ESP32: a 20-byte UART "
                    "frame parse, no library needed",
    "driver_status": "Verified",
},
"S044": {
    "esp32_driver": "claws/BH1750 (Arduino-ESP32); ESPHome bh1750",
    "driver_status": "Verified",
},
"S045": {
    "esp32_driver": "Adafruit_VEML7700 (Arduino-ESP32); ESPHome veml7700",
    "driver_status": "Verified",
},
"S046": {
    "esp32_driver": "Adafruit_LTR390 (Arduino-ESP32); ESPHome ltr390",
    "driver_status": "Verified",
},
"S047": {
    "esp32_driver": "ESP-IDF adc_oneshot / analogRead + slope (no driver needed); ESPHome adc",
    "driver_status": "Generic",
},
"S048": {
    "esp32_driver": "Adafruit_TSL2591 (Arduino-ESP32); ESPHome tsl2591",
    "driver_status": "Verified",
},
"S049": {
    "esp32_driver": "ESP-IDF adc_oneshot / analogRead on a divider (no driver needed); "
                    "ESPHome adc + resistance",
    "driver_status": "Generic",
},
"S050": {
    "esp32_driver": "SparkFun_AS7331_Arduino_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S051": {
    "esp32_driver": "Adafruit_TCS34725 (Arduino-ESP32); ESPHome tcs34725",
    "driver_status": "Verified",
},
"S052": {
    "esp32_driver": "Adafruit_AS7341 (Arduino-ESP32); ESPHome as7341",
    "driver_status": "Verified",
},
"S053": {
    "addr_mode": "Fixed",
    "esp32_driver": "SparkFun_AS726X_Arduino_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S054": {
    "esp32_driver": "Adafruit_APDS9960 (Arduino-ESP32); ESPHome apds9960",
    "driver_status": "Verified",
},
"S055": {
    "esp32_driver": "SparkFun_OPT4048_Arduino_Library (Arduino-ESP32); Adafruit_OPT4048",
    "driver_status": "Verified",
},
"S056": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF RMT or MCPWM capture for the echo pulse (no driver needed); "
                    "ESPHome ultrasonic",
    "driver_status": "Generic",
},
"S057": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF uart_driver in auto-report mode, or RMT pulse capture (no driver "
                    "needed); ESPHome ultrasonic",
    "driver_status": "Generic",
},
"S058": {
    "esp32_driver": "Adafruit_VL53L0X or Pololu VL53L0X (Arduino-ESP32); ESPHome vl53l0x",
    "driver_status": "Verified",
},
"S059": {
    "esp32_driver": "SparkFun_VL53L1X_Arduino_Library or Pololu VL53L1X (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S060": {
    "i_peak_ua": 70000.0,
    "esp32_driver": "SparkFun_VL53L5CX_Arduino_Library (wraps ST's ULD API) (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S061": {
    "esp32_driver": "budryerson/TFLuna-I2C (TFLI2C) (Arduino-ESP32); budryerson/TFLuna-Serial "
                    "for the default UART mode",
    "driver_status": "Verified",
},
"S062": {
    "i_peak_ua": 300000.0,
    "esp32_driver": "pschatzmann/LDROBOT-LIDAR-STL (Arduino-ESP32); LDROBOT's own "
                    "ldlidar_stl_sdk is Linux/ROS-targeted, not an ESP32 port",
    "driver_status": "Community",
},
"S063": {
    "level_shift": "Divider",
    "i_peak_ua": 50000.0,
    "esp32_driver": "ESP-IDF adc_oneshot / analogRead + inverse-distance lookup table (no "
                    "driver needed)",
    "driver_status": "Generic",
},
"S064": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF uart_driver / HardwareSerial 4-byte frame parse (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S065": {
    "esp32_driver": "GPIO input + ext0/ext1 deep-sleep wake (no driver needed); ESPHome gpio "
                    "binary_sensor",
    "driver_status": "Generic",
},
"S066": {
    "esp32_driver": "GPIO input + ext0/ext1 deep-sleep wake (no driver needed); ESPHome gpio "
                    "binary_sensor",
    "driver_status": "Generic",
},
"S067": {
    "esp32_driver": "iavorvel/MyLD2410 (Arduino-ESP32, explicitly an Arduino/ESP32 library); "
                    "ESPHome ld2410",
    "driver_status": "Verified",
},
"S068": {
    "esp32_driver": "ESPHome ld2450 component; Arduino-ESP32: community HLK-LD2450 frame "
                    "parsers",
    "driver_status": "Verified",
},
"S069": {
    "esp32_driver": "Love4yzp/Seeed-mmWave-library (Arduino-ESP32); "
                    "limengdu/MR60BHA2_ESPHome_external_components for ESPHome",
    "driver_status": "Verified",
},
"S070": {
    "esp32_driver": "GPIO input + interrupt (no driver needed); ESPHome gpio binary_sensor",
    "driver_status": "Generic",
},
"S071": {
    "esp32_driver": "Adafruit_AMG88xx (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S072": {
    "esp32_driver": "Adafruit_MPU6050 (Arduino-ESP32); jrowberg i2cdevlib MPU6050 for the "
                    "DMP; ESPHome mpu6050",
    "driver_status": "Verified",
},
"S073": {
    "esp32_driver": "Adafruit_LSM6DS (Arduino-ESP32); STM32duino LSM6DSOX for the MLC examples",
    "driver_status": "Verified",
},
"S074": {
    "esp32_driver": "Adafruit_BNO055 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S075": {
    "esp32_driver": "SparkFun_BNO08x_Arduino_Library (Arduino-ESP32); Adafruit_BNO08x",
    "driver_status": "Verified",
},
"S076": {
    "esp32_driver": "Adafruit_ADXL345 (Arduino-ESP32); SparkFun_ADXL345_Arduino_Library",
    "driver_status": "Verified",
},
"S077": {
    "esp32_driver": "plasmapper/adxl355-arduino (PL_ADXL355) (Arduino-ESP32) — a small "
                    "single-maintainer library; no vendor or Adafruit driver exists",
    "driver_status": "Community",
},
"S078": {
    "esp32_driver": "Adafruit_LIS3DH (Arduino-ESP32); SparkFun LIS3DH "
                    "(SparkFun_LIS3DH_Arduino_Library)",
    "driver_status": "Verified",
},
"S079": {
    "esp32_driver": "SparkFun_ICM-20948_ArduinoLibrary (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S080": {
    "esp32_driver": "Adafruit_ADXL375 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S081": {
    "esp32_driver": "mprograms/QMC5883LCompass (Arduino-ESP32); ESPHome qmc5883l",
    "driver_status": "Verified",
},
"S082": {
    "esp32_driver": "Adafruit_MMC56x3 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S083": {
    "esp32_driver": "Infineon/TLV493D-A1B6-3DMagnetic-Sensor (Arduino-ESP32) — the only real "
                    "Arduino driver; Adafruit ships only a CircuitPython version, and the "
                    "Infineon library's non-standard I2C recovery is the weak point on ESP32",
    "driver_status": "Community",
},
"S084": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF PCNT for the A3144 open-collector switch / adc_oneshot for the "
                    "SS49E linear output (no driver needed)",
    "driver_status": "Generic",
},
"S085": {
    "esp32_driver": "GPIO with internal pull-up + ext0/ext1 deep-sleep wake (no driver "
                    "needed); ESPHome gpio binary_sensor",
    "driver_status": "Generic",
},
"S086": {
    "esp32_driver": "Adafruit_MLX90393 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S087": {
    "esp32_driver": "ESP-IDF i2s_std RX (no driver needed); arduino-audio-tools or ESP-SR for "
                    "the DSP/wake-word layer",
    "driver_status": "Generic",
},
"S088": {
    "esp32_driver": "ESP-IDF i2s_std RX (no driver needed); arduino-audio-tools for the DSP "
                    "layer",
    "driver_status": "Generic",
},
"S089": {
    "esp32_driver": "ESP-IDF adc_oneshot / adc_continuous on an ADC1 channel (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S090": {
    "esp32_driver": "ESP-IDF i2s_std RX with 32-bit slots, sample >> 14 (no driver needed)",
    "driver_status": "Generic",
},
"S091": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot / adc_continuous + peak detection (no driver needed)",
    "driver_status": "Generic",
},
"S092": {
    "esp32_driver": "ESP-IDF adc_oneshot with eFuse Vref calibration, dB = V * 50 (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S093": {
    "level_shift": "Analog-front-end",
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S094": {
    "esp32_driver": "ESP-IDF PCNT on the DO output, or GPIO interrupt with debounce (no "
                    "driver needed)",
    "driver_status": "Generic",
},
"S095": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF adc_oneshot on an ADC1 channel (no driver needed)",
    "driver_status": "Generic",
},
"S096": {
    "level_shift": "Analog-front-end",
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S097": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot with clamp diodes on the input (no driver needed)",
    "driver_status": "Generic",
},
"S098": {
    "esp32_driver": "bogde/HX711 (Arduino-ESP32); ESPHome hx711",
    "driver_status": "Verified",
},
"S099": {
    "esp32_driver": "ESP-IDF adc_oneshot on an ADC1 divider (no driver needed); ESPHome adc + "
                    "resistance",
    "driver_status": "Generic",
},
"S100": {
    "esp32_driver": "ESP-IDF adc_oneshot behind a CD74HC4067 row/column mux driven from GPIOs "
                    "(no driver needed)",
    "driver_status": "Generic",
},
"S101": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "bogde/HX711 (Arduino-ESP32); ESPHome hx711 — the HX711 or an INA125 is "
                    "the required bridge amplifier",
    "driver_status": "Verified",
},
"S102": {
    "esp32_driver": "SparkFun_Qwiic_Scale_NAU7802_Arduino_Library (Arduino-ESP32); ESPHome "
                    "nau7802",
    "driver_status": "Verified",
},
"S103": {
    "esp32_driver": "Protocentral/ProtoCentral_fdc1004_breakout (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S104": {
    "esp32_driver": "Adafruit_MPR121 (Arduino-ESP32); ESPHome mpr121",
    "driver_status": "Verified",
},
"S105": {
    "esp32_driver": "GPIO input + ext0 deep-sleep wake (no driver needed); ESPHome gpio "
                    "binary_sensor",
    "driver_status": "Generic",
},
"S106": {
    "esp32_driver": "Arduino-ESP32 touchRead()/touchAttachInterrupt(); ESP-IDF touch_sensor / "
                    "touch_element (built-in peripheral, no driver needed) — absent on "
                    "C3/C6/H2",
    "driver_status": "Generic",
},
"S107": {
    "esp32_driver": "BelaPlatform/Trill-Arduino (Arduino-ESP32); jakkra/Trill-esp-idf "
                    "(ESP-IDF)",
    "driver_status": "Verified",
},
"S108": {
    "level_shift": "Divider",
    "esp32_driver": "GPIO input behind level translation + ext0 deep-sleep wake (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S109": {
    "esp32_driver": "ESP-IDF adc_oneshot on an ADC1 divider, op-amp buffered for the 25k-125k "
                    "source impedance (no driver needed)",
    "driver_status": "Generic",
},
"S110": {
    "esp32_driver": "ESP-IDF adc_oneshot on a GPIO-gated divider (no driver needed)",
    "driver_status": "Generic",
},
"S111": {
    "esp32_driver": "SparkFun_Displacement_Sensor_Arduino_Library (Arduino-ESP32) — the Bend "
                    "Labs ADS driver",
    "driver_status": "Verified",
},
"S112": {
    "i_peak_ua": 50000.0,
    "esp32_driver": "SparkFun_MAX3010x_Sensor_Library (Arduino-ESP32); ProtoCentral MAX30102 "
                    "as an alternative; ESPHome max30102 external component",
    "driver_status": "Verified",
},
"S113": {
    "esp32_driver": "ESP-IDF adc_oneshot / adc_continuous at 250Hz+ on ADC1, or an external "
                    "ADS1115 (no driver needed — the AD8232 is itself the front end)",
    "driver_status": "Generic",
},
"S114": {
    "esp32_driver": "Protocentral/Protocentral_MAX30205 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S115": {
    "esp32_driver": "ESP-IDF adc_oneshot / adc_continuous on ADC1 for the envelope output (no "
                    "driver needed)",
    "driver_status": "Generic",
},
"S116": {
    "esp32_driver": "ESP-IDF adc_oneshot with heavy averaging (no driver needed)",
    "driver_status": "Generic",
},
"S117": {
    "esp32_driver": "Adafruit_MLX90614 (Arduino-ESP32); ESPHome mlx90614",
    "driver_status": "Verified",
},
"S118": {
    "esp32_driver": "WorldFamousElectronics/PulseSensorPlayground (Arduino-ESP32) — ESP32 "
                    "timer/interrupt support has been patchy; "
                    "bhawiyuga/PulseSensor_Playground_esp32 is the ESP32 fork people actually "
                    "use",
    "driver_status": "Community",
},
"S119": {
    "esp32_driver": "upsidedownlabs/BioAmp-EXG-Pill Arduino example sketches (Arduino-ESP32) "
                    "— sketches and filter code, not a packaged library",
    "driver_status": "Community",
},
"S120": {
    "esp32_driver": "Adafruit_Fingerprint (Arduino-ESP32); ESPHome fingerprint_grow",
    "driver_status": "Verified",
},
"S121": {
    "esp32_driver": "ESP-IDF PCNT (GPIO interrupt counter on the C3, which has no PCNT) (no "
                    "driver needed); ESPHome pulse_counter / pulse_meter",
    "driver_status": "Generic",
},
"S122": {
    "esp32_driver": "ESP-IDF adc_oneshot + a 16-state resistance lookup table (no driver "
                    "needed); ESPHome adc + resistance",
    "driver_status": "Generic",
},
"S123": {
    "esp32_driver": "GPIO interrupt counter with debounce, or PCNT; ext0 wake for solar nodes "
                    "(no driver needed); ESPHome pulse_counter",
    "driver_status": "Generic",
},
"S124": {
    "esp32_driver": "SparkFun_AS3935_Lightning_Detector_Arduino_Library (Arduino-ESP32); "
                    "ESPHome as3935_i2c / as3935_spi",
    "driver_status": "Verified",
},
"S125": {
    "esp32_driver": "ESP-IDF adc_oneshot + linear slope (no driver needed); ESPHome adc",
    "driver_status": "Generic",
},
"S126": {
    "esp32_driver": "budryerson/TFMini-Plus (Arduino-ESP32) covers the Benewake "
                    "TFmini-Plus/TF02-Pro serial protocol; the TF350 and the CAN variant need "
                    "a hand-written frame parse over uart_driver or TWAI",
    "driver_status": "Community",
},
"S127": {
    "esp32_driver": "ESP-IDF adc_oneshot for the analog version (no driver needed); the "
                    "RS-485 version is ModbusMaster over uart_driver plus a DE/RE GPIO",
    "driver_status": "Generic",
},
"S128": {
    "esp32_driver": "ESP-IDF adc_oneshot (an ADS1115 is worth it here) for the analog version "
                    "(no driver needed); the RS-485 version is ModbusMaster / ESPHome "
                    "modbus_controller",
    "driver_status": "Generic",
},
"S129": {
    "esp32_driver": "ESP-IDF adc_oneshot on ADC1 with the board power-gated from a GPIO (no "
                    "driver needed); ESPHome adc",
    "driver_status": "Generic",
},
"S130": {
    "esp32_driver": "4-20ma/ModbusMaster (Arduino-ESP32); emelianov/modbus-esp8266 also "
                    "supports ESP32; ESPHome modbus_controller",
    "driver_status": "Verified",
},
"S131": {
    "esp32_driver": "Apollon77/I2CSoilMoistureSensor (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S132": {
    "i_peak_ua": 1500.0,
    "esp32_driver": "OneWire + DallasTemperature (Arduino-ESP32); ESP-IDF onewire_bus "
                    "component (RMT-backed); ESPHome dallas_temp",
    "driver_status": "Verified",
},
"S133": {
    "i_peak_ua": 4500.0,
    "esp32_driver": "OneWire + DallasTemperature multi-drop (Arduino-ESP32); ESP-IDF "
                    "onewire_bus component; ESPHome dallas_temp with per-address sensors",
    "driver_status": "Verified",
},
"S134": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "GreenPonik/DFRobot_ESP_PH_BY_GREENPONIK (Arduino-ESP32, an ESP32 port of "
                    "DFRobot_PH with NVS-backed calibration); DFRobot/DFRobot_PH upstream",
    "driver_status": "Verified",
},
"S135": {
    "esp32_driver": "DFRobot/GravityTDS (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S137": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF adc_oneshot / Arduino-ESP32 analogRead (no driver needed)",
    "driver_status": "Generic",
},
"S138": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF PCNT (pulse_cnt) or Arduino-ESP32 attachInterrupt counting (no "
                    "driver needed)",
    "driver_status": "Generic",
},
"S139": {
    "esp32_driver": "Arduino-ESP32 digitalRead with INPUT_PULLUP (no driver needed)",
    "driver_status": "Generic",
},
"S140": {
    "esp32_driver": "ESP-IDF adc_oneshot / Arduino-ESP32 analogRead (no driver needed)",
    "driver_status": "Generic",
},
"S141": {
    "esp32_driver": "ESP-IDF adc_oneshot with GPIO AC/pulsed excitation (no driver needed)",
    "driver_status": "Generic",
},
"S142": {
    "level_shift": "Divider",
    "esp32_driver": "wvmarle/Arduino_DS1603L (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S143": {
    "esp32_driver": "Atlas Scientific Ezo_I2c_lib (Arduino-ESP32); ESPHome ezo",
    "driver_status": "Verified",
},
"S144": {
    "esp32_driver": "Adafruit_INA219 (Arduino-ESP32); ESPHome ina219",
    "driver_status": "Verified",
},
"S145": {
    "esp32_driver": "Adafruit_INA228 and RobTillaart/INA226 (Arduino-ESP32); ESPHome ina2xx",
    "driver_status": "Verified",
},
"S146": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF adc_oneshot / adc_continuous for AC RMS (no driver needed)",
    "driver_status": "Generic",
},
"S147": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "openenergymonitor/EmonLib, ESP32 fork Savjee/EmonLib-esp32 "
                    "(Arduino-ESP32)",
    "driver_status": "Community",
},
"S148": {
    "level_shift": "Divider",
    "esp32_driver": "mandulaj/PZEM-004T-v30 (Arduino-ESP32); ESPHome pzemac",
    "driver_status": "Verified",
},
"S149": {
    "esp32_driver": "openenergymonitor/EmonLib voltage channel, ESP32 fork "
                    "Savjee/EmonLib-esp32 (Arduino-ESP32)",
    "driver_status": "Community",
},
"S150": {
    "esp32_driver": "Adafruit_ADS1X15 (Arduino-ESP32); ESPHome ads1115",
    "driver_status": "Verified",
},
"S151": {
    "esp32_driver": "madhephaestus/ESP32Encoder (Arduino-ESP32, PCNT-backed); ESPHome "
                    "rotary_encoder",
    "driver_status": "Verified",
},
"S152": {
    "addr_mode": "Fixed",
    "esp32_driver": "RobTillaart/AS5600 and SimpleFOC MagneticSensorI2C (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S153": {
    "level_shift": "Divider",
    "esp32_driver": "madhephaestus/ESP32Encoder (Arduino-ESP32, PCNT-backed)",
    "driver_status": "Verified",
},
"S154": {
    "esp32_driver": "ESP-IDF adc_oneshot / Arduino-ESP32 analogRead (no driver needed)",
    "driver_status": "Generic",
},
"S155": {
    "addr_mode": "Programmable",
    "esp32_driver": "Adafruit_VL6180X (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S156": {
    "esp32_driver": "ESP-IDF adc_oneshot / Arduino-ESP32 analogRead (no driver needed)",
    "driver_status": "Generic",
},
"S157": {
    "esp32_driver": "mikalhart/TinyGPSPlus (Arduino-ESP32); ESPHome gps",
    "driver_status": "Verified",
},
"S158": {
    "addr_mode": "Programmable",
    "esp32_driver": "SparkFun u-blox GNSS Arduino Library v3 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S159": {
    "addr_mode": "Programmable",
    "i_peak_ua": 130000.0,
    "esp32_driver": "SparkFun u-blox GNSS Arduino Library v3 plus any NTRIP client "
                    "(Arduino-ESP32)",
    "driver_status": "Verified",
},
"S160": {
    "esp32_driver": "Arduino-ESP32 attachInterrupt on PPS paired with TinyGPSPlus NMEA (no "
                    "dedicated driver)",
    "driver_status": "Generic",
},
"S161": {
    "addr_mode": "Programmable",
    "esp32_driver": "Adafruit_MLX90640 (Arduino-ESP32); Melexis MLX90640 C driver (ESP-IDF)",
    "driver_status": "Verified",
},
"S162": {
    "addr_mode": "Programmable",
    "esp32_driver": "dndubins/MLX90641 (Arduino-ESP32) and the Melexis MLX90641 C driver; "
                    "ESP32 use is community-tested only",
    "driver_status": "Community",
},
"S163": {
    "i_peak_ua": 160000.0,
    "esp32_driver": "NachtRaveVL/Lepton-FLiR-Arduino and groupgets/LeptonModule SDK ports "
                    "(Arduino-ESP32); VoSPI on ESP32 needs DMA care",
    "driver_status": "Community",
},
"S164": {
    "level_shift": "Shifter",
    "addr_mode": "Fixed",
    "esp32_driver": "omron-devhub/d6t-2jcieev01-arduino, Omron's own sample code "
                    "(Arduino-ESP32)",
    "driver_status": "Community",
},
"S165": {
    "i_peak_ua": 180000.0,
    "esp32_driver": "espressif/esp32-camera (ESP-IDF and Arduino-ESP32); ESPHome esp32_camera",
    "driver_status": "Verified",
},
"S166": {
    "i_peak_ua": 200000.0,
    "esp32_driver": "espressif/esp32-camera (ESP-IDF and Arduino-ESP32); ESPHome esp32_camera",
    "driver_status": "Verified",
},
"S167": {
    "addr_mode": "Fixed",
    "esp32_driver": "ESPHome sen21231; Useful Sensors person_sensor Arduino example code "
                    "(Arduino-ESP32)",
    "driver_status": "Verified",
},
"S168": {
    "i_peak_ua": 320000.0,
    "esp32_driver": "HuskyLens/HUSKYLENSArduino (Arduino-ESP32, DFRobot-maintained)",
    "driver_status": "Verified",
},
"S169": {
    "i_peak_ua": 150000.0,
    "esp32_driver": "Seeed-Studio/Seeed_Arduino_SSCMA (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S170": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF PCNT (pulse_cnt) or attachInterrupt counting (no driver needed)",
    "driver_status": "Generic",
},
"S171": {
    "esp32_driver": "ESPHome radon_eye_ble / radon_eye_rd200 (BLE)",
    "driver_status": "Verified",
},
"S172": {
    "esp32_driver": "ESP-IDF adc_oneshot / Arduino-ESP32 analogRead (no driver needed)",
    "driver_status": "Generic",
},
"S173": {
    "i_peak_ua": 34000.0,
    "esp32_driver": "jgromes/RadioLib (Arduino-ESP32 and ESP-IDF); "
                    "LSatan/SmartRC-CC1101-Driver-Lib",
    "driver_status": "Verified",
},
"S174": {
    "esp32_driver": "miguelbalboa/rfid MFRC522 (Arduino-ESP32); ESPHome rc522_spi",
    "driver_status": "Verified",
},
"S175": {
    "addr_mode": "Fixed",
    "i_peak_ua": 100000.0,
    "esp32_driver": "Adafruit_PN532 (Arduino-ESP32); ESPHome pn532_i2c / pn532_spi",
    "driver_status": "Verified",
},
"S176": {
    "level_shift": "Divider",
    "esp32_driver": "arduino12/rdm6300 (Arduino-ESP32, ships ESP32 hardware-UART examples); "
                    "ESPHome rdm6300",
    "driver_status": "Verified",
},
"S177": {
    "addr_mode": "Fixed",
    "esp32_driver": "SparkFun_FS3000_Arduino_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S178": {
    "esp32_driver": "Seeed Grove - 2-Channel Inductive Sensor LDC1612 Arduino library "
                    "(Arduino-ESP32); TI LDC1612 register map for ESP-IDF",
    "driver_status": "Community",
},
"S179": {
    "i_peak_ua": 90000.0,
    "esp32_driver": "ESPHome dfrobot_sen0395; DFRobot_mmWave_Radar (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S180": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF adc_oneshot plus gpio for the comparator output (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S181": {
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S182": {
    "addr_mode": "Fixed",
    "esp32_driver": "SparkFun_Qwiic_Scale_NAU7802_Arduino_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S183": {
    "addr_mode": "Fixed",
    "esp32_driver": "Sensirion/arduino-i2c-sdp (Arduino-ESP32); ESPHome sdp3x",
    "driver_status": "Verified",
},
"S184": {
    "level_shift": "Divider",
    "i_peak_ua": 150000.0,
    "esp32_driver": "miguel5612/MQSensorsLib MQUnifiedsensor (Arduino-ESP32, ships ESP32 "
                    "examples)",
    "driver_status": "Verified",
},
"S185": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous peak capture (no driver needed)",
    "driver_status": "Generic",
},
"S186": {
    "esp32_driver": "ESP-IDF adc_oneshot with GPIO H-bridge AC excitation (no driver needed)",
    "driver_status": "Generic",
},
"S187": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF PCNT / attachInterrupt coincidence counting (no driver needed)",
    "driver_status": "Generic",
},
"S188": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "Open Gamma Detector project firmware is RP2040-only; on ESP32 use "
                    "ESP-IDF adc_continuous peak capture with your own MCA binning",
    "driver_status": "Community",
},
"S189": {
    "addr_mode": "Fixed",
    "esp32_driver": "Adafruit_AHTX0 (Arduino-ESP32); ESPHome aht10",
    "driver_status": "Verified",
},
"S190": {
    "addr_mode": "Fixed",
    "esp32_driver": "Adafruit_Si7021 (Arduino-ESP32); ESPHome htu21d (covers Si7021)",
    "driver_status": "Verified",
},
"S191": {
    "addr_mode": "Fixed",
    "esp32_driver": "Adafruit_SHTC3 (Arduino-ESP32); ESPHome shtcx",
    "driver_status": "Verified",
},
"S192": {
    "esp32_driver": "Adafruit_BMP280 (Arduino-ESP32); ESPHome bmp280_i2c",
    "driver_status": "Verified",
},
"S193": {
    "esp32_driver": "Adafruit_TSL2561 (Arduino-ESP32); ESPHome tsl2561",
    "driver_status": "Verified",
},
"S194": {
    "esp32_driver": "RobTillaart/Max44009 (Arduino-ESP32); ESPHome max44009",
    "driver_status": "Verified",
},
"S195": {
    "addr_mode": "Fixed",
    "esp32_driver": "Adafruit_SI1145 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S196": {
    "addr_mode": "Fixed",
    "esp32_driver": "SparkFun_VCNL4040_Arduino_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S197": {
    "esp32_driver": "Arduino-ESP32 HardwareSerial two-byte read, or ESP-IDF RMT echo timing "
                    "(no driver needed)",
    "driver_status": "Generic",
},
"S198": {
    "esp32_driver": "Arduino-ESP32 HardwareSerial frame read or ESP-IDF adc_oneshot (no "
                    "driver needed)",
    "driver_status": "Generic",
},
"S199": {
    "level_shift": "Divider",
    "i_peak_ua": 150000.0,
    "esp32_driver": "miguel5612/MQSensorsLib MQUnifiedsensor (Arduino-ESP32, ships ESP32 "
                    "examples)",
    "driver_status": "Verified",
},
"S200": {
    "level_shift": "Divider",
    "i_peak_ua": 150000.0,
    "esp32_driver": "miguel5612/MQSensorsLib MQUnifiedsensor (Arduino-ESP32, ships ESP32 "
                    "examples)",
    "driver_status": "Verified",
},
"S201": {
    "level_shift": "Divider",
    "i_peak_ua": 150000.0,
    "esp32_driver": "miguel5612/MQSensorsLib MQUnifiedsensor (Arduino-ESP32, ships ESP32 "
                    "examples)",
    "driver_status": "Verified",
},
"S202": {
    "esp32_driver": "Adafruit_AGS02MA (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S203": {
    "esp32_driver": "Arduino-ESP32 digitalRead / ESP-IDF gpio (no driver needed)",
    "driver_status": "Generic",
},
"S204": {
    "esp32_driver": "ESPHome uart + text_sensor lambda (community YAML, e.g. "
                    "patrick3399/Hi-Link_mmWave_Radar_ESPHome); no driver library needed",
    "driver_status": "Generic",
},
"S205": {
    "esp32_driver": "SparkFun_BMI270_Arduino_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S206": {
    "esp32_driver": "hideakitai/MPU9250 (Arduino-ESP32); bolderflight invensense-imu",
    "driver_status": "Verified",
},
"S207": {
    "esp32_driver": "SparkFun_KX13X_Arduino_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S208": {
    "esp32_driver": "ESP-IDF adc_continuous or I2S-ADC sampling (no driver needed)",
    "driver_status": "Generic",
},
"S209": {
    "esp32_driver": "ESP-IDF adc_oneshot plus gpio for the comparator output (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S210": {
    "esp32_driver": "milesburton/Arduino-Temperature-Control-Library + "
                    "PaulStoffregen/OneWire, with ESP-IDF PCNT for the flow pulses "
                    "(Arduino-ESP32); ESPHome dallas_temp",
    "driver_status": "Verified",
},
"S211": {
    "level_shift": "Divider",
    "esp32_driver": "Arduino-ESP32 digitalRead (no driver needed)",
    "driver_status": "Generic",
},
"S212": {
    "esp32_driver": "ESPHome ina3221; SDL_Arduino_INA3221 (Arduino-ESP32, unmaintained)",
    "driver_status": "Verified",
},
"S213": {
    "esp32_driver": "Adafruit_ADS1X15 (Arduino-ESP32); ESPHome ads1115",
    "driver_status": "Verified",
},
"S214": {
    "esp32_driver": "SimpleFOC MagneticSensorSPI (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S215": {
    "addr_mode": "Fixed",
    "esp32_driver": "madhephaestus/ESP32Encoder for the encoder build, or RobTillaart/AS5600 "
                    "for the magnetic build (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S216": {
    "esp32_driver": "DavidArmstrong/SCL3300 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S217": {
    "addr_mode": "Fixed",
    "esp32_driver": "Protocentral/protocentral_max86150_ecg_ppg (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S218": {
    "esp32_driver": "ESP-IDF adc_oneshot with peak detection (no driver needed)",
    "driver_status": "Generic",
},
"S219": {
    "level_shift": "Divider",
    "esp32_driver": "Arduino-ESP32 digitalRead (no driver needed)",
    "driver_status": "Generic",
},
"S220": {
    "esp32_driver": "Arduino-ESP32 digitalRead with INPUT_PULLUP (no driver needed)",
    "driver_status": "Generic",
},
"S221": {
    "esp32_driver": "ESP-IDF gpio ISR or PCNT (no driver needed)",
    "driver_status": "Generic",
},
"S222": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot behind a high-impedance buffer (no driver needed)",
    "driver_status": "Generic",
},
"S223": {
    "esp32_driver": "jgromes/RadioLib for the CC1101 (Arduino-ESP32); TPMS frame decode "
                    "hand-ported from rtl_433 — no ready ESP32 decoder",
    "driver_status": "Community",
},
"S224": {
    "addr_mode": "Fixed",
    "esp32_driver": "ProtoCentral FDC1004 Arduino library (Arduino-ESP32); TI FDC1004 "
                    "register map",
    "driver_status": "Community",
},
"S225": {
    "esp32_driver": "Arduino-ESP32 touchRead / ESP-IDF touch_pad (no driver needed)",
    "driver_status": "Generic",
},
"S226": {
    "esp32_driver": "ESP-IDF adc_oneshot with pulsed LED drive (no driver needed)",
    "driver_status": "Generic",
},
"S227": {
    "addr_mode": "Fixed",
    "esp32_driver": "Adafruit_TCS34725 (Arduino-ESP32); ESPHome tcs34725",
    "driver_status": "Verified",
},
"S228": {
    "esp32_driver": "espressif/esp-csi (ESP-IDF)",
    "driver_status": "Verified",
},
"S229": {
    "esp32_driver": "ESP-IDF temperature_sensor, touch_pad and adc_oneshot built-ins (no "
                    "driver needed)",
    "driver_status": "Generic",
},
"S230": {
    "addr_mode": "Fixed",
    "esp32_driver": "SparkFun_AS726X_Arduino_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S231": {
    "esp32_driver": "Arduino-ESP32 touchRead / ESP-IDF touch_pad delta tracking (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S232": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous envelope capture (no driver needed)",
    "driver_status": "Generic",
},
"S233": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "Adafruit_ADS1X15 for the external ADC (Arduino-ESP32); the Nernst maths "
                    "is your own",
    "driver_status": "Verified",
},
"S234": {
    "esp32_driver": "eModbus or 4-20ma/ModbusMaster (Arduino-ESP32); ESPHome modbus_controller",
    "driver_status": "Verified",
},
"S235": {
    "addr_mode": "Strappable",
    "esp32_driver": "boschsensortec/Bosch-BSEC2-Library with the BME68x Sensor API "
                    "(Arduino-ESP32); ESPHome bme680_bsec2",
    "driver_status": "Verified",
},
"S236": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF RMT or pulse timing, sequenced per transducer (no driver needed)",
    "driver_status": "Generic",
},
"S237": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot with slow averaging (no driver needed)",
    "driver_status": "Generic",
},
"S238": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous change detection (no driver needed)",
    "driver_status": "Generic",
},
"S239": {
    "esp32_driver": "ESPHome ezo; Atlas Scientific Ezo_I2c_lib (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S240": {
    "i_peak_ua": 160000.0,
    "esp32_driver": "thotro/arduino-dw1000 with the Makerfabs ESP32-UWB fork (Arduino-ESP32); "
                    "Qorvo DW1000 API C code for ESP-IDF",
    "driver_status": "Community",
},
"S241": {
    "i_peak_ua": 30000.0,
    "esp32_driver": "Fhilb/DW3000_Arduino and Makerfabs-ESP32-UWB-DW3000 (Arduino-ESP32); "
                    "Qorvo DW3xxx API",
    "driver_status": "Community",
},
"S242": {
    "i_peak_ua": 100000.0,
    "esp32_driver": "Arduino-ESP32 HardwareSerial / ESP-IDF uart driving the Qorvo PANS UART "
                    "shell (no driver needed)",
    "driver_status": "Generic",
},
"S243": {
    "addr_mode": "Programmable",
    "esp32_driver": "SparkFun u-blox GNSS Arduino Library v3 (Arduino-ESP32); TinyGPSPlus for "
                    "plain NMEA",
    "driver_status": "Verified",
},
"S244": {
    "addr_mode": "Programmable",
    "i_peak_ua": 110000.0,
    "esp32_driver": "SparkFun u-blox GNSS Arduino Library v3 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S245": {
    "addr_mode": "Programmable",
    "i_peak_ua": 150000.0,
    "esp32_driver": "SparkFun u-blox GNSS Arduino Library v3 covers the UBX basics but has no "
                    "X20-specific support (Arduino-ESP32)",
    "driver_status": "Community",
},
"S246": {
    "esp32_driver": "mikalhart/TinyGPSPlus for NMEA plus any NTRIP client (Arduino-ESP32); no "
                    "vendor Arduino library exists",
    "driver_status": "Verified",
},
"S247": {
    "i_peak_ua": 250000.0,
    "esp32_driver": "SparkFun_Unicore_GNSS_Arduino_Library, a.k.a. SparkFun UM980 Triband RTK "
                    "GNSS (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S248": {
    "i_peak_ua": 350000.0,
    "esp32_driver": "SparkFun_Unicore_GNSS_Arduino_Library targets the UM980; UM982 "
                    "dual-antenna heading commands are hand-sent over UART (Arduino-ESP32)",
    "driver_status": "Community",
},
"S249": {
    "esp32_driver": "mikalhart/TinyGPSPlus for the GNSS half plus mprograms/QMC5883LCompass "
                    "(or Adafruit_HMC5883_Unified) for the compass (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S250": {
    "addr_mode": "Programmable",
    "esp32_driver": "SparkFun u-blox GNSS Arduino Library v3 (Arduino-ESP32); PPS capture via "
                    "ESP-IDF gptimer/PCNT is your own code",
    "driver_status": "Verified",
},
"S251": {
    "esp32_driver": "Arduino-ESP32 HardwareSerial NMEA read plus ESP-IDF gptimer/PCNT capture "
                    "on the 10MHz and PPS outputs (no driver needed)",
    "driver_status": "Generic",
},
"S252": {
    "esp32_driver": "Arduino-ESP32 HardwareSerial driving the u-blox u-connectLocate AT "
                    "command set (no driver needed)",
    "driver_status": "Generic",
},
"S253": {
    "esp32_driver": "ESP-IDF esp_wifi_scan_start plus your own kNN or particle filter (no "
                    "driver exists)",
    "driver_status": "Generic",
},
"S254": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "Adafruit_ADS1X15 across a 150R sense resistor (Arduino-ESP32); ESPHome "
                    "ads1115",
    "driver_status": "Verified",
},
"S255": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "Adafruit_ADS1X15 across a 150R sense resistor (Arduino-ESP32); ESPHome "
                    "ads1115",
    "driver_status": "Verified",
},
"S256": {
    "esp32_driver": "ESPHome modbus_controller; eModbus or 4-20ma/ModbusMaster (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S257": {
    "esp32_driver": "ESPHome sdm_meter; reaper7/SDM_Energy_Meter (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S258": {
    "esp32_driver": "ESP-IDF driver/twai.h with your own ISO-TP layer (no driver library; "
                    "ELMduino is for ELM327 adapters, not raw CAN)",
    "driver_status": "Generic",
},
"S259": {
    "level_shift": "Isolator",
    "esp32_driver": "Arduino-ESP32 digitalRead (no driver needed)",
    "driver_status": "Generic",
},
"S260": {
    "level_shift": "Isolator",
    "esp32_driver": "Arduino-ESP32 digitalRead, ESP-IDF PCNT for counting (no driver needed)",
    "driver_status": "Generic",
},
"S261": {
    "level_shift": "Isolator",
    "esp32_driver": "Arduino-ESP32 digitalRead, ESP-IDF PCNT for counting and timing (no "
                    "driver needed)",
    "driver_status": "Generic",
},
"S262": {
    "level_shift": "Isolator",
    "esp32_driver": "Arduino-ESP32 digitalRead with debounce sized to ignore the OSSD test "
                    "pulses (no driver needed)",
    "driver_status": "Generic",
},
"S263": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "Adafruit_MAX31865 (Arduino-ESP32); ESPHome max31865",
    "driver_status": "Verified",
},
"S264": {
    "level_shift": "Isolator",
    "esp32_driver": "Arduino-ESP32 digitalRead (no driver needed)",
    "driver_status": "Generic",
},
"S265": {
    "level_shift": "Direct",
    "esp32_driver": "Arduino-ESP32 digitalRead with INPUT_PULLUP and 50ms debounce (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S266": {
    "level_shift": "Direct",
    "esp32_driver": "Arduino-ESP32 digitalRead with INPUT_PULLUP and debounce (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S267": {
    "i_peak_ua": 1000000.0,
    "esp32_driver": "SparkFun_Simultaneous_RFID_Tag_Reader_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S268": {
    "i_peak_ua": 500000.0,
    "esp32_driver": "Arduino-ESP32 HardwareSerial with a hand-written 0xBB/0x7E frame parser "
                    "(no library exists)",
    "driver_status": "Generic",
},
"S269": {
    "i_peak_ua": 250000.0,
    "esp32_driver": "ATrappmann/PN5180-Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S270": {
    "addr_mode": "Fixed",
    "esp32_driver": "SparkFun_ST25DV64KC_Arduino_Library (Arduino-ESP32); STMicroelectronics "
                    "stm32-st25dv portable C driver for ESP-IDF",
    "driver_status": "Verified",
},
"S271": {
    "addr_mode": "Fixed",
    "esp32_driver": "Arduino-ESP32 Wire register access against the NXP NTAG I2C Plus "
                    "register map (no dominant driver)",
    "driver_status": "Generic",
},
"S272": {
    "i_peak_ua": 150000.0,
    "esp32_driver": "Arduino-ESP32 HardwareSerial line reads / ESP-IDF uart driver (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S273": {
    "i_peak_ua": 150000.0,
    "esp32_driver": "ESPHome wiegand component; Arduino-ESP32 GPIO interrupt capture on D0/D1",
    "driver_status": "Verified",
},
"S274": {
    "i_peak_ua": 50000.0,
    "esp32_driver": "DFRobot_ID809 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S275": {
    "esp32_driver": "NimBLE-Arduino (Arduino-ESP32); ESPHome esp32_ble_tracker with ble_rssi",
    "driver_status": "Verified",
},
"S276": {
    "addr_mode": "Programmable",
    "esp32_driver": "espressif/esp-cryptoauthlib (ESP-IDF component registry); ArduinoECCX08 "
                    "(Arduino-ESP32)",
    "driver_status": "Verified",
},
"S277": {
    "addr_mode": "Fixed",
    "i_peak_ua": 100000.0,
    "esp32_driver": "Sensirion arduino-i2c-sen5x (Arduino-ESP32); ESPHome sen5x component",
    "driver_status": "Verified",
},
"S278": {
    "addr_mode": "Fixed",
    "esp32_driver": "Sensirion arduino-i2c-sen66 (Arduino-ESP32); ESPHome sen6x component",
    "driver_status": "Verified",
},
"S279": {
    "esp32_driver": "Sensirion arduino-i2c-stc3x (Arduino-ESP32); "
                    "SparkFun_STC3x_Arduino_Library",
    "driver_status": "Verified",
},
"S280": {
    "addr_mode": "Fixed",
    "esp32_driver": "Sensirion arduino-i2c-stcc4 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S281": {
    "esp32_driver": "Arduino-ESP32 HardwareSerial with the documented SprintIR ASCII command "
                    "set (no driver needed)",
    "driver_status": "Generic",
},
"S282": {
    "i_peak_ua": 300000.0,
    "esp32_driver": "Arduino-ESP32 HardwareSerial with the documented SenseAir K30 "
                    "serial/Modbus frames (no driver needed)",
    "driver_status": "Generic",
},
"S283": {
    "i_peak_ua": 300000.0,
    "esp32_driver": "espressif/esp-idf i2c_master + Telaire T67xx register map (community "
                    "Arduino sketches only)",
    "driver_status": "Community",
},
"S284": {
    "i_peak_ua": 60000.0,
    "esp32_driver": "Arduino-ESP32 HardwareSerial with the documented Cubic CM110x UART "
                    "frame; community ESPHome external components",
    "driver_status": "Community",
},
"S285": {
    "esp32_driver": "espressif/bme690 (ESP-IDF component registry); Bosch BME69x SensorAPI + "
                    "BSEC 3",
    "driver_status": "Verified",
},
"S286": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot behind a low-noise buffer / external ADC (no driver "
                    "exists)",
    "driver_status": "Generic",
},
"S287": {
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S288": {
    "level_shift": "Analog-front-end",
    "i_peak_ua": 80000.0,
    "esp32_driver": "ESP-IDF adc_oneshot behind an instrumentation amplifier (no driver "
                    "exists)",
    "driver_status": "Generic",
},
"S289": {
    "esp32_driver": "Arduino-ESP32 HardwareSerial with the documented INIR ASCII command set "
                    "(no driver needed)",
    "driver_status": "Generic",
},
"S290": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot behind an external potentiostat and 16-bit ADC (no "
                    "driver exists)",
    "driver_status": "Generic",
},
"S291": {
    "esp32_driver": "Arduino-ESP32 HardwareSerial parsing the documented Winsen 9-byte frame "
                    "(no driver needed)",
    "driver_status": "Generic",
},
"S292": {
    "esp32_driver": "Arduino-ESP32 HardwareSerial parsing the documented Winsen 9-byte frame "
                    "(no driver needed)",
    "driver_status": "Generic",
},
"S293": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot behind an LMP91000 potentiostat front end (no sensor "
                    "driver exists)",
    "driver_status": "Generic",
},
"S294": {
    "i_peak_ua": 100000.0,
    "esp32_driver": "Adafruit_PM25AQI (Arduino-ESP32); ESPHome pmsx003 component",
    "driver_status": "Verified",
},
"S295": {
    "i_peak_ua": 80000.0,
    "esp32_driver": "Arduino-ESP32 HardwareSerial with the documented HPMA115 binary command "
                    "set; community hpma115S0 Arduino library",
    "driver_status": "Community",
},
"S296": {
    "i_peak_ua": 175000.0,
    "esp32_driver": "Arduino-ESP32 SPI with the documented OPC-N3 command set; py-opc/opcn3 "
                    "as reference (no ESP32 library)",
    "driver_status": "Community",
},
"S297": {
    "i_peak_ua": 100000.0,
    "esp32_driver": "PieraSystems 7100-I2C-example / 7100-UART-example vendor Arduino code "
                    "(Arduino-ESP32)",
    "driver_status": "Community",
},
"S298": {
    "esp32_driver": "DFRobot_BMI323 (Arduino-ESP32); boschsensortec BMI323_SensorAPI (ESP-IDF)",
    "driver_status": "Verified",
},
"S299": {
    "esp32_driver": "SparkFun_BMA400_Arduino_Library (Arduino-ESP32); Bosch BMA400 SensorAPI "
                    "(ESP-IDF)",
    "driver_status": "Verified",
},
"S300": {
    "addr_mode": "Strappable",
    "esp32_driver": "DFRobot_BMM350 (Arduino-ESP32); boschsensortec BMM350_SensorAPI (ESP-IDF)",
    "driver_status": "Verified",
},
"S301": {
    "esp32_driver": "SparkFun_LSM6DSV16X_Arduino_Library (Arduino-ESP32); ST "
                    "STMems_Standard_C_drivers lsm6dsv16x_reg (ESP-IDF)",
    "driver_status": "Verified",
},
"S302": {
    "esp32_driver": "Adafruit_LSM6DS (Arduino-ESP32); ST STMems_Standard_C_drivers "
                    "lsm6dso32_reg (ESP-IDF)",
    "driver_status": "Verified",
},
"S303": {
    "esp32_driver": "STM32duino LIS2DW12 (Arduino-ESP32); ST STMems_Standard_C_drivers "
                    "lis2dw12_reg (ESP-IDF)",
    "driver_status": "Verified",
},
"S304": {
    "esp32_driver": "Adafruit_LSM6DS (covers ISM330DHCX) (Arduino-ESP32); ST "
                    "STMems_Standard_C_drivers ism330dhcx_reg (ESP-IDF)",
    "driver_status": "Verified",
},
"S305": {
    "esp32_driver": "ST STMems_Standard_C_drivers iis3dwb_reg (ESP-IDF, platform-agnostic C)",
    "driver_status": "Verified",
},
"S306": {
    "esp32_driver": "finani/ICM42688 Arduino library (Arduino-ESP32); TDK InvenSense "
                    "ICM-426xx eMD driver (ESP-IDF)",
    "driver_status": "Verified",
},
"S307": {
    "esp32_driver": "tdk-invn-oss/motion.arduino.ICM45686 (Arduino-ESP32); "
                    "tdk-invn-oss/motion.mcu.icm45686.driver (ESP-IDF)",
    "driver_status": "Verified",
},
"S308": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous behind an anti-alias filter and buffer (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S309": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous behind an anti-alias filter and buffer (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S310": {
    "i_peak_ua": 50000.0,
    "esp32_driver": "Analog Devices no-OS adis16505 driver as reference; hand-written SPI "
                    "burst read on ESP-IDF spi_master",
    "driver_status": "Community",
},
"S311": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous behind an IEPE constant-current conditioner and "
                    "anti-alias filter (no driver exists)",
    "driver_status": "Generic",
},
"S312": {
    "esp32_driver": "Murata SCA3300 reference C code and register map; port to ESP-IDF "
                    "spi_master (no first-party Arduino library)",
    "driver_status": "Community",
},
"S313": {
    "esp32_driver": "Arduino-ESP32 digitalRead with INPUT_PULLUP plus debounce (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S314": {
    "esp32_driver": "Pololu L3G Arduino library (Arduino-ESP32); Adafruit_L3GD20_U",
    "driver_status": "Verified",
},
"S315": {
    "addr_mode": "Fixed",
    "i_peak_ua": 100000.0,
    "esp32_driver": "SparkFun_AS7265x_Arduino_Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S316": {
    "addr_mode": "Fixed",
    "esp32_driver": "Adafruit_AS7343 (Arduino-ESP32); SparkFun_AS7343_Arduino_Library",
    "driver_status": "Verified",
},
"S317": {
    "level_shift": "Analog-front-end",
    "i_peak_ua": 30000.0,
    "esp32_driver": "ESP-IDF LEDC clock generation + external ADC capture; GroupGets Arduino "
                    "timing sketch as reference",
    "driver_status": "Community",
},
"S318": {
    "i_peak_ua": 40000.0,
    "esp32_driver": "ESP-IDF PCNT pulse counting (no driver needed)",
    "driver_status": "Generic",
},
"S319": {
    "esp32_driver": "ClosedCube_OPT3001 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S320": {
    "esp32_driver": "SparkFun Ambient Light Sensor Arduino Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S321": {
    "esp32_driver": "IRremoteESP8266 (Arduino-ESP32); ESP-IDF RMT RX driver",
    "driver_status": "Verified",
},
"S322": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot behind a transimpedance amplifier (no driver needed)",
    "driver_status": "Generic",
},
"S323": {
    "esp32_driver": "ESP-IDF adc_oneshot / Arduino-ESP32 analogRead (no driver needed)",
    "driver_status": "Generic",
},
"S324": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "Adafruit_ADS1X15 (Arduino-ESP32) reading the millivolt output; no sensor "
                    "driver exists",
    "driver_status": "Generic",
},
"S325": {
    "esp32_driver": "karl-mohring/MLX90621-Lite Arduino library (Arduino-ESP32); Melexis "
                    "reference driver for the compensation maths",
    "driver_status": "Community",
},
"S326": {
    "esp32_driver": "Heimann reference compensation code; community igor-morawski/HTPA32x32d "
                    "port (no maintained ESP32 library)",
    "driver_status": "Community",
},
"S327": {
    "esp32_driver": "Heimann reference compensation code and application note; port to "
                    "ESP-IDF spi_master yourself",
    "driver_status": "Community",
},
"S328": {
    "i_peak_ua": 120000.0,
    "esp32_driver": "Meridian SenXor SDK; Waveshare ESP32-S3 reference firmware for this "
                    "module",
    "driver_status": "Community",
},
"S329": {
    "esp32_driver": "Teledyne FLIR Lepton SDK (CCI over I2C + VoSPI); community ESP32 VoSPI "
                    "ports of varying quality",
    "driver_status": "Community",
},
"S330": {
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S331": {
    "i_peak_ua": 40000.0,
    "esp32_driver": "Adafruit_VL53L4CD (Arduino-ESP32); ST VL53L4CD ULD driver (ESP-IDF)",
    "driver_status": "Verified",
},
"S332": {
    "i_peak_ua": 40000.0,
    "esp32_driver": "stm32duino VL53L4CX Arduino library (Arduino-ESP32); ST VL53L4CX ULD "
                    "driver (ESP-IDF)",
    "driver_status": "Verified",
},
"S333": {
    "i_peak_ua": 90000.0,
    "esp32_driver": "stm32duino VL53L8CX Arduino library (Arduino-ESP32); ST VL53L8CX ULD "
                    "driver (ESP-IDF)",
    "driver_status": "Verified",
},
"S334": {
    "esp32_driver": "bitcraze/Bitcraze_PMW3901 Arduino library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S335": {
    "esp32_driver": "Bitcraze_PMW3901 Arduino library with the PAA5100JE near-field register "
                    "set; Pimoroni pmw3901-python as reference",
    "driver_status": "Community",
},
"S336": {
    "i_peak_ua": 600000.0,
    "esp32_driver": "Slamtec rplidar_sdk (C++) / RPLidarDriver Arduino library (Arduino-ESP32)",
    "driver_status": "Community",
},
"S337": {
    "esp32_driver": "Arduino-ESP32 HardwareSerial parsing the documented Benewake 9-byte "
                    "frame (no driver needed)",
    "driver_status": "Generic",
},
"S338": {
    "i_peak_ua": 1500000.0,
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S339": {
    "esp32_driver": "SparkFun_Qwiic_XM125_Arduino_Library (Arduino-ESP32); Acconeer RSS SDK "
                    "(ESP-IDF)",
    "driver_status": "Verified",
},
"S340": {
    "i_peak_ua": 90000.0,
    "esp32_driver": "ESPHome rd03d component; Arduino-ESP32 HardwareSerial frame parsing",
    "driver_status": "Verified",
},
"S341": {
    "i_peak_ua": 80000.0,
    "esp32_driver": "ESPHome ld2412 component (first-class; the ld2410 component does NOT "
                    "work)",
    "driver_status": "Verified",
},
"S342": {
    "i_peak_ua": 400000.0,
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S343": {
    "esp32_driver": "omron-devhub/d6t-2jcieev01-arduino vendor sample driver, d6t-32l example "
                    "(Arduino-ESP32)",
    "driver_status": "Community",
},
"S344": {
    "esp32_driver": "ProtoCentral_FDC2214_Capacitance Arduino library (Arduino-ESP32); TI "
                    "reference C code",
    "driver_status": "Community",
},
"S345": {
    "i_peak_ua": 2500000.0,
    "esp32_driver": "Arduino-ESP32 HardwareSerial parsing the TI mmWave demo TLV stream (no "
                    "driver needed)",
    "driver_status": "Generic",
},
"S346": {
    "level_shift": "Divider",
    "esp32_driver": "ESP-IDF adc_oneshot / Arduino-ESP32 analogRead of the BTA voltage output "
                    "(no driver needed)",
    "driver_status": "Generic",
},
"S347": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot behind a high-impedance electrometer buffer (no "
                    "driver exists)",
    "driver_status": "Generic",
},
"S348": {
    "esp32_driver": "Adafruit_ADS1X15 (Arduino-ESP32) across a 150 ohm loop sense resistor; "
                    "no driver needed",
    "driver_status": "Generic",
},
"S349": {
    "esp32_driver": "DFRobot_EC Arduino library (Arduino-ESP32) — written for 10-bit AVR ADC, "
                    "rescale for the ESP32 ADC",
    "driver_status": "Community",
},
"S350": {
    "esp32_driver": "ESP-IDF PCNT pulse counting (no driver needed)",
    "driver_status": "Generic",
},
"S351": {
    "addr_mode": "Fixed",
    "esp32_driver": "Sensirion arduino-i2c-sf06-lf (SLF3x/SF06 liquid flow) (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S352": {
    "esp32_driver": "eModbus (Arduino-ESP32 / ESP-IDF) or ModbusMaster over a MAX485 "
                    "transceiver",
    "driver_status": "Verified",
},
"S353": {
    "esp32_driver": "Arduino-ESP32 digitalRead with INPUT_PULLUP plus debounce (no driver "
                    "needed)",
    "driver_status": "Generic",
},
"S354": {
    "esp32_driver": "eModbus (Arduino-ESP32 / ESP-IDF) or ModbusMaster over a MAX485 "
                    "transceiver",
    "driver_status": "Verified",
},
"S355": {
    "esp32_driver": "EnviroDIY Arduino-SDI-12 (Arduino-ESP32; ESP support since v2.0.1)",
    "driver_status": "Verified",
},
"S356": {
    "esp32_driver": "EnviroDIY Arduino-SDI-12 (Arduino-ESP32; ESP support since v2.0.1)",
    "driver_status": "Verified",
},
"S357": {
    "esp32_driver": "Arduino-ESP32 GPIO H-bridge AC excitation + analogRead of the divider "
                    "(no driver needed)",
    "driver_status": "Generic",
},
"S358": {
    "esp32_driver": "EnviroDIY Arduino-SDI-12 (Arduino-ESP32; ESP support since v2.0.1)",
    "driver_status": "Verified",
},
"S359": {
    "addr_mode": "Fixed",
    "esp32_driver": "Sensirion arduino-i2c-scd30 / Adafruit_SCD30 (Arduino-ESP32); ESPHome "
                    "scd30 component",
    "driver_status": "Verified",
},
"S360": {
    "i_peak_ua": 300000.0,
    "esp32_driver": "EnviroDIY Arduino-SDI-12 (Arduino-ESP32; ESP support since v2.0.1)",
    "driver_status": "Verified",
},
"S361": {
    "esp32_driver": "Adafruit_ADS1X15 (Arduino-ESP32) reading the potentiometer divider; no "
                    "driver needed",
    "driver_status": "Generic",
},
"S362": {
    "esp32_driver": "Protocentral protocentral_max30001_arduino_library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S363": {
    "esp32_driver": "Analog Devices ad5940lib (portable C) ported onto ESP-IDF spi_master; no "
                    "Arduino library",
    "driver_status": "Community",
},
"S364": {
    "esp32_driver": "Protocentral protocentral-ads1292r-arduino (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S365": {
    "esp32_driver": "espressif/esp-idf spi_master + TI ADS129x register map; community "
                    "research-repo ADS129x drivers as reference",
    "driver_status": "Community",
},
"S366": {
    "esp32_driver": "OpenBCI open-source firmware as the reference ADS1299 driver; port onto "
                    "ESP-IDF spi_master",
    "driver_status": "Community",
},
"S367": {
    "i_peak_ua": 40000.0,
    "esp32_driver": "Arduino-ESP32 HardwareSerial reading the Cyton binary stream (BrainFlow "
                    "is host-side only)",
    "driver_status": "Generic",
},
"S368": {
    "esp32_driver": "ProtoCentral AFE4490 Arduino library (Arduino-ESP32); TI register "
                    "documentation for the timing engine",
    "driver_status": "Community",
},
"S369": {
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S370": {
    "esp32_driver": "lewisxhe/MAX30208_Library (Arduino-ESP32)",
    "driver_status": "Community",
},
"S371": {
    "i_peak_ua": 600000.0,
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S372": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot behind a constant-voltage op-amp front end (no "
                    "driver needed)",
    "driver_status": "Generic",
},
"S373": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous behind a JFET-input charge amplifier (no driver "
                    "exists)",
    "driver_status": "Generic",
},
"S374": {
    "addr_mode": "Fixed",
    "esp32_driver": "Adafruit_MAX1704X (Arduino-ESP32); SparkFun MAX1704x Fuel Gauge Arduino "
                    "Library",
    "driver_status": "Verified",
},
"S375": {
    "addr_mode": "Fixed",
    "esp32_driver": "espressif/esp-idf i2c_master + ADI ModelGauge m5 host-side reference "
                    "implementation (no Arduino library)",
    "driver_status": "Community",
},
"S376": {
    "addr_mode": "Fixed",
    "esp32_driver": "Adafruit_LC709203F (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S377": {
    "addr_mode": "Fixed",
    "esp32_driver": "SparkFun BQ27441 Arduino Library (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S378": {
    "addr_mode": "Strappable",
    "esp32_driver": "espressif/esp-idf i2c_master + TI INA700 register map (ESPHome ina2xx "
                    "covers INA228/229/237/238/239 only, NOT INA700)",
    "driver_status": "Community",
},
"S379": {
    "esp32_driver": "ESPHome atm90e32 component; CircuitSetup ATM90E32 Arduino library "
                    "(Arduino-ESP32)",
    "driver_status": "Verified",
},
"S380": {
    "esp32_driver": "ESPHome ade7953_i2c / ade7953_spi components; Tasmota ADE7953 driver",
    "driver_status": "Verified",
},
"S381": {
    "esp32_driver": "ESPHome bl0940 component; Tasmota BL0940 driver",
    "driver_status": "Verified",
},
"S382": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot across a burden resistor with a bipolar bias network "
                    "(no driver exists)",
    "driver_status": "Generic",
},
"S383": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot across a precision burden resistor with a bipolar "
                    "bias network (no driver exists)",
    "driver_status": "Generic",
},
"S384": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous on the integrator output with a mid-rail bias (no "
                    "driver exists)",
    "driver_status": "Generic",
},
"S385": {
    "level_shift": "Isolator",
    "esp32_driver": "Arduino-ESP32 digitalRead of the trip output across a mains-rated "
                    "isolation barrier (no driver exists)",
    "driver_status": "Generic",
},
"S386": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_oneshot on the low-side differential output via a difference "
                    "amplifier (no driver exists)",
    "driver_status": "Generic",
},
"S388": {
    "esp32_driver": "Adafruit_CAP1188 (Arduino-ESP32)",
    "driver_status": "Verified",
},
"S389": {
    "addr_mode": "Fixed",
    "esp32_driver": "espressif/esp-idf i2c_master + Microchip AT42QT1070 register map; "
                    "community Arduino AT42QT libraries",
    "driver_status": "Community",
},
"S390": {
    "addr_mode": "Strappable",
    "esp32_driver": "espressif/esp_lcd_touch_gt911 and esp_lcd_touch_ft5x06 (ESP-IDF "
                    "component registry); TAMC_GT911 (Arduino-ESP32); LVGL indev bindings",
    "driver_status": "Verified",
},
"S391": {
    "esp32_driver": "Azoteq reference C code ported onto ESP-IDF i2c_master; community "
                    "Arduino ports are thin",
    "driver_status": "Community",
},
"S392": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "bogde/HX711 (Arduino-ESP32); SparkFun_Qwiic_Scale_NAU7802_Arduino_Library",
    "driver_status": "Verified",
},
"S393": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "bogde/HX711 (Arduino-ESP32); SparkFun_Qwiic_Scale_NAU7802_Arduino_Library",
    "driver_status": "Verified",
},
"S394": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "bogde/HX711 (Arduino-ESP32) for a raw bridge, or adc_oneshot across a "
                    "4-20mA burden for an amplified unit",
    "driver_status": "Generic",
},
"S395": {
    "esp32_driver": "Arduino-ESP32 GPIO row/column scanning + adc_oneshot per column (no "
                    "driver exists)",
    "driver_status": "Generic",
},
"S396": {
    "esp32_driver": "ESP-IDF adc_oneshot / Arduino-ESP32 analogRead of a fixed divider (no "
                    "driver needed)",
    "driver_status": "Generic",
},
"S397": {
    "esp32_driver": "ProtoCentral FDC1004 Arduino library (Arduino-ESP32) for DIY builds",
    "driver_status": "Community",
},
"S398": {
    "esp32_driver": "No driver — it is an electrode material; read it with adc_oneshot inside "
                    "whatever circuit it sits in",
    "driver_status": "Generic",
},
"S399": {
    "esp32_driver": "No driver — a passive RF structure that connects to a radio front end, "
                    "not to an ESP32 peripheral",
    "driver_status": "Generic",
},
"S400": {
    "esp32_driver": "ESP-IDF I2S PDM RX mode (i2s_pdm) (no driver needed)",
    "driver_status": "Generic",
},
"S401": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous / I2S ADC behind a charge or voltage preamp (no "
                    "driver exists)",
    "driver_status": "Generic",
},
"S402": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF MCPWM/LEDC 40kHz burst drive + adc_continuous envelope capture "
                    "(no driver needed)",
    "driver_status": "Generic",
},
"S403": {
    "esp32_driver": "tdk-invn-oss/ultrasonic.arduino.CHx01 Arduino driver (Arduino-ESP32); "
                    "TDK SonicLib (ESP-IDF)",
    "driver_status": "Verified",
},
"S404": {
    "i_peak_ua": 300000.0,
    "esp32_driver": None,
    "driver_status": "None-known",
},
"S405": {
    "i_peak_ua": 120000.0,
    "esp32_driver": "RadioLib (Arduino-ESP32 and ESP-IDF)",
    "driver_status": "Verified",
},
"S406": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous / analog comparator behind a charge-sensitive "
                    "preamp and shaper (no ESP32 driver exists)",
    "driver_status": "Generic",
},
"S407": {
    "level_shift": "Analog-front-end",
    "esp32_driver": "ESP-IDF adc_continuous behind a charge-sensitive amplifier and "
                    "discriminator (no driver exists)",
    "driver_status": "Generic",
},
}
