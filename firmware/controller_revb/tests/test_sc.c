/* Host tests for the portable Rev B firmware logic (no HAL).  Build: see tests/CMakeLists.txt */
#include <math.h>
#include <stdio.h>
#include <string.h>

#include "sc_canproto.h"
#include "sc_config.h"
#include "sc_power.h"
#include "sc_referee.h"
#include "sc_sensing.h"
#include "sc_supervisor.h"

static int fails, checks;
#define CHECK(c, ...) do { checks++; if (!(c)) { fails++; printf("FAIL %s:%d: ", __FILE__, __LINE__); printf(__VA_ARGS__); printf("\n"); } } while (0)
#define NEAR(a, b, tol) (fabsf((float)(a) - (float)(b)) <= (tol))

/* ---------- CRC: compare with the first entries of the DJI lookup tables */
static uint16_t tbl16(uint8_t k)
{
    uint16_t c = k;
    for (int i = 0; i < 8; i++) c = (c & 1u) ? (uint16_t)((c >> 1) ^ 0x8408u) : (uint16_t)(c >> 1);
    return c;
}

static void test_crc(void)
{
    static const uint8_t t8[8] = {0x00, 0x5e, 0xbc, 0xe2, 0x61, 0x3f, 0xdd, 0x83};
    static const uint16_t t16[8] = {0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf};
    for (int i = 0; i < 8; i++) {
        /* DJI table form: crc8 = T8[crc ^ b] with init 0xFF -> one byte (i ^ 0xFF) gives T8[i] */
        uint8_t b = (uint8_t)(i ^ 0xFF);
        CHECK(sc_crc8(&b, 1) == t8[i], "crc8 table %d", i);
        CHECK(tbl16((uint8_t)i) == t16[i], "crc16 table %d", i);
        /* DJI table form: crc16 = (crc >> 8) ^ T16[(crc ^ b) & 0xFF] with init 0xFFFF */
        uint8_t w = (uint8_t)i;
        CHECK(sc_crc16(&w, 1) == (uint16_t)(0x00FFu ^ tbl16((uint8_t)(0xFFu ^ (uint8_t)i))), "crc16 byte %d", i);
    }
}

/* ---------- referee frames */
static int make_frame(uint8_t *f, uint16_t cmd, const uint8_t *data, uint16_t len, uint8_t seq)
{
    f[0] = 0xA5;
    f[1] = (uint8_t)len;
    f[2] = (uint8_t)(len >> 8);
    f[3] = seq;
    f[4] = sc_crc8(f, 4);
    f[5] = (uint8_t)cmd;
    f[6] = (uint8_t)(cmd >> 8);
    memcpy(&f[7], data, len);
    uint16_t c = sc_crc16(f, 7u + len);
    f[7 + len] = (uint8_t)c;
    f[8 + len] = (uint8_t)(c >> 8);
    return 9 + len;
}

static void feed(sc_referee_t *r, const uint8_t *p, int n, uint32_t now)
{
    for (int i = 0; i < n; i++) {
        (void)sc_referee_feed(r, p[i], now);
    }
}

static void test_referee(void)
{
    sc_referee_t r;
    sc_referee_init(&r);
    uint8_t st[13] = {3, 1, 200, 0, 200, 0, 40, 0, 0x90, 0x01, 60, 0, 0x07};   /* limit 60 W, chassis on */
    uint8_t pw[14] = {0};
    pw[8] = 25;                                                                /* buffer 25 J */
    uint8_t f[64];
    uint8_t junk[] = {0x00, 0xA5, 0x12, 0x34, 0xFF};
    feed(&r, junk, sizeof(junk), 10);
    int n = make_frame(f, 0x0201, st, 13, 1);
    feed(&r, f, n, 100);
    n = make_frame(f, 0x0202, pw, 14, 2);
    feed(&r, f, n, 110);
    CHECK(r.data.have_status && r.data.chassis_power_limit == 60, "limit %u", r.data.chassis_power_limit);
    CHECK(r.data.chassis_output_on, "chassis on");
    CHECK(r.data.have_power && r.data.buffer_energy == 25, "buffer %u", r.data.buffer_energy);
    /* corrupted CRC16 must be ignored */
    st[10] = 80;
    n = make_frame(f, 0x0201, st, 13, 3);
    f[n - 1] ^= 0x55;
    feed(&r, f, n, 200);
    CHECK(r.data.chassis_power_limit == 60 && r.data.crc_errors >= 1, "crc reject");
    /* other command ids pass through without touching the data */
    uint8_t other[20] = {0};
    n = make_frame(f, 0x0003, other, 20, 4);
    feed(&r, f, n, 210);
    CHECK(r.data.chassis_power_limit == 60, "other cmd");

    /* stress: random noise (with many 0xA5) between valid frames; every frame must be found */
    sc_referee_init(&r);
    unsigned seed = 12345u;
    int sent = 0;
    for (int k = 0; k < 200; k++) {
        int nn = (int)(seed % 40u);
        for (int i = 0; i < nn; i++) {
            seed = seed * 1103515245u + 12345u;
            uint8_t b = (seed >> 16) & 1u ? 0xA5u : (uint8_t)(seed >> 8);
            (void)sc_referee_feed(&r, b, 300);
        }
        st[10] = (uint8_t)(40 + k % 60);
        n = make_frame(f, 0x0201, st, 13, (uint8_t)k);
        uint32_t before = r.data.frames_ok;
        feed(&r, f, n, 300);
        sent++;
        CHECK(r.data.frames_ok == before + 1u && r.data.chassis_power_limit == (uint16_t)(40 + k % 60),
              "stress frame %d lost", k);
        if (r.data.frames_ok != before + 1u) break;
    }
    printf("  info: %d frames after random noise: %u parsed\n", sent, (unsigned)r.data.frames_ok);
}

/* ---------- sensing */
static uint16_t counts(float v, float vdda)
{
    return (uint16_t)lrintf(v / vdda * 4095.0f);
}

static void test_sensing(void)
{
    sc_cal_t cal;
    sc_cal_default(&cal);
    const uint16_t vcal = 1655;     /* typical VREFINT_CAL */
    const float vdda = 3.30f;
    sc_adc_raw_t raw;
    raw.vrefint = (uint16_t)lrintf(3.0f * vcal / vdda);
    raw.vnode = counts(26.0f / 11.0f, vdda);
    raw.vin = counts(24.0f / 11.0f, vdda);
    raw.iin = counts(2.0f * 0.24f, vdda);
    raw.icap = counts(vdda / 2 + 3.0f * 0.04f, vdda);
    /* NTC at 25 C: 10k / 10k -> VDDA/2 */
    raw.temp = counts(vdda / 2, vdda);
    sc_meas_t m;
    sc_sensing_convert(&raw, vcal, &cal, &m);
    CHECK(NEAR(m.vdda, 3.30f, 0.005f), "vdda %f", m.vdda);
    CHECK(NEAR(m.vnode, 26.0f, 0.03f), "vnode %f", m.vnode);
    CHECK(NEAR(m.vin, 24.0f, 0.03f), "vin %f", m.vin);
    CHECK(NEAR(m.iin, 2.0f, 0.01f), "iin %f", m.iin);
    CHECK(NEAR(m.icap, 3.0f, 0.03f), "icap %f", m.icap);
    CHECK(NEAR(m.temp_c, 25.0f, 0.3f), "temp %f", m.temp_c);
    CHECK(m.valid, "valid");
    raw.temp = 0;   /* open NTC -> invalid */
    sc_sensing_convert(&raw, vcal, &cal, &m);
    CHECK(!m.valid, "ntc open invalid");
}

/* ---------- power target and DAC mapping */
static void test_power_target(void)
{
    sc_referee_data_t ref;
    memset(&ref, 0, sizeof(ref));
    sc_target_t t;
    sc_power_target(&ref, false, 0, 1000, &t);
    CHECK(t.src == SC_SRC_DEFAULT && NEAR(t.p_target, SC_P_DEFAULT_W - SC_P_MARGIN_W, 0.01f), "default %f", t.p_target);
    sc_power_target(&ref, true, 70.0f, 1000, &t);
    CHECK(t.src == SC_SRC_CAN && NEAR(t.p_target, 68.0f, 0.01f), "can %f", t.p_target);
    ref.have_status = ref.have_power = true;
    ref.chassis_power_limit = 60;
    ref.chassis_output_on = true;
    ref.buffer_energy = 60;
    ref.t_status_ms = ref.t_power_ms = 900;
    sc_power_target(&ref, true, 70.0f, 1000, &t);
    CHECK(t.src == SC_SRC_REFEREE && NEAR(t.p_target, 58.0f, 0.01f), "referee %f", t.p_target);
    ref.buffer_energy = 20;
    sc_power_target(&ref, false, 0, 1000, &t);
    CHECK(NEAR(t.p_target, 58.0f - SC_K_BUF_W_PER_J * 20.0f, 0.01f), "buffer low %f", t.p_target);
    ref.chassis_output_on = false;
    sc_power_target(&ref, false, 0, 1000, &t);
    CHECK(t.chassis_off && t.p_target == 0.0f, "chassis off");
    ref.chassis_output_on = true;
    sc_power_target(&ref, false, 0, 1000 + SC_SRC_TIMEOUT_MS + 1, &t);
    CHECK(t.src == SC_SRC_DEFAULT, "referee stale");

    CHECK(sc_dac_volts_for_limit(SC_ILIM_HW_MAX_A + 0.1f) == 0.0f, "dac zero at max");
    float v2 = sc_dac_volts_for_limit(2.0f);    /* offset 26 mV -> 0.26 mA -> Vb 0.62+1.77 */
    CHECK(NEAR(v2, 2.41f, 0.03f), "dac 2A %f", v2);
    float imin = sc_limit_min_hw(3.3f);
    CHECK(imin > 1.0f && imin < 1.4f, "imin %f", imin);
    printf("  info: DAC 2.0 A -> %.3f V, lowest hardware limit at VDDA 3.3 V = %.2f A\n", v2, imin);
}

/* ---------- supervisor sequence */
static void run(sc_super_t *s, const sc_meas_t *m, const sc_inputs_t *in, float p, int ms)
{
    for (int i = 0; i < ms; i++) {
        sc_super_step(s, m, in, p, 1);
    }
}

static int run_until(sc_super_t *s, const sc_meas_t *m, const sc_inputs_t *in, float p, sc_state_t st, int max)
{
    for (int i = 0; i < max; i++) {
        if (s->state == st) return i;
        sc_super_step(s, m, in, p, 1);
    }
    return -1;
}

static void test_supervisor(void)
{
    sc_super_t s;
    sc_super_init(&s);
    sc_meas_t m = {.vdda = 3.3f, .vnode = 20.0f, .vin = 24.0f, .iin = 0.0f, .icap = 0, .temp_c = 30, .pin = 0, .valid = true};
    sc_inputs_t in = {.pmos_en_rb = false, .node_ok = true, .pgood = false};
    int t_start = run_until(&s, &m, &in, 50.0f, SC_ST_START, 1000);
    CHECK(t_start >= (int)SC_BOOT_MS && t_start <= (int)(SC_BOOT_MS + SC_VIN_OK_MS + 2) && s.en_pmos && !s.en_chg,
          "start after %d ms state %d", t_start, s.state);
    run(&s, &m, &in, 50.0f, SC_START_CHECK_MS + 1);
    CHECK(s.state == SC_ST_FAULT && (s.last_fault & SC_F_START) && !s.en_pmos, "readback fault %d", s.state);
    in.pmos_en_rb = true;
    run(&s, &m, &in, 50.0f, SC_RETRY_MS + SC_VIN_OK_MS + SC_START_CHECK_MS + 5);
    CHECK(s.state == SC_ST_CHARGE && s.en_chg, "charging %d", s.state);
    /* input lost -> IDLE (not a fault) */
    m.vin = 15.0f;
    run(&s, &m, &in, 50.0f, 2);
    CHECK(s.state == SC_ST_IDLE && !s.en_pmos, "input lost %d", s.state);
    m.vin = 24.0f;
    run(&s, &m, &in, 50.0f, SC_VIN_OK_MS + SC_START_CHECK_MS + 5);
    CHECK(s.state == SC_ST_CHARGE, "restart %d", s.state);
    /* comparator pulls PMOS_EN low while charging -> input OV fault, retry later */
    in.pmos_en_rb = false;
    run(&s, &m, &in, 50.0f, 2);
    CHECK(s.state == SC_ST_FAULT && (s.last_fault & SC_F_IN_OV), "in ov %d", s.state);
    in.pmos_en_rb = true;
    run(&s, &m, &in, 50.0f, SC_RETRY_MS + SC_VIN_OK_MS + SC_START_CHECK_MS + 5);
    CHECK(s.state == SC_ST_CHARGE, "after in ov %d", s.state);
    /* over-temperature with hysteresis */
    m.temp_c = 90.0f;
    run(&s, &m, &in, 50.0f, 2);
    CHECK(s.state == SC_ST_FAULT && (s.last_fault & SC_F_OVERTEMP), "ot %d", s.state);
    m.temp_c = 75.0f;
    run(&s, &m, &in, 50.0f, SC_RETRY_MS + 10);
    CHECK(s.state == SC_ST_FAULT, "ot hysteresis %d", s.state);
    m.temp_c = 60.0f;
    run(&s, &m, &in, 50.0f, SC_RETRY_MS + SC_VIN_OK_MS + SC_START_CHECK_MS + 10);
    CHECK(s.state == SC_ST_CHARGE, "ot cleared %d", s.state);
    /* over-current is latched */
    m.iin = 6.0f;
    run(&s, &m, &in, 50.0f, SC_IIN_OC_MS + 2);
    CHECK(s.state == SC_ST_FAULT && (s.faults & SC_F_IN_OC), "oc %d", s.state);
    m.iin = 0.0f;
    run(&s, &m, &in, 50.0f, 10 * SC_RETRY_MS);
    CHECK(s.state == SC_ST_FAULT, "oc latched %d", s.state);
    /* node over-voltage */
    sc_super_init(&s);
    m.iin = 0.0f;
    run(&s, &m, &in, 50.0f, SC_BOOT_MS + SC_VIN_OK_MS + SC_START_CHECK_MS + 5);
    CHECK(s.state == SC_ST_CHARGE, "charge again %d", s.state);
    in.node_ok = false;
    run(&s, &m, &in, 50.0f, 1);
    CHECK(s.state == SC_ST_FAULT && (s.last_fault & SC_F_NODE_OV) && !s.en_chg, "node ov %d", s.state);
    /* no permission (power target 0) keeps the charger off */
    sc_super_init(&s);
    in.node_ok = true;
    run(&s, &m, &in, 0.0f, 2000);
    CHECK(s.state == SC_ST_IDLE && !s.en_pmos, "no permission %d", s.state);
}

/* ---------- short / stall detection: node must rise while the charger switches */
static void test_short(void)
{
    sc_super_t s;
    sc_meas_t m = {.vdda = 3.3f, .vnode = 0.2f, .vin = 24.0f, .iin = 0.3f, .icap = 0, .temp_c = 30, .pin = 7, .valid = true};
    sc_inputs_t in = {.pmos_en_rb = true, .node_ok = true, .pgood = true, .chg_on = true};

    /* 1. healthy empty bank: 5 F at 5.5 A (lowest valley limit) = 1.1 V/s -> no trip, charges to 12 V */
    sc_super_init(&s);
    CHECK(run_until(&s, &m, &in, 40.0f, SC_ST_CHARGE, 2000) > 0, "to charge %d", s.state);
    int tripped = 0;
    for (int i = 0; i < 12000; i++) {
        m.vnode += 5.5f / 5.0f / 1000.0f;
        sc_super_step(&s, &m, &in, 40.0f, 1);
        if (s.state != SC_ST_CHARGE) { tripped = 1; break; }
    }
    CHECK(!tripped && m.vnode > 12.0f, "healthy bank tripped (state %d, %.2f V)", s.state, m.vnode);

    /* 2. gated (low power, 30%% on-time): rise only while switching -> still no trip */
    sc_super_init(&s);
    m.vnode = 0.5f;
    run_until(&s, &m, &in, 40.0f, SC_ST_CHARGE, 2000);
    tripped = 0;
    for (int i = 0; i < 20000 && m.vnode < SC_SHORT_V_CHECK; i++) {
        in.chg_on = (i % 100) < 30;
        if (in.chg_on) m.vnode += 5.5f / 5.0f / 1000.0f;
        else m.vnode -= 0.05f / 5.0f / 1000.0f;        /* small standby drain */
        sc_super_step(&s, &m, &in, 40.0f, 1);
        if (s.state != SC_ST_CHARGE) { tripped = 1; break; }
    }
    CHECK(!tripped, "gated charging tripped (state %d, %.2f V)", s.state, m.vnode);
    in.chg_on = true;

    /* 3. hard short at 0.1 V: trips after one window, retries after SC_SHORT_RETRY_MS */
    sc_super_init(&s);
    m.vnode = 0.1f;
    run_until(&s, &m, &in, 40.0f, SC_ST_CHARGE, 2000);
    int t = run_until(&s, &m, &in, 40.0f, SC_ST_FAULT, 3000);
    CHECK(t >= (int)SC_SHORT_WIN_MS - 1 && t <= (int)SC_SHORT_WIN_MS + 1 && (s.last_fault & SC_F_SHORT) && !s.en_chg && !s.en_pmos,
          "short trip after %d ms fault %02x", t, s.last_fault);
    run(&s, &m, &in, 40.0f, SC_RETRY_MS + 100);
    CHECK(s.state == SC_ST_FAULT, "short uses the longer retry delay %d", s.state);
    run(&s, &m, &in, 40.0f, SC_SHORT_RETRY_MS - SC_RETRY_MS);
    CHECK(s.state != SC_ST_FAULT, "short retry %d", s.state);

    /* 4. short stays: 3 consecutive trips -> latched */
    for (int k = 0; k < 3; k++) {
        run_until(&s, &m, &in, 40.0f, SC_ST_FAULT, SC_SHORT_RETRY_MS + SC_VIN_OK_MS + SC_SHORT_WIN_MS + 100);
        run_until(&s, &m, &in, 40.0f, SC_ST_IDLE, SC_SHORT_RETRY_MS + 100);
    }
    CHECK(s.short_trips >= SC_SHORT_MAX_TRIPS && s.state == SC_ST_FAULT && (s.faults & SC_F_SHORT),
          "latched after %u trips, state %d faults %02x", s.short_trips, s.state, s.faults);
    run(&s, &m, &in, 40.0f, 3 * SC_SHORT_RETRY_MS);
    CHECK(s.state == SC_ST_FAULT && !s.en_pmos, "short latched %d", s.state);

    /* 5. a single trip then a good charge resets the trip counter */
    sc_super_init(&s);
    m.vnode = 0.1f;
    run_until(&s, &m, &in, 40.0f, SC_ST_CHARGE, 2000);
    run_until(&s, &m, &in, 40.0f, SC_ST_FAULT, 3000);
    run_until(&s, &m, &in, 40.0f, SC_ST_CHARGE, SC_SHORT_RETRY_MS + SC_VIN_OK_MS + 100);
    for (int i = 0; i < 12000 && s.state == SC_ST_CHARGE; i++) {
        m.vnode += 1.1f / 1000.0f;
        sc_super_step(&s, &m, &in, 40.0f, 1);
    }
    CHECK(s.state == SC_ST_CHARGE && s.short_trips == 0u, "trip counter reset %u state %d", s.short_trips, s.state);

    /* 6. node collapses while running from 24 V: detected once it is below the check voltage */
    sc_super_init(&s);
    m.vnode = 24.0f;
    run_until(&s, &m, &in, 40.0f, SC_ST_CHARGE, 2000);
    run(&s, &m, &in, 40.0f, 3000);
    CHECK(s.state == SC_ST_CHARGE, "normal at 24 V %d", s.state);
    m.vnode = 0.3f;
    t = run_until(&s, &m, &in, 40.0f, SC_ST_FAULT, 3000);
    CHECK(t > 0 && t <= (int)SC_SHORT_WIN_MS + 1 && (s.last_fault & SC_F_SHORT), "collapse trip %d", t);
}

/* ---------- closed loop with a crude converter model */
static float plant_ilim(float dac_v, float err)
{
    /* invert the DAC model with a gain error to emulate component tolerance */
    float v_b = dac_v / (1.0f + SC_R_OFS_B / SC_R_OFS_BPD);
    float i_ofs = (v_b - SC_VBE * (1.0f + err)) / SC_R_OFS_E;
    if (i_ofs < 0) i_ofs = 0;
    float i = (SC_ISNS_TH_V * (1.0f - err) - i_ofs * SC_R_ISNS) / SC_R_SHUNT_IN;
    return i > 0 ? i : 0;
}

static void test_power_loop(void)
{
    sc_power_t p;
    sc_power_init(&p);
    sc_target_t t = {.p_target = 58.0f, .src = SC_SRC_REFEREE, .chassis_off = false};
    float vin = 24.0f, pin = 0, vnode = 20.0f;
    float ilim_real = 0;
    for (int ms = 0; ms < 3000; ms++) {
        sc_power_step(&p, &t, true, vin, pin, 2.0f, vnode, 3.3f, 1);
        ilim_real = plant_ilim(p.dac_v, 0.08f);
        float demand = 4.0f;   /* empty bank wants more than the limit */
        float i = p.gate ? (demand < ilim_real ? demand : ilim_real) : 0.0f;
        pin = vin * i;
    }
    CHECK(NEAR(pin, 58.0f, 1.5f), "closed loop pin %f (trim %f)", pin, p.trim_a);
    printf("  info: closed loop with 8%% model error: Pin %.1f W for target 58 W (trim %.2f A)\n", pin, p.trim_a);

    /* low target below the DAC range -> on-time gating */
    sc_power_init(&p);
    t.p_target = 15.0f;
    float acc = 0;
    int n = 0;
    for (int ms = 0; ms < 3000; ms++) {
        sc_power_step(&p, &t, true, vin, pin, 0.0f, vnode, 3.3f, 1);
        ilim_real = plant_ilim(p.dac_v, 0.0f);
        pin = p.gate ? vin * ilim_real : 0.0f;
        if (ms >= 2000) { acc += pin; n++; }
    }
    CHECK(NEAR(acc / n, 15.0f, 3.0f), "low power average %f", acc / n);
    printf("  info: target 15 W below the DAC range -> average %.1f W by on-time gating\n", acc / n);

    /* end of charge: bank current limited to ~SC_I_EOC_A on average */
    sc_power_init(&p);
    t.p_target = 58.0f;
    vnode = 25.8f;
    acc = 0; n = 0;
    float icap = 0;
    for (int ms = 0; ms < 5000; ms++) {
        sc_power_step(&p, &t, true, vin, pin, icap, vnode, 3.3f, 1);
        icap = p.gate ? 2.0f : 0.0f;
        pin = p.gate ? 55.0f : 0.0f;
        if (ms >= 3000) { acc += icap; n++; }
    }
    CHECK(p.eoc && NEAR(acc / n, SC_I_EOC_A, 0.12f), "eoc average %f", acc / n);
    printf("  info: end of charge: average bank current %.2f A (target %.2f A)\n", acc / n, SC_I_EOC_A);

    /* not running: DAC at the lowest limit, gate off, ramp reset */
    sc_power_step(&p, &t, false, vin, 0, 0, vnode, 3.3f, 1);
    CHECK(!p.gate && p.p_ramp == 0.0f && p.dac_code > 3000, "idle dac %u", p.dac_code);
}

/* ---------- CAN */
static void test_can(void)
{
    sc_can_status_t s = {24.12f, 25.5f, 2.34f, 58.0f};
    uint8_t d[8];
    sc_can_pack_status(&s, d);
    /* the robot reads: input_voltage = buf[1]*256 + buf[0]; capacitor_voltage = buf[3]*256 + buf[2] */
    CHECK(d[1] * 256 + d[0] == 2412, "vin %d", d[1] * 256 + d[0]);
    CHECK(d[3] * 256 + d[2] == 2550, "vcap %d", d[3] * 256 + d[2]);
    CHECK(d[5] * 256 + d[4] == 234 && d[7] * 256 + d[6] == 5800, "iin/p");
    sc_can_ext_t e = {3, 0, -1.5f, 41.2f, 77, 0x41};
    sc_can_pack_ext(&e, d);
    CHECK(d[0] == 3 && (int16_t)(d[2] | (d[3] << 8)) == -150 && (int16_t)(d[4] | (d[5] << 8)) == 412 && d[6] == 77, "ext");
    uint8_t cmd[2] = {0x70, 0x17};   /* 6000 -> 60.00 W */
    float w;
    CHECK(sc_can_parse_cmd(cmd, 2, &w) && NEAR(w, 60.0f, 0.001f), "cmd %f", w);
    CHECK(!sc_can_parse_cmd(cmd, 1, &w), "short cmd");
}

int main(void)
{
    test_crc();
    test_referee();
    test_sensing();
    test_power_target();
    test_supervisor();
    test_short();
    test_power_loop();
    test_can();
    printf("%d checks, %d failures\n", checks, fails);
    return fails ? 1 : 0;
}
