/*
 * test_physlib.cpp — host-side known-answer tests for physlib.h.
 *
 *   pio test -e native
 *
 * Runs on the desktop with Unity, compiling the exact header the three ESP32
 * examples compile. No Arduino, no Wire, no board.
 *
 * The expected values here come from outside this repository — published
 * psychrometric tables, the ICAO standard atmosphere, and arithmetic done by
 * hand — so that a wrong formula fails the test instead of agreeing with
 * itself. Nothing below is asserted against physlib's own output.
 *
 * Cited edges: condensation-watch, ach-co2-decay, air-density-live
 * (sensor-universe/data/fusion.py).
 */

#include <unity.h>

#include "physlib.h"

using namespace physlib;

void setUp(void) {}
void tearDown(void) {}

/* ===========================================================================
 * Magnus saturation vapour pressure
 * ===========================================================================
 */

static void test_saturation_pressure_known_values(void) {
    /* e_s(0 degC) = 611.2 Pa by definition of the Magnus form used here. */
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 611.2f, saturation_vapour_pressure_pa(0.0f));

    /* Published saturation vapour pressure over water:
     *   20 degC -> 2339 Pa, 30 degC -> 4246 Pa (CRC / Smithsonian tables).
     * The Magnus fit is not the table, so allow 1 % — which is far tighter
     * than any error a wrong coefficient would produce. */
    const float es20 = saturation_vapour_pressure_pa(20.0f);
    TEST_ASSERT_FLOAT_WITHIN(2339.0f * 0.01f, 2339.0f, es20);

    const float es30 = saturation_vapour_pressure_pa(30.0f);
    TEST_ASSERT_FLOAT_WITHIN(4246.0f * 0.01f, 4246.0f, es30);

    /* Monotonic in temperature — a sign error would break this. */
    TEST_ASSERT_TRUE(saturation_vapour_pressure_pa(10.0f) < es20);
    TEST_ASSERT_TRUE(es20 < es30);
}

static void test_saturation_pressure_rejects_nonsense(void) {
    TEST_ASSERT_FALSE(is_valid(saturation_vapour_pressure_pa(-273.15f)));
    TEST_ASSERT_FALSE(is_valid(saturation_vapour_pressure_pa(-300.0f)));
    TEST_ASSERT_FALSE(is_valid(saturation_vapour_pressure_pa(PHYSLIB_INVALID)));
}

/* ===========================================================================
 * Magnus dew point — fusion edge "condensation-watch"
 * ===========================================================================
 */

static void test_dew_point_published_values(void) {
    /* Published psychrometric dew points (standard tables, sea level):
     *   20 degC / 50 % RH -> 9.3 degC
     *   25 degC / 60 % RH -> 16.7 degC
     *   30 degC / 80 % RH -> 26.2 degC
     * The Magnus inversion the atlas specifies reproduces these to better
     * than 0.1 K; 0.1 is the tolerance, not the agreement. */
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 9.3f, dew_point_magnus(20.0f, 50.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 16.7f, dew_point_magnus(25.0f, 60.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1f, 26.2f, dew_point_magnus(30.0f, 80.0f));

    /* HANDOFF Phase 4 Task 4.2's own known answer, quoted:
     * "Magnus dew point of 20 degC/50 % RH ~= 9.3 degC". */
    TEST_ASSERT_FLOAT_WITHIN(0.05f, 9.25f, dew_point_magnus(20.0f, 50.0f));

    /* Below freezing, still over water: -5 degC / 70 % RH -> about -9.6 degC. */
    TEST_ASSERT_FLOAT_WITHIN(0.15f, -9.6f, dew_point_magnus(-5.0f, 70.0f));
}

static void test_dew_point_at_saturation_equals_temperature(void) {
    /* At 100 % RH the dew point IS the air temperature. gamma reduces to
     * 17.62*T/(243.12+T), and the inversion must return T exactly. */
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 21.0f, dew_point_magnus(21.0f, 100.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 0.0f, dew_point_magnus(0.0f, 100.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.01f, -12.0f, dew_point_magnus(-12.0f, 100.0f));
}

static void test_dew_point_is_monotonic_and_bounded(void) {
    /* Drier air has a lower dew point, and the dew point never exceeds the
     * air temperature. Both would break under a sign or bracket error. */
    const float t = 22.0f;
    float previous = -1000.0f;
    for (float rh = 10.0f; rh <= 100.0f; rh += 10.0f) {
        const float td = dew_point_magnus(t, rh);
        TEST_ASSERT_TRUE(is_valid(td));
        TEST_ASSERT_TRUE(td > previous);
        TEST_ASSERT_TRUE(td <= t + 0.01f);
        previous = td;
    }
}

static void test_dew_point_rejects_nonsense(void) {
    TEST_ASSERT_FALSE(is_valid(dew_point_magnus(20.0f, 0.0f)));    /* ln(0)   */
    TEST_ASSERT_FALSE(is_valid(dew_point_magnus(20.0f, -1.0f)));   /* RH < 0  */
    TEST_ASSERT_FALSE(is_valid(dew_point_magnus(20.0f, 101.0f)));  /* RH > 100*/
    TEST_ASSERT_FALSE(is_valid(dew_point_magnus(-273.15f, 50.0f)));/* 0 K     */
    TEST_ASSERT_FALSE(is_valid(dew_point_magnus(-400.0f, 50.0f))); /* below 0K*/
    TEST_ASSERT_FALSE(is_valid(dew_point_magnus(PHYSLIB_INVALID, 50.0f)));
    TEST_ASSERT_FALSE(is_valid(dew_point_magnus(20.0f, PHYSLIB_INVALID)));
}

/* ===========================================================================
 * Condensation margin and the 1.5 degC risk predicate
 * ===========================================================================
 */

static void test_condensation_margin_and_threshold(void) {
    /* 20 degC / 50 % RH -> T_dew = 9.25 degC. */
    const float t_dew = dew_point_magnus(20.0f, 50.0f);

    /* A surface 0.75 K above the dew point is inside the atlas's 1.5 degC
     * threshold: risk. */
    const float margin_wet = condensation_margin_k(t_dew + 0.75f, t_dew);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 0.75f, margin_wet);
    TEST_ASSERT_TRUE(condensation_risk(margin_wet));

    /* A surface 5 K above it is clear. */
    const float margin_dry = condensation_margin_k(t_dew + 5.0f, t_dew);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 5.0f, margin_dry);
    TEST_ASSERT_FALSE(condensation_risk(margin_dry));

    /* The threshold sits exactly where the atlas puts it: strictly below
     * 1.5 K is risk, 1.5 K itself is not. */
    TEST_ASSERT_TRUE(condensation_risk(1.49f));
    TEST_ASSERT_FALSE(condensation_risk(1.50f));
    TEST_ASSERT_FALSE(condensation_risk(1.51f));

    /* A NaN margin is neither an alarm nor an all-clear; the predicate must
     * not raise an alarm on it. */
    TEST_ASSERT_FALSE(condensation_risk(PHYSLIB_INVALID));
}

static void test_condensation_watch_edge(void) {
    /* Bathroom wall: 20 degC air at 50 % RH, wall at 10 degC.
     * T_dew = 9.25 degC, margin = 0.75 K -> risk. */
    const CondensationResult r = condensation_watch(20.0f, 50.0f, 10.0f);
    TEST_ASSERT_TRUE(r.margin.valid);
    TEST_ASSERT_FLOAT_WITHIN(0.05f, 9.25f, r.t_dew_c);
    TEST_ASSERT_FLOAT_WITHIN(0.05f, 0.75f, r.margin.value);
    TEST_ASSERT_TRUE(r.risk);
    TEST_ASSERT_EQUAL_STRING("K", r.margin.units);
    TEST_ASSERT_NULL(r.margin.invalid_reason);

    /* Same room, a wall at 18 degC: margin 8.75 K, no risk. */
    const CondensationResult clear = condensation_watch(20.0f, 50.0f, 18.0f);
    TEST_ASSERT_TRUE(clear.margin.valid);
    TEST_ASSERT_FLOAT_WITHIN(0.05f, 8.75f, clear.margin.value);
    TEST_ASSERT_FALSE(clear.risk);
}

static void test_condensation_watch_invalid_inputs(void) {
    const CondensationResult bad_rh = condensation_watch(20.0f, 0.0f, 10.0f);
    TEST_ASSERT_FALSE(bad_rh.margin.valid);
    TEST_ASSERT_FALSE(is_valid(bad_rh.margin.value));
    TEST_ASSERT_NOT_NULL(bad_rh.margin.invalid_reason);
    TEST_ASSERT_FALSE(bad_rh.risk);

    const CondensationResult bad_t = condensation_watch(-273.15f, 50.0f, 10.0f);
    TEST_ASSERT_FALSE(bad_t.margin.valid);
    TEST_ASSERT_NOT_NULL(bad_t.margin.invalid_reason);

    const CondensationResult bad_surface =
        condensation_watch(20.0f, 50.0f, PHYSLIB_INVALID);
    TEST_ASSERT_FALSE(bad_surface.margin.valid);
    TEST_ASSERT_NOT_NULL(bad_surface.margin.invalid_reason);

    /* Even a refusal carries the standing confound text. */
    TEST_ASSERT_NOT_NULL(bad_rh.margin.confound_text);
}

static void test_condensation_watch_emissivity_heuristic(void) {
    /* A plausible indoor wall: nothing detected, standing confound only. */
    const CondensationResult ok = condensation_watch(20.0f, 50.0f, 16.0f);
    TEST_ASSERT_EQUAL(ConfoundState::Standing, ok.margin.confound);
    TEST_ASSERT_NULL(ok.margin.confound_detail);

    /* An IR spot 25 K below air temperature indoors: shiny target. */
    const CondensationResult shiny = condensation_watch(20.0f, 50.0f, -5.0f);
    TEST_ASSERT_EQUAL(ConfoundState::Detected, shiny.margin.confound);
    TEST_ASSERT_NOT_NULL(shiny.margin.confound_detail);

    /* An IR spot 10 K above air temperature: reflected warm source. */
    const CondensationResult hot = condensation_watch(20.0f, 50.0f, 30.0f);
    TEST_ASSERT_EQUAL(ConfoundState::Detected, hot.margin.confound);
    TEST_ASSERT_NOT_NULL(hot.margin.confound_detail);
}

/* ===========================================================================
 * CO2 decay -> ACH — fusion edge "ach-co2-decay"
 * ===========================================================================
 */

static void test_ach_handoff_known_answer(void) {
    /* HANDOFF Phase 4 Task 4.2, quoted: "ACH of a decay from 1400->800 ppm in
     * 1 h with 420 ppm outside ~= 0.95 h^-1".
     * By hand: ln((1400-420)/(800-420)) / 1 = ln(980/380) = ln(2.5789474)
     *        = 0.947380 h^-1. */
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.947380f,
                             ach_from_co2_decay(1400.0f, 800.0f, 1.0f, 420.0f));

    /* The 420 ppm default must be the same number. */
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.947380f,
                             ach_from_co2_decay(1400.0f, 800.0f, 1.0f));
}

static void test_ach_second_hand_computed_case(void) {
    /* By hand: ln((2000-400)/(1000-400)) / 2 h = ln(1600/600)/2
     *        = ln(2.6666667)/2 = 0.9808293/2 = 0.4904146 h^-1. */
    TEST_ASSERT_FLOAT_WITHIN(
        0.001f, 0.4904146f,
        ach_from_co2_decay(2000.0f, 1000.0f, 2.0f, 400.0f));

    /* Halving the window doubles the rate — a 1/dt error would not survive. */
    const float half = ach_from_co2_decay(2000.0f, 1000.0f, 1.0f, 400.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.9808293f, half);

    /* C_out matters: with a 420 ppm outdoor level the same pair of readings
     * gives ln(1580/580)/2 = ln(2.7241379)/2 = 1.0021795/2 = 0.5010898. */
    TEST_ASSERT_FLOAT_WITHIN(
        0.001f, 0.5010898f,
        ach_from_co2_decay(2000.0f, 1000.0f, 2.0f, 420.0f));
}

static void test_ach_rejects_nonsense(void) {
    /* dt <= 0 */
    TEST_ASSERT_FALSE(is_valid(ach_from_co2_decay(1400.0f, 800.0f, 0.0f)));
    TEST_ASSERT_FALSE(is_valid(ach_from_co2_decay(1400.0f, 800.0f, -1.0f)));
    /* C1 at or below outdoor: no excess CO2 to decay */
    TEST_ASSERT_FALSE(is_valid(ach_from_co2_decay(420.0f, 410.0f, 1.0f)));
    TEST_ASSERT_FALSE(is_valid(ach_from_co2_decay(300.0f, 250.0f, 1.0f)));
    /* C2 at or below outdoor: the room cannot go below the outside air */
    TEST_ASSERT_FALSE(is_valid(ach_from_co2_decay(1400.0f, 420.0f, 1.0f)));
    TEST_ASSERT_FALSE(is_valid(ach_from_co2_decay(1400.0f, 300.0f, 1.0f)));
    /* CO2 rose, or did not move: that is not a decay */
    TEST_ASSERT_FALSE(is_valid(ach_from_co2_decay(800.0f, 1400.0f, 1.0f)));
    TEST_ASSERT_FALSE(is_valid(ach_from_co2_decay(900.0f, 900.0f, 1.0f)));
    /* NaN in, NaN out */
    TEST_ASSERT_FALSE(
        is_valid(ach_from_co2_decay(PHYSLIB_INVALID, 800.0f, 1.0f)));
    TEST_ASSERT_FALSE(
        is_valid(ach_from_co2_decay(1400.0f, PHYSLIB_INVALID, 1.0f)));
    TEST_ASSERT_FALSE(
        is_valid(ach_from_co2_decay(1400.0f, 800.0f, PHYSLIB_INVALID)));
}

static void test_ach_edge_result(void) {
    const AchResult r = ach_co2_decay(1400.0f, 800.0f, 1.0f);
    TEST_ASSERT_TRUE(r.ach.valid);
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.947380f, r.ach.value);
    TEST_ASSERT_EQUAL_STRING("h^-1", r.ach.units);
    TEST_ASSERT_NULL(r.ach.invalid_reason);
    TEST_ASSERT_EQUAL(ConfoundState::Standing, r.ach.confound);
    TEST_ASSERT_NULL(r.ach.confound_detail);
    TEST_ASSERT_NOT_NULL(r.ach.confound_text);
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 420.0f, r.c_out_ppm);
}

static void test_ach_confound_co2_rose(void) {
    /* Someone walked back in: CO2 climbed across the window. */
    const AchResult r = ach_co2_decay(800.0f, 1100.0f, 1.0f);
    TEST_ASSERT_FALSE(r.ach.valid);
    TEST_ASSERT_NOT_NULL(r.ach.invalid_reason);
    TEST_ASSERT_EQUAL(ConfoundState::Detected, r.ach.confound);
    TEST_ASSERT_NOT_NULL(r.ach.confound_detail);
}

static void test_ach_confound_window_too_short(void) {
    /* A genuine decay, but sampled over 6 minutes (0.1 h): the value computes,
     * and the result says out loud that the window cannot support a fit. */
    const AchResult r = ach_co2_decay(1400.0f, 1300.0f, 0.1f);
    TEST_ASSERT_TRUE(r.ach.valid);
    TEST_ASSERT_EQUAL(ConfoundState::Detected, r.ach.confound);
    TEST_ASSERT_NOT_NULL(r.ach.confound_detail);

    /* Half an hour is long enough: nothing detected. */
    const AchResult ok = ach_co2_decay(1400.0f, 1100.0f, 0.5f);
    TEST_ASSERT_TRUE(ok.ach.valid);
    TEST_ASSERT_EQUAL(ConfoundState::Standing, ok.ach.confound);
    TEST_ASSERT_NULL(ok.ach.confound_detail);
}

static void test_ach_invalid_reasons_are_specific(void) {
    TEST_ASSERT_NOT_NULL(ach_co2_decay(1400.0f, 800.0f, 0.0f).ach.invalid_reason);
    TEST_ASSERT_NOT_NULL(ach_co2_decay(420.0f, 410.0f, 1.0f).ach.invalid_reason);
    TEST_ASSERT_NOT_NULL(ach_co2_decay(1400.0f, 400.0f, 1.0f).ach.invalid_reason);
}

/* ===========================================================================
 * Humid air density — fusion edge "air-density-live"
 * ===========================================================================
 */

static void test_air_density_icao_standard(void) {
    /* The ICAO standard atmosphere at sea level: 15 degC, 101325 Pa, dry air
     * -> 1.225 kg/m3.
     *
     * Tolerance 0.002 kg/m3 (0.16 %), because ICAO's figure is defined with
     * M_d = 0.0289644 kg/mol and R = 8.31432 J/(mol*K) while this library uses
     * the CIPM-2007 values the atlas names (0.0289652, 8.31446). Those two
     * constant sets differ by ~3e-5 relative, and single-precision arithmetic
     * adds another ~1e-6. Anything larger than 0.002 is a real error, not a
     * constants choice. */
    const float rho = air_density(101325.0f, 15.0f, 0.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.002f, 1.225f, rho);
}

static void test_air_density_other_published_points(void) {
    /* Dry air at 0 degC and 101325 Pa: 1.2922 kg/m3 (CRC Handbook). */
    TEST_ASSERT_FLOAT_WITHIN(0.002f, 1.2922f,
                             air_density(101325.0f, 0.0f, 0.0f));

    /* Dry air at 25 degC and 101325 Pa: 1.1839 kg/m3 (CRC Handbook). */
    TEST_ASSERT_FLOAT_WITHIN(0.002f, 1.1839f,
                             air_density(101325.0f, 25.0f, 0.0f));

    /* Saturated air at 20 degC and 101325 Pa: about 1.1936 kg/m3 (CIPM
     * moist-air formula gives 1.1941; the ideal-gas mixture the atlas
     * specifies is ~0.05 % lighter, hence the 0.002 window). */
    TEST_ASSERT_FLOAT_WITHIN(0.002f, 1.1936f,
                             air_density(101325.0f, 20.0f, 100.0f));
}

static void test_air_density_humid_is_lighter_than_dry(void) {
    /* Water vapour (18.016 g/mol) is lighter than dry air (28.9652 g/mol), so
     * at the same pressure and temperature humid air is LESS dense. Getting
     * the mixture backwards is the classic error; this catches it. */
    const float dry = air_density(101325.0f, 25.0f, 0.0f);
    const float humid = air_density(101325.0f, 25.0f, 100.0f);
    TEST_ASSERT_TRUE(is_valid(dry));
    TEST_ASSERT_TRUE(is_valid(humid));
    TEST_ASSERT_TRUE(humid < dry);
    /* and the effect is small: under 1.5 % at 25 degC */
    TEST_ASSERT_TRUE((dry - humid) / dry < 0.015f);
}

static void test_air_density_responds_to_pressure_and_temperature(void) {
    /* Halving the pressure halves the density at fixed T (dry air). */
    const float p_full = air_density(100000.0f, 20.0f, 0.0f);
    const float p_half = air_density(50000.0f, 20.0f, 0.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.001f, p_full / 2.0f, p_half);

    /* Hotter air is thinner. */
    TEST_ASSERT_TRUE(air_density(101325.0f, 35.0f, 0.0f) <
                     air_density(101325.0f, 5.0f, 0.0f));
}

static void test_air_density_rejects_nonsense(void) {
    TEST_ASSERT_FALSE(is_valid(air_density(0.0f, 20.0f, 50.0f)));      /* P=0  */
    TEST_ASSERT_FALSE(is_valid(air_density(-1000.0f, 20.0f, 50.0f)));  /* P<0  */
    TEST_ASSERT_FALSE(is_valid(air_density(101325.0f, -273.15f, 50.0f)));
    TEST_ASSERT_FALSE(is_valid(air_density(101325.0f, -300.0f, 50.0f)));
    TEST_ASSERT_FALSE(is_valid(air_density(101325.0f, 20.0f, 101.0f)));
    TEST_ASSERT_FALSE(is_valid(air_density(101325.0f, 20.0f, -1.0f)));
    TEST_ASSERT_FALSE(is_valid(air_density(PHYSLIB_INVALID, 20.0f, 50.0f)));
    /* Mutually impossible: 90 degC saturated vapour alone exceeds 1000 Pa
     * of total pressure, so P_dry would be negative. */
    TEST_ASSERT_FALSE(is_valid(air_density(1000.0f, 90.0f, 100.0f)));
}

static void test_air_density_edge_result(void) {
    const AirDensityResult r = air_density_live(101325.0f, 15.0f, 0.0f);
    TEST_ASSERT_TRUE(r.rho.valid);
    TEST_ASSERT_FLOAT_WITHIN(0.002f, 1.225f, r.rho.value);
    TEST_ASSERT_EQUAL_STRING("kg/m3", r.rho.units);
    TEST_ASSERT_NULL(r.rho.invalid_reason);
    TEST_ASSERT_NOT_NULL(r.rho.confound_text);
    /* No reference thermometer supplied: the self-heating check cannot run. */
    TEST_ASSERT_EQUAL(ConfoundState::Standing, r.rho.confound);
    TEST_ASSERT_NULL(r.rho.confound_detail);

    /* Dry air: P_vap is zero and P_dry is the whole of P. */
    TEST_ASSERT_FLOAT_WITHIN(0.001f, 0.0f, r.p_vap_pa);
    TEST_ASSERT_FLOAT_WITHIN(1.0f, 101325.0f, r.p_dry_pa);

    /* Humid air at 20 degC / 60 % RH: P_vap = 0.6 * e_s(20) = 0.6 * 2332.8
     * = 1399.7 Pa, and P_dry is the remainder. */
    const AirDensityResult humid = air_density_live(101325.0f, 20.0f, 60.0f);
    TEST_ASSERT_TRUE(humid.rho.valid);
    TEST_ASSERT_FLOAT_WITHIN(20.0f, 1400.0f, humid.p_vap_pa);
    TEST_ASSERT_FLOAT_WITHIN(20.0f, 101325.0f - 1400.0f, humid.p_dry_pa);
}

static void test_air_density_self_heating_confound(void) {
    /* Board reads 23.0 degC while a separate thermometer says 21.0: a 2 K gap,
     * over the 1 K the confound allows. Detected. */
    const AirDensityResult hot =
        air_density_live(101325.0f, 23.0f, 40.0f, 21.0f);
    TEST_ASSERT_TRUE(hot.rho.valid);
    TEST_ASSERT_EQUAL(ConfoundState::Detected, hot.rho.confound);
    TEST_ASSERT_NOT_NULL(hot.rho.confound_detail);

    /* A 0.5 K gap is within the noise: standing only. */
    const AirDensityResult ok =
        air_density_live(101325.0f, 21.5f, 40.0f, 21.0f);
    TEST_ASSERT_EQUAL(ConfoundState::Standing, ok.rho.confound);
    TEST_ASSERT_NULL(ok.rho.confound_detail);

    /* The board reading COLDER than the reference is not self-heating. */
    const AirDensityResult cold =
        air_density_live(101325.0f, 19.0f, 40.0f, 21.0f);
    TEST_ASSERT_EQUAL(ConfoundState::Standing, cold.rho.confound);
}

static void test_air_density_invalid_reasons_are_specific(void) {
    TEST_ASSERT_NOT_NULL(air_density_live(0.0f, 20.0f, 50.0f).rho.invalid_reason);
    TEST_ASSERT_NOT_NULL(
        air_density_live(101325.0f, -300.0f, 50.0f).rho.invalid_reason);
    TEST_ASSERT_NOT_NULL(
        air_density_live(101325.0f, 20.0f, 150.0f).rho.invalid_reason);
    TEST_ASSERT_NOT_NULL(
        air_density_live(1000.0f, 90.0f, 100.0f).rho.invalid_reason);
}

/* ===========================================================================
 * Cross-checks between the edges
 * ===========================================================================
 */

static void test_dew_point_and_vapour_pressure_agree(void) {
    /* The dew point is by definition the temperature at which the current
     * vapour pressure becomes the saturation pressure. So
     *   e_s(T_dew) == (RH/100) * e_s(T)
     * must hold for the two functions that the two edges share. This links
     * condensation-watch and air-density-live: if they disagree, one of them
     * is using different coefficients. */
    const float t = 24.0f;
    const float rh = 45.0f;
    const float td = dew_point_magnus(t, rh);
    const float e_actual = (rh / 100.0f) * saturation_vapour_pressure_pa(t);
    const float e_at_dew = saturation_vapour_pressure_pa(td);
    TEST_ASSERT_FLOAT_WITHIN(e_actual * 0.002f, e_actual, e_at_dew);
}

static void test_every_confound_text_is_present(void) {
    /* A result must never reach the caller without the atlas's own caveat,
     * on any path, valid or not. */
    TEST_ASSERT_NOT_NULL(condensation_watch(20.0f, 50.0f, 10.0f).margin.confound_text);
    TEST_ASSERT_NOT_NULL(condensation_watch(20.0f, 0.0f, 10.0f).margin.confound_text);
    TEST_ASSERT_NOT_NULL(ach_co2_decay(1400.0f, 800.0f, 1.0f).ach.confound_text);
    TEST_ASSERT_NOT_NULL(ach_co2_decay(1400.0f, 800.0f, 0.0f).ach.confound_text);
    TEST_ASSERT_NOT_NULL(air_density_live(101325.0f, 15.0f, 0.0f).rho.confound_text);
    TEST_ASSERT_NOT_NULL(air_density_live(0.0f, 15.0f, 0.0f).rho.confound_text);
}

int main(int argc, char **argv) {
    (void)argc;
    (void)argv;

    UNITY_BEGIN();

    RUN_TEST(test_saturation_pressure_known_values);
    RUN_TEST(test_saturation_pressure_rejects_nonsense);

    RUN_TEST(test_dew_point_published_values);
    RUN_TEST(test_dew_point_at_saturation_equals_temperature);
    RUN_TEST(test_dew_point_is_monotonic_and_bounded);
    RUN_TEST(test_dew_point_rejects_nonsense);

    RUN_TEST(test_condensation_margin_and_threshold);
    RUN_TEST(test_condensation_watch_edge);
    RUN_TEST(test_condensation_watch_invalid_inputs);
    RUN_TEST(test_condensation_watch_emissivity_heuristic);

    RUN_TEST(test_ach_handoff_known_answer);
    RUN_TEST(test_ach_second_hand_computed_case);
    RUN_TEST(test_ach_rejects_nonsense);
    RUN_TEST(test_ach_edge_result);
    RUN_TEST(test_ach_confound_co2_rose);
    RUN_TEST(test_ach_confound_window_too_short);
    RUN_TEST(test_ach_invalid_reasons_are_specific);

    RUN_TEST(test_air_density_icao_standard);
    RUN_TEST(test_air_density_other_published_points);
    RUN_TEST(test_air_density_humid_is_lighter_than_dry);
    RUN_TEST(test_air_density_responds_to_pressure_and_temperature);
    RUN_TEST(test_air_density_rejects_nonsense);
    RUN_TEST(test_air_density_edge_result);
    RUN_TEST(test_air_density_self_heating_confound);
    RUN_TEST(test_air_density_invalid_reasons_are_specific);

    RUN_TEST(test_dew_point_and_vapour_pressure_agree);
    RUN_TEST(test_every_confound_text_is_present);

    return UNITY_END();
}
