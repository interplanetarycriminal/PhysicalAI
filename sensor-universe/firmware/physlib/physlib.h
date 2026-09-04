/*
 * physlib.h — executable physics for the ESP32 Sensor Universe atlas.
 *
 * This is the C++ half of HANDOFF.md "Phase 4 — Executable physics: physlib".
 * It is header-only, allocation-free, `float`-only, and deliberately free of
 * <Arduino.h>, <Wire.h> and every other hardware header, so that:
 *
 *   - the three ESP32 examples under ../src/ include it unchanged, and
 *   - the host-side Unity test under ../test/test_physlib/ compiles the very
 *     same code with a desktop compiler and checks it against published
 *     psychrometric numbers.
 *
 * Every function names the fusion edge key it serves and quotes the atlas's
 * own `math` string verbatim. The atlas is the source of truth; nothing here
 * invents physics that the atlas does not state.
 *
 * Source of the quoted strings: sensor-universe/data/fusion.py, FUSION_EDGES.
 *
 * ---------------------------------------------------------------------------
 * Invalid results
 * ---------------------------------------------------------------------------
 * Every scalar function returns PHYSLIB_INVALID (a quiet NaN) rather than a
 * plausible-looking number when it is handed input outside its domain:
 * RH outside (0, 100], a temperature at or below absolute zero, a CO2 decay
 * that did not decay, dt <= 0, a vapour pressure exceeding total pressure.
 * Call physlib::is_valid() before believing a value. The examples depend on
 * this: a NaN is a refusal to answer, never a zero.
 *
 * ---------------------------------------------------------------------------
 * Confounds are values, not comments
 * ---------------------------------------------------------------------------
 * Each edge returns a small result struct that carries the inferred quantity,
 * its units, a validity flag, and the edge's confound as data: the verbatim
 * atlas confound string (always present — these caveats never stop applying)
 * plus a ConfoundState saying whether a machine-detectable instance of it
 * actually fired on this reading, and a detail string saying which one.
 */

#ifndef PHYSLIB_H
#define PHYSLIB_H

#include <cmath>

namespace physlib {

/* ===========================================================================
 * Constants — named, with units.
 * ===========================================================================
 */

/** Quiet NaN returned by every function that refuses to answer. */
#define PHYSLIB_INVALID (NAN)

/* --- Magnus-Tetens coefficients, exactly as the atlas states them ---------
 * The atlas writes the dew-point step as
 *     γ = ln(RH/100) + 17.62·T/(243.12+T)
 * i.e. the WMO/Sonntag-1990 Magnus coefficients over water.
 */
static const float MAGNUS_A = 17.62f;    /* dimensionless                     */
static const float MAGNUS_B = 243.12f;   /* degC                              */
static const float MAGNUS_ES0_PA = 611.2f; /* Pa, saturation pressure at 0 degC */

/* Magnus validity band over water (Sonntag 1990). Outside it the fit is not
 * trustworthy; physlib still computes, but this is the honest domain. */
static const float MAGNUS_T_MIN_C = -45.0f; /* degC */
static const float MAGNUS_T_MAX_C = 60.0f;  /* degC */

/* --- Thermodynamics ------------------------------------------------------ */
static const float R_UNIVERSAL = 8.31446f;  /* J / (mol * K)  molar gas constant */
static const float M_DRY_AIR = 0.0289652f;  /* kg / mol       dry air            */
static const float M_WATER_VAPOUR = 0.018016f; /* kg / mol    water vapour       */
static const float ABSOLUTE_ZERO_C = -273.15f; /* degC                          */

/* --- Edge thresholds, from the atlas text -------------------------------- */

/** condensation-watch: "Risk when T_surface − T_dew < 1.5°C". Units: K. */
static const float CONDENSATION_MARGIN_THRESHOLD_K = 1.5f;

/** ach-co2-decay: "C_out ≈ 420 ppm". Units: ppm CO2. */
static const float CO2_OUTDOOR_DEFAULT_PPM = 420.0f;

/* --- Firmware heuristics (NOT atlas numbers) -----------------------------
 * These thresholds are this firmware's own choices for turning a confound the
 * atlas describes in prose into something the code can actually detect. They
 * are flagged as heuristics everywhere they are used.
 */

/** ach-co2-decay: a decay window shorter than this cannot support a fit.
 *  15 min at the SCD41's 5 s cadence is ~180 points; below that the ppm noise
 *  (+/-(40 ppm + 5% of reading)) dominates the slope. Units: hours. */
static const float ACH_MIN_FIT_WINDOW_H = 0.25f;

/** air-density-live: the BME280 confound says self-heating biases T "by up to
 *  1°C". A combo-board temperature this far above an independent reference
 *  is self-heating, not weather. Units: K. */
static const float SELF_HEATING_LIMIT_K = 1.0f;

/** condensation-watch: an IR spot reading this far from air temperature on an
 *  indoor wall is more likely a low-emissivity (shiny) target reflecting
 *  something else than a real surface temperature. Units: K. */
static const float IR_SUSPECT_BELOW_AIR_K = 15.0f;
static const float IR_SUSPECT_ABOVE_AIR_K = 5.0f;

/* ===========================================================================
 * Validity helpers
 * ===========================================================================
 */

/** True when v is a real number this library is willing to stand behind. */
inline bool is_valid(float v) { return !std::isnan(v) && !std::isinf(v); }

/** True when t_c is a physically possible temperature (above absolute zero). */
inline bool is_valid_temperature_c(float t_c) {
    return is_valid(t_c) && t_c > ABSOLUTE_ZERO_C;
}

/** True when rh_pct is a usable relative humidity in percent.
 *  0 % is rejected for dew point (ln(0) diverges) but allowed for density. */
inline bool is_valid_rh_pct(float rh_pct) {
    return is_valid(rh_pct) && rh_pct >= 0.0f && rh_pct <= 100.0f;
}

/* ===========================================================================
 * Confound model — a confound is a value the caller can branch on.
 * ===========================================================================
 */

/** Did a machine-detectable instance of this edge's confound fire? */
enum class ConfoundState : unsigned char {
    /** The standing confound applies (it always does) but nothing this code
     *  can detect actually fired on this reading. */
    Standing = 0,
    /** A machine check fired: read confound_detail for which one. */
    Detected = 1
};

/**
 * The common shell of every edge result: the inferred quantity, its units,
 * whether it may be believed, and the confound carried as data.
 */
struct EdgeResult {
    float value;                 /* the inferred quantity, or PHYSLIB_INVALID */
    const char *units;           /* units of `value`, never null              */
    bool valid;                  /* false => `value` is PHYSLIB_INVALID       */
    const char *invalid_reason;  /* why, or null when valid                   */
    ConfoundState confound;      /* Standing | Detected                       */
    const char *confound_text;   /* VERBATIM fusion.py confound, never null   */
    const char *confound_detail; /* what fired, or null when nothing did      */
};

/* --- The three verbatim confound strings, quoted from fusion.py ---------- */

/** fusion.py FUSION_EDGES["condensation-watch"].confound, verbatim. */
static const char *const CONFOUND_CONDENSATION_WATCH =
    "Emissivity: a shiny surface lies to the IR thermometer by 20× "
    "(Anti-Catalog II). Put a strip of matt tape at the cold spot and aim at "
    "that.";

/** fusion.py FUSION_EDGES["ach-co2-decay"].confound, verbatim. */
static const char *const CONFOUND_ACH_CO2_DECAY =
    "Anyone re-entering mid-decay corrupts the fit (gate on presence); "
    "wind-driven infiltration makes ACH weather-dependent, so log the fits "
    "against wind and you get the infiltration curve as a bonus.";

/** fusion.py FUSION_EDGES["air-density-live"].confound, verbatim. */
static const char *const CONFOUND_AIR_DENSITY_LIVE =
    "Sensor self-heating biases T by up to 1°C on combo boards "
    "(BME280's known flaw) — read fast, sleep long, or mount the "
    "thermometer separately.";

/* ===========================================================================
 * Magnus saturation vapour pressure and dew point
 *   Serves fusion edge: "condensation-watch"  (also feeds "air-density-live")
 *   Atlas math, verbatim:
 *     "Risk when T_surface − T_dew < 1.5°C (T_dew via Magnus:
 *      γ = ln(RH/100) + 17.62·T/(243.12+T))"
 * ===========================================================================
 */

/**
 * Saturation vapour pressure over liquid water, Magnus form.
 *
 *     e_s(T) = 611.2 Pa * exp(17.62 * T / (243.12 + T))
 *
 * This is the same 17.62 / 243.12 pair the atlas names for the dew point; it
 * is the exponential whose inverse gives dew_point_magnus(). It is also the
 * "P_vap from RH x saturation pressure (Magnus)" half of the air-density edge.
 *
 * @param t_c  air temperature, degC. Trustworthy over -45..+60 degC.
 * @return     saturation vapour pressure in Pa, or PHYSLIB_INVALID if t_c is
 *             at or below absolute zero, NaN, or would divide by zero.
 *
 * Cites: fusion edge "condensation-watch"; fusion edge "air-density-live".
 */
inline float saturation_vapour_pressure_pa(float t_c) {
    if (!is_valid_temperature_c(t_c)) {
        return PHYSLIB_INVALID;
    }
    const float denom = MAGNUS_B + t_c;
    if (denom <= 0.0f) {
        /* t_c <= -243.12 degC: the Magnus pole. Below any real atmosphere. */
        return PHYSLIB_INVALID;
    }
    return MAGNUS_ES0_PA * std::exp((MAGNUS_A * t_c) / denom);
}

/**
 * Dew-point temperature by the Magnus inversion the atlas states verbatim:
 *
 *     γ = ln(RH/100) + 17.62·T/(243.12+T)
 *     T_dew = 243.12 * gamma / (17.62 - gamma)
 *
 * Known answers (published psychrometric tables): 20 degC / 50 % RH -> 9.25 degC;
 * 25 degC / 60 % RH -> 16.69 degC; 30 degC / 80 % RH -> 26.17 degC.
 *
 * @param t_c     air temperature, degC.
 * @param rh_pct  relative humidity, percent, in (0, 100].
 * @return        dew-point temperature in degC, or PHYSLIB_INVALID when
 *                rh_pct <= 0 (ln diverges), rh_pct > 100, t_c is at or below
 *                absolute zero, or gamma reaches the 17.62 pole.
 *
 * Cites: fusion edge "condensation-watch". Named in HANDOFF Phase 4 Task 4.1
 * as dew_point_magnus(T, RH).
 */
inline float dew_point_magnus(float t_c, float rh_pct) {
    if (!is_valid_temperature_c(t_c)) {
        return PHYSLIB_INVALID;
    }
    if (!is_valid_rh_pct(rh_pct) || rh_pct <= 0.0f) {
        return PHYSLIB_INVALID;
    }
    const float denom = MAGNUS_B + t_c;
    if (denom <= 0.0f) {
        return PHYSLIB_INVALID;
    }
    const float gamma =
        std::log(rh_pct / 100.0f) + (MAGNUS_A * t_c) / denom;
    const float pole = MAGNUS_A - gamma;
    if (std::fabs(pole) < 1e-6f) {
        return PHYSLIB_INVALID;
    }
    return (MAGNUS_B * gamma) / pole;
}

/**
 * The condensation decision variable:
 *
 *     dT = T_surface - T_dew        [K]
 *
 * @return dT in K, or PHYSLIB_INVALID if either input is invalid.
 * Cites: fusion edge "condensation-watch".
 */
inline float condensation_margin_k(float t_surface_c, float t_dew_c) {
    if (!is_valid_temperature_c(t_surface_c) || !is_valid(t_dew_c)) {
        return PHYSLIB_INVALID;
    }
    return t_surface_c - t_dew_c;
}

/**
 * The atlas's risk predicate, at its own threshold:
 *     "Risk when T_surface − T_dew < 1.5°C"
 *
 * An invalid margin is NOT a risk: a NaN must never read as an alarm, and it
 * must never read as an all-clear either — check validity separately.
 *
 * Cites: fusion edge "condensation-watch".
 */
inline bool condensation_risk(float margin_k) {
    if (!is_valid(margin_k)) {
        return false;
    }
    return margin_k < CONDENSATION_MARGIN_THRESHOLD_K;
}

/**
 * Result of the "condensation-watch" edge.
 * provides: condensation-risk (EMERGENT — no catalog sensor claims it).
 */
struct CondensationResult {
    /** margin.value = dT = T_surface - T_dew, units "K". */
    EdgeResult margin;
    float t_dew_c;   /* the intermediate quantity, degC, or PHYSLIB_INVALID */
    bool risk;       /* dT < 1.5 K, and margin.valid                        */
};

/**
 * Full "condensation-watch" edge: SHT41 (air T, RH) + MLX90614 (surface T)
 * -> dew point, margin, risk flag, and the emissivity confound as data.
 *
 * The emissivity confound is not decidable from one IR reading — a shiny
 * surface simply reports the wrong number with no signature. So it is carried
 * as a standing warning, and the one thing that IS checkable is checked: an
 * indoor spot reading absurdly far from air temperature is far more likely a
 * reflection off a low-emissivity target than a real surface. That threshold
 * is this firmware's heuristic, not an atlas number.
 *
 * @param t_air_c      air temperature from the SHT41, degC
 * @param rh_pct       relative humidity from the SHT41, %
 * @param t_surface_c  object temperature from the MLX90614, degC
 *
 * Cites: fusion edge "condensation-watch"; math
 *   "Risk when T_surface − T_dew < 1.5°C (T_dew via Magnus:
 *    γ = ln(RH/100) + 17.62·T/(243.12+T))"
 */
inline CondensationResult condensation_watch(float t_air_c, float rh_pct,
                                             float t_surface_c) {
    CondensationResult r;
    r.margin.units = "K";
    r.margin.confound_text = CONFOUND_CONDENSATION_WATCH;
    r.margin.confound = ConfoundState::Standing;
    r.margin.confound_detail = nullptr;
    r.t_dew_c = PHYSLIB_INVALID;
    r.risk = false;

    if (!is_valid_temperature_c(t_air_c)) {
        r.margin.value = PHYSLIB_INVALID;
        r.margin.valid = false;
        r.margin.invalid_reason = "air temperature is not a physical value";
        return r;
    }
    if (!is_valid_rh_pct(rh_pct) || rh_pct <= 0.0f) {
        r.margin.value = PHYSLIB_INVALID;
        r.margin.valid = false;
        r.margin.invalid_reason = "relative humidity outside (0, 100] %";
        return r;
    }
    if (!is_valid_temperature_c(t_surface_c)) {
        r.margin.value = PHYSLIB_INVALID;
        r.margin.valid = false;
        r.margin.invalid_reason = "surface temperature is not a physical value";
        return r;
    }

    r.t_dew_c = dew_point_magnus(t_air_c, rh_pct);
    r.margin.value = condensation_margin_k(t_surface_c, r.t_dew_c);
    r.margin.valid = is_valid(r.margin.value);
    r.margin.invalid_reason =
        r.margin.valid ? nullptr : "Magnus inversion out of domain";
    r.risk = r.margin.valid && condensation_risk(r.margin.value);

    /* Machine-detectable slice of the emissivity confound (heuristic). */
    if (t_surface_c < t_air_c - IR_SUSPECT_BELOW_AIR_K) {
        r.margin.confound = ConfoundState::Detected;
        r.margin.confound_detail =
            "IR spot reads >15 K below air temperature: suspect a shiny "
            "(low-emissivity) target reflecting a cold source, not a cold "
            "surface. Aim at matt tape.";
    } else if (t_surface_c > t_air_c + IR_SUSPECT_ABOVE_AIR_K) {
        r.margin.confound = ConfoundState::Detected;
        r.margin.confound_detail =
            "IR spot reads >5 K above air temperature: suspect a reflected "
            "warm source or a heat source in the field of view, not a wall.";
    }
    return r;
}

/* ===========================================================================
 * CO2 decay -> air changes per hour
 *   Serves fusion edge: "ach-co2-decay"
 *   Atlas math, verbatim:
 *     "ACH = ln((C₁−C_out)/(C₂−C_out)) / Δt[h], C_out ≈ 420 ppm,
 *      after the room empties"
 * ===========================================================================
 */

/**
 * Air changes per hour from a CO2 decay, exactly as the atlas states it:
 *
 *     ACH = ln((C1 - C_out) / (C2 - C_out)) / dt[h]
 *
 * Known answer (HANDOFF Phase 4 Task 4.2): 1400 -> 800 ppm over 1 h with
 * C_out = 420 ppm gives ln(980/380) = 0.9474 h^-1.
 *
 * @param c1_ppm    CO2 at the start of the decay, ppm
 * @param c2_ppm    CO2 at the end of the decay, ppm
 * @param dt_hours  elapsed time, hours
 * @param c_out_ppm outdoor CO2, ppm (default 420 per the atlas)
 * @return          ACH in h^-1, or PHYSLIB_INVALID when
 *                    - dt_hours <= 0,
 *                    - c1_ppm <= c_out_ppm (log of a non-positive number),
 *                    - c2_ppm <= c_out_ppm (division by <= 0),
 *                    - c2_ppm >= c1_ppm (the room did not decay — a rise or a
 *                      flat line has no air-change rate; the caller is told
 *                      which via ach_co2_decay()'s confound detail).
 *
 * Cites: fusion edge "ach-co2-decay". Named in HANDOFF Phase 4 Task 4.1 as
 * ach_from_co2_decay(c1, c2, dt_h, c_out=420).
 */
inline float ach_from_co2_decay(float c1_ppm, float c2_ppm, float dt_hours,
                                float c_out_ppm = CO2_OUTDOOR_DEFAULT_PPM) {
    if (!is_valid(c1_ppm) || !is_valid(c2_ppm) || !is_valid(dt_hours) ||
        !is_valid(c_out_ppm)) {
        return PHYSLIB_INVALID;
    }
    if (dt_hours <= 0.0f) {
        return PHYSLIB_INVALID;
    }
    const float excess1 = c1_ppm - c_out_ppm;
    const float excess2 = c2_ppm - c_out_ppm;
    if (excess1 <= 0.0f || excess2 <= 0.0f) {
        return PHYSLIB_INVALID;
    }
    if (c2_ppm >= c1_ppm) {
        /* Not a decay. A negative or zero "ACH" is not a ventilation rate. */
        return PHYSLIB_INVALID;
    }
    return std::log(excess1 / excess2) / dt_hours;
}

/**
 * Result of the "ach-co2-decay" edge.
 * provides: air-changes-hour (EMERGENT).
 */
struct AchResult {
    /** ach.value = ACH, units "h^-1". */
    EdgeResult ach;
    float c1_ppm;
    float c2_ppm;
    float dt_hours;
    float c_out_ppm;
};

/**
 * Full "ach-co2-decay" edge: one SCD41, two ppm readings and the gap between
 * them -> ACH, with the re-entry / infiltration confound as data.
 *
 * Machine-detectable instances of the confound, both checked here:
 *   - CO2 rose (or did not fall) across the window: somebody re-entered, or
 *     the room never emptied. The atlas's confound names exactly this.
 *   - the window is shorter than ACH_MIN_FIT_WINDOW_H: too few points against
 *     the SCD41's +/-(40 ppm + 5 % of reading) to call the slope a fit.
 * Wind-driven infiltration is NOT detectable without an anemometer, so it
 * stays part of the standing confound text.
 *
 * Cites: fusion edge "ach-co2-decay"; math
 *   "ACH = ln((C₁−C_out)/(C₂−C_out)) / Δt[h], C_out ≈ 420 ppm,
 *    after the room empties"
 */
inline AchResult ach_co2_decay(float c1_ppm, float c2_ppm, float dt_hours,
                               float c_out_ppm = CO2_OUTDOOR_DEFAULT_PPM) {
    AchResult r;
    r.c1_ppm = c1_ppm;
    r.c2_ppm = c2_ppm;
    r.dt_hours = dt_hours;
    r.c_out_ppm = c_out_ppm;
    r.ach.units = "h^-1";
    r.ach.confound_text = CONFOUND_ACH_CO2_DECAY;
    r.ach.confound = ConfoundState::Standing;
    r.ach.confound_detail = nullptr;

    r.ach.value = ach_from_co2_decay(c1_ppm, c2_ppm, dt_hours, c_out_ppm);
    r.ach.valid = is_valid(r.ach.value);
    r.ach.invalid_reason = nullptr;

    if (!r.ach.valid) {
        if (!is_valid(c1_ppm) || !is_valid(c2_ppm) || !is_valid(dt_hours) ||
            !is_valid(c_out_ppm)) {
            r.ach.invalid_reason = "a CO2 or time input was not a number";
        } else if (dt_hours <= 0.0f) {
            r.ach.invalid_reason = "elapsed time must be > 0 h";
        } else if (c1_ppm - c_out_ppm <= 0.0f) {
            r.ach.invalid_reason =
                "start CO2 is not above outdoor CO2: no excess to decay";
        } else if (c2_ppm - c_out_ppm <= 0.0f) {
            r.ach.invalid_reason =
                "end CO2 is not above outdoor CO2: below the outdoor floor";
        } else {
            r.ach.invalid_reason =
                "CO2 did not fall across the window: this is not a decay";
        }
    }

    /* --- machine-detectable confounds ------------------------------------ */
    if (is_valid(c1_ppm) && is_valid(c2_ppm) && c2_ppm >= c1_ppm) {
        r.ach.confound = ConfoundState::Detected;
        r.ach.confound_detail =
            "CO2 rose or stayed flat across the window: someone re-entered "
            "mid-decay, or the room never emptied. The fit is corrupt.";
    } else if (is_valid(dt_hours) && dt_hours > 0.0f &&
               dt_hours < ACH_MIN_FIT_WINDOW_H) {
        r.ach.confound = ConfoundState::Detected;
        r.ach.confound_detail =
            "fit window shorter than 15 min: too few points against the "
            "SCD41's +/-(40 ppm + 5 % of reading) for the slope to mean "
            "anything.";
    }
    return r;
}

/* ===========================================================================
 * Humid air density
 *   Serves fusion edge: "air-density-live"
 *   Atlas math, verbatim:
 *     "ρ = (P_dry·M_d + P_vap·M_v)/(R·T); P_vap from RH × saturation
 *      pressure (Magnus)"
 * ===========================================================================
 */

/**
 * Density of humid air as an ideal-gas mixture of dry air and water vapour:
 *
 *     P_vap = (RH/100) * e_s(T)        [Pa], e_s from Magnus above
 *     P_dry = P - P_vap                [Pa]
 *     rho   = (P_dry*M_d + P_vap*M_v) / (R*T)     [kg/m3]
 *
 * with M_d = 0.0289652 kg/mol (dry air), M_v = 0.018016 kg/mol (water vapour),
 * R = 8.31446 J/(mol*K) and T in kelvin.
 *
 * Known answer: dry air at 15 degC and 101325 Pa gives 1.2250 kg/m3, the ICAO
 * standard sea-level density.
 *
 * @param p_pa    absolute pressure, Pa (a BME280 reports Pa via readPressure())
 * @param t_c     temperature, degC
 * @param rh_pct  relative humidity, percent, in [0, 100]
 * @return        density in kg/m3, or PHYSLIB_INVALID when p_pa <= 0, t_c is
 *                at or below absolute zero, rh_pct is outside [0, 100], or the
 *                vapour pressure would exceed the total pressure (which means
 *                the inputs are mutually impossible).
 *
 * Cites: fusion edge "air-density-live". Named in HANDOFF Phase 4 Task 4.1 as
 * air_density(P, T, RH).
 */
inline float air_density(float p_pa, float t_c, float rh_pct) {
    if (!is_valid(p_pa) || p_pa <= 0.0f) {
        return PHYSLIB_INVALID;
    }
    if (!is_valid_temperature_c(t_c)) {
        return PHYSLIB_INVALID;
    }
    if (!is_valid_rh_pct(rh_pct)) {
        return PHYSLIB_INVALID;
    }
    const float t_kelvin = t_c - ABSOLUTE_ZERO_C;
    if (t_kelvin <= 0.0f) {
        return PHYSLIB_INVALID;
    }
    const float es_pa = saturation_vapour_pressure_pa(t_c);
    if (!is_valid(es_pa)) {
        return PHYSLIB_INVALID;
    }
    const float p_vap = (rh_pct / 100.0f) * es_pa;
    const float p_dry = p_pa - p_vap;
    if (p_dry < 0.0f) {
        /* Saturated vapour alone would exceed the measured total pressure:
         * the P/T/RH triple is not a physically possible atmosphere. */
        return PHYSLIB_INVALID;
    }
    return (p_dry * M_DRY_AIR + p_vap * M_WATER_VAPOUR) /
           (R_UNIVERSAL * t_kelvin);
}

/**
 * Result of the "air-density-live" edge.
 * provides: air-density (EMERGENT).
 */
struct AirDensityResult {
    /** rho.value = air density, units "kg/m3". */
    EdgeResult rho;
    float p_vap_pa;  /* the Magnus intermediate, Pa */
    float p_dry_pa;  /* Pa                          */
};

/**
 * Full "air-density-live" edge: one BME280 -> rho, with the self-heating
 * confound as data.
 *
 * Machine-detectable instance of the confound: pass a temperature from a
 * thermometer that is NOT on the combo board (the SHT41 on a flying lead, the
 * SCD41, anything thermally separate). If the BME280's own channel sits more
 * than SELF_HEATING_LIMIT_K above that reference, the board is heating itself
 * and rho is biased low. Pass PHYSLIB_INVALID (the default) when no reference
 * exists — the check is then skipped and the confound stays Standing, which is
 * the honest answer for a single-board build.
 *
 * @param p_pa           BME280 pressure, Pa
 * @param t_c            BME280 temperature, degC
 * @param rh_pct         BME280 relative humidity, %
 * @param t_reference_c  temperature from a thermally separate sensor, degC,
 *                       or PHYSLIB_INVALID for "no reference available"
 *
 * Cites: fusion edge "air-density-live"; math
 *   "ρ = (P_dry·M_d + P_vap·M_v)/(R·T); P_vap from RH × saturation pressure
 *    (Magnus)"
 */
inline AirDensityResult air_density_live(float p_pa, float t_c, float rh_pct,
                                         float t_reference_c = PHYSLIB_INVALID) {
    AirDensityResult r;
    r.rho.units = "kg/m3";
    r.rho.confound_text = CONFOUND_AIR_DENSITY_LIVE;
    r.rho.confound = ConfoundState::Standing;
    r.rho.confound_detail = nullptr;
    r.p_vap_pa = PHYSLIB_INVALID;
    r.p_dry_pa = PHYSLIB_INVALID;

    r.rho.value = air_density(p_pa, t_c, rh_pct);
    r.rho.valid = is_valid(r.rho.value);
    r.rho.invalid_reason = nullptr;

    if (!r.rho.valid) {
        if (!is_valid(p_pa) || p_pa <= 0.0f) {
            r.rho.invalid_reason = "absolute pressure must be > 0 Pa";
        } else if (!is_valid_temperature_c(t_c)) {
            r.rho.invalid_reason = "temperature is not a physical value";
        } else if (!is_valid_rh_pct(rh_pct)) {
            r.rho.invalid_reason = "relative humidity outside [0, 100] %";
        } else {
            r.rho.invalid_reason =
                "vapour pressure exceeds total pressure: impossible P/T/RH";
        }
    } else {
        const float es_pa = saturation_vapour_pressure_pa(t_c);
        r.p_vap_pa = (rh_pct / 100.0f) * es_pa;
        r.p_dry_pa = p_pa - r.p_vap_pa;
    }

    /* --- machine-detectable confound ------------------------------------- */
    if (is_valid_temperature_c(t_reference_c) && is_valid_temperature_c(t_c) &&
        (t_c - t_reference_c) > SELF_HEATING_LIMIT_K) {
        r.rho.confound = ConfoundState::Detected;
        r.rho.confound_detail =
            "combo-board temperature is more than 1 K above the separate "
            "reference thermometer: this is BME280 self-heating, and rho is "
            "biased low. Read fast, sleep long, or move the thermometer.";
    }
    return r;
}

}  // namespace physlib

#endif  /* PHYSLIB_H */
