#include "bq76942.h"
#include "rev_a.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;

#define CHECK(x)                                                                                   \
    do {                                                                                           \
        if (!(x)) {                                                                                \
            fprintf(stderr, "FAIL %s:%d %s\n", __FILE__, __LINE__, #x);                            \
            return 1;                                                                              \
        }                                                                                          \
        checks++;                                                                                  \
    } while (0)
static app_t a;

static void fixture(uint32_t now) {
    unsigned i;
    app_init(&a, &rev_a_config, now);
    a.config.tuning_verified = true;
    a.config.commissioning_authorized = true;
    a.calibration.verified = true;
    a.calibration.crc = crc32(&a.calibration, offsetof(calibration_t, crc));
    a.monitor.config_valid = true;
    a.monitor.measurements_valid = true;
    a.monitor.open_wire_observed = true;
    a.monitor.permissions_healthy = true;
    a.monitor.timestamp_ms = now;
    a.sensors.valid = true;
    a.sensors.timestamp_ms = now;
    a.sensors.value[BUS_V] = a.sensors.value[BUS_RAW] = 24;
    a.sensors.value[CAP_V] = a.sensors.value[CAP_RAW] = 19.8f;
    for (i = 0; i < 3; i++)
        a.sensors.value[TEMP_FET_CH + i] = 25;
    for (i = 0; i < CELL_COUNT; i++)
        a.monitor.cell_v[i] = 2.2f;
    a.hw_fault_clear = true;
    a.referee_permit = true;
    a.command_seen = true;
    a.command_ms = now;
    a.self_test_pass = true;
    a.state = DISARMED;
}
static void fresh(uint32_t now) {
    a.sensors.timestamp_ms = now;
    a.monitor.timestamp_ms = now;
    a.command_ms = now;
}
static void frame(uint8_t *d, uint8_t seq, command_t cmd, uint16_t watts10) {
    memset(d, 0, 8);
    d[0] = 1;
    d[1] = seq;
    d[2] = (uint8_t)cmd;
    d[4] = (uint8_t)watts10;
    d[5] = (uint8_t)(watts10 >> 8);
    d[7] = crc8(d, 7);
}
/* Behavioral BQ SPI emulator. Model assumptions do not establish actual IC timing/polarity. */
typedef struct {
    uint8_t reg[128], ram[65536], pending[3];
    uint16_t command, mfg;
    uint32_t now;
    bool corrupt, drop, write_drift;
    unsigned writes;
} mock_bq_t;

static mock_bq_t mock;

static void mock_buffer(mock_bq_t *m, uint16_t command) {
    uint8_t sum = (uint8_t)((uint8_t)command + (uint8_t)(command >> 8));
    unsigned i, len;
    m->reg[0x3e] = (uint8_t)command;
    m->reg[0x3f] = (uint8_t)(command >> 8);
    memset(m->reg + 0x40, 0, 32);
    len = 2;
    if (command >= 0x9200) {
        len = 32;
        for (i = 0; i < len; i++)
            m->reg[0x40 + i] = m->ram[command + i];
    } else if (command == 1) {
        m->reg[0x40] = 0x94;
        m->reg[0x41] = 0x76;
    } else if (command == 0x57) {
        m->reg[0x40] = (uint8_t)m->mfg;
    } else if (command == 0x83) {
        m->reg[0x40] = (uint8_t)m->command;
        m->reg[0x41] = (uint8_t)(m->command >> 8);
    }
    for (i = 0; i < len; i++)
        sum = (uint8_t)(sum + m->reg[0x40 + i]);
    m->reg[0x60] = (uint8_t)(0xffu - sum);
    m->reg[0x61] = (uint8_t)(len + 4u);
}
static bool mock_transfer(void *context, const uint8_t tx[3], uint8_t rx[3]) {
    mock_bq_t *m = context;
    uint8_t address = (uint8_t)(tx[0] & 0x7fu), value = 0;
    bool write = (tx[0] & 0x80u) != 0;
    unsigned i;
    if (m->drop)
        return false;
    memcpy(rx, m->pending, 3);
    if (m->corrupt)
        rx[2] ^= 1;
    assert(crc8(tx, 2) == tx[2]);
    if (write) {
        m->reg[address] = tx[1];
        value = tx[1];
        m->writes++;
        if (address == 0x3f) {
            uint16_t cmd = (uint16_t)((uint16_t)m->reg[0x3e] | ((uint16_t)tx[1] << 8));
            if (cmd == 0x90)
                m->reg[0x12] |= 1;
            else if (cmd == 0x92)
                m->reg[0x12] &= (uint8_t)~1u;
            else if (cmd == 0x9a)
                m->reg[0x12] &= (uint8_t)~4u;
            else if (cmd == 0x22)
                m->mfg ^= 0x10;
            else if (cmd == 0x96)
                m->reg[0x7f] = 5;
            else
                mock_buffer(m, cmd);
        }
        if (address == 0x61) {
            uint16_t addr = (uint16_t)((uint16_t)m->reg[0x3e] | ((uint16_t)m->reg[0x3f] << 8));
            uint8_t sum = (uint8_t)((uint8_t)addr + (uint8_t)(addr >> 8));
            assert(tx[1] >= 4 && tx[1] <= 36);
            for (i = 0; i < (unsigned)(tx[1] - 4u); i++)
                sum = (uint8_t)(sum + m->reg[0x40 + i]);
            assert(m->reg[0x60] == (uint8_t)(255u - sum));
            if (addr >= 0x9200) {
                for (i = 0; i < (unsigned)(tx[1] - 4u); i++)
                    m->ram[addr + i] = m->reg[0x40 + i];
                if (m->write_drift)
                    m->ram[addr] ^= 1;
            } else if (addr == 0x83)
                m->command = (uint16_t)((uint16_t)m->reg[0x40] | ((uint16_t)m->reg[0x41] << 8));
        }
    } else {
        value = m->reg[address];
        if (address == 0x12 && m->now % 1000u < 100u)
            value |= 0x20;
    }
    m->pending[0] = tx[0];
    m->pending[1] = value;
    m->pending[2] = crc8(m->pending, 2);
    return true;
}
static void mock_delay(void *context, uint32_t us) {
    (void)context;
    (void)us;
}
static void mock_init(void) {
    unsigned i;
    memset(&mock, 0, sizeof(mock));
    mock.reg[0x12] = 8;
    for (i = 0; i < 10; i++) {
        mock.reg[0x14 + i * 2] = 0x98;
        mock.reg[0x15 + i * 2] = 8;
    } /* 2200mV */
}
static int run_tests(void) {
    uint8_t d[8];
    sensors_t s = {0};
    unsigned i;
    outputs_t out;
    bq_t b;
    bq_transport_t io = {mock_transfer, mock_delay, &mock};
    float original;
    CHECK(crc8((const uint8_t *)"123456789", 9) == 0xf4);
    CHECK(crc32("123456789", 9) == 0xcbf43926u);
    fixture(0);
    CHECK(calibration_valid(&a.calibration));
    a.calibration.gain[BUS_V] += 1;
    CHECK(!calibration_valid(&a.calibration));
    calibration_defaults(&a.calibration);
    CHECK(!calibration_valid(&a.calibration));
    CHECK(fabsf(stored_energy_j(22.05f) - 1350.5625f) < 0.02f);
    CHECK(fabsf(usable_energy_j(22.05f) - 950.5625f) < 0.02f);
    CHECK(soe_percent(12) == 0);
    CHECK(fabsf(soe_percent(22.05f) - 100) < 0.01f);
    CHECK(stored_energy_j(NAN) == 0);
    CHECK(soe_percent(30) == 100);
    /* 25C with10k NTC ||100k,10k top: ratio10/21. */
    CHECK(fabsf(sensors_ntc_c(1950, &a.calibration) - 25.0f) < 0.05f);
    CHECK(isnan(sensors_ntc_c(0, &a.calibration)));
    CHECK(isnan(sensors_ntc_c(4095, &a.calibration)));
    for (i = 0; i < ADC_COUNT; i++)
        s.raw[i] = 1950;
    s.raw[BUS_V] = 2100;
    s.raw[CAP_V] = 1900;
    s.raw[BUS_I] = 2045;
    s.raw[CAP_I] = 2045;
    s.raw[IL_I] = 2045;
    sensors_convert(&s, &a.calibration);
    CHECK(s.valid);
    CHECK(fabsf(s.value[IL_I]) < 0.05f);
    original = s.value[BUS_V];
    s.raw[BUS_V] = 1050;
    sensors_convert(&s, &a.calibration);
    CHECK(fabsf(s.value[BUS_V] * 2 - original) < 0.001f);
    s.raw[TEMP_L_CH] = 4095;
    sensors_convert(&s, &a.calibration);
    CHECK(!s.valid);
    fixture(0);
    CHECK(!app_transition(&a, ASSIST, 0));
    CHECK(!app_transition(&a, READY, 0));
    app_fault(&a, HW_OC, 10);
    CHECK(a.state == FAULT_LATCHED);
    CHECK(a.first_fault == HW_OC);
    CHECK(a.log_frozen);
    app_fault(&a, BQ_CRC, 11);
    CHECK(a.faults == (HW_OC | BQ_CRC));
    CHECK(a.first_fault == HW_OC);
    CHECK(!app_transition(&a, READY, 20));
    a.hw_fault_clear = false;
    CHECK(!app_command(&a, CMD_REARM, 0, 20));
    a.hw_fault_clear = true;
    fresh(20);
    CHECK(app_command(&a, CMD_REARM, 0, 20));
    CHECK(a.state == SELF_TEST);
    app_step(&a, 21);
    CHECK(a.state == DISARMED);
    CHECK(!a.power_session);
    CHECK(!a.outputs.gate);
    fixture(0);
    a.config.commissioning_authorized = false;
    CHECK(!app_command(&a, CMD_ARM, 0, 0));
    fixture(0);
    frame(d, 1, CMD_STATUS, 0);
    CHECK(app_can_receive(&a, 0x501, d, 8, 1));
    CHECK(!app_can_receive(&a, 0x501, d, 8, 2));
    frame(d, 2, CMD_ASSIST, 1201);
    CHECK(!app_can_receive(&a, 0x501, d, 8, 3));
    frame(d, 2, CMD_STATUS, 0);
    d[7] ^= 1;
    CHECK(!app_can_receive(&a, 0x501, d, 8, 3));
    CHECK(a.command_ms == 1);
    frame(d, 2, CMD_STATUS, 0);
    CHECK(!app_can_receive(&a, 0x501, d, 7, 3));
    CHECK(!app_can_receive(&a, 0x502, d, 8, 3));
    a.sequence = 255;
    frame(d, 0, CMD_STATUS, 0);
    CHECK(app_can_receive(&a, 0x501, d, 8, 4));
    fixture(300);
    frame(d, 1, CMD_STATUS, 0);
    CHECK(!app_can_receive_at(&a, 0x501, d, 8, 0, 300));
    CHECK(app_can_receive_at(&a, 0x501, d, 8, 250, 300) && a.command_ms == 250);
    fixture(0);
    a.state = ASSIST;
    a.power_session = true;
    a.command_ms = 0;
    fresh(251);
    a.command_ms = 0;
    app_step(&a, 251);
    CHECK(a.faults & CAN_TIMEOUT);
    CHECK(a.state == FAULT_LATCHED);
    CHECK(!a.outputs.gate);
    fixture(0);
    a.sensors.value[TEMP_BANK_CH] = 50;
    CHECK(app_live_faults(&a, 0) & TEMP_BANK);
    a.sensors.value[TEMP_BANK_CH] = NAN;
    CHECK(app_live_faults(&a, 0) & TEMP_SENSOR_INVALID);
    fixture(0);
    a.monitor.cell_v[8] = 2.6f;
    CHECK(app_live_faults(&a, 0) & CELL_OV);
    CHECK(balance_physical_mask(8) == 0x200);
    CHECK(balance_physical_mask(7) == 0x80);
    CHECK(balance_physical_mask(-1) == 0);
    fixture(0);
    for (i = 0; i < 9; i++)
        a.monitor.cell_v[i] = 2.31f;
    a.monitor.cell_v[8] = 2.34f;
    CHECK(balance_select(&a.monitor, 25, true, -1) == 8);
    CHECK(balance_select(&a.monitor, 25, false, -1) == -1);
    CHECK(balance_select(&a.monitor, 45, true, -1) == -1);
    a.monitor.cell_v[8] = 2.315f;
    CHECK(balance_select(&a.monitor, 25, true, 8) == -1);
    fixture(0);
    a.state = CHARGE;
    a.outputs.gate = true;
    a.outputs.arm = true;
    a.outputs.iso_bus = true;
    a.power_session = true;
    out = app_safe_outputs(&a);
    CHECK(FW_MODE == SAFE_MONITOR_ONLY ? !out.gate : out.gate);
    a.referee_permit = false;
    out = app_safe_outputs(&a);
    CHECK(!out.gate && !out.arm && !out.iso_bus);
    fixture(0);
    if (FW_MODE != SAFE_MONITOR_ONLY) {
        CHECK(app_command(&a, CMD_ARM, 0, 0));
        CHECK(a.state == PRECHARGE);
        a.sensors.value[BUS_V] = 0;
        a.sensors.value[CAP_V] = 0;
        a.previous_bus_v = 0;
        a.previous_cap_v = 0;
        fresh(3001);
        app_step(&a, 3001);
        CHECK(a.state == FAULT_LATCHED);
        CHECK(a.faults & PRECHARGE_TIMEOUT);
        fixture(0);
        CHECK(app_command(&a, CMD_ARM, 0, 0));
        fresh(100);
        app_step(&a, 100);
        fresh(200);
        app_step(&a, 200);
        fresh(300);
        app_step(&a, 300);
        CHECK(a.state == READY);
        CHECK(app_command(&a, CMD_CHARGE, 40, 300));
        CHECK(!app_command(&a, CMD_ASSIST, 80, 300));
        for (i = 0; i < 300; i++) {
            fresh(301 + i);
            app_step(&a, 301 + i);
            control_fast(&a, 0, 24, 19.8f);
        }
        CHECK(a.current_reference <= 9.5f);
        CHECK(a.duty_a >= 0.05f && a.duty_a <= 0.95f);
        CHECK(a.duty_b >= 0.05f && a.duty_b <= 0.95f);
        fresh(700);
        CHECK(app_command(&a, CMD_STANDBY, 0, 700));
        CHECK(app_command(&a, CMD_ASSIST, 120, 700));
        a.sensors.value[CAP_V] = 12.1f;
        a.duty_b = 0.9f;
        control_slow(&a, 700);
        CHECK(fabsf(a.current_reference) <= 9.5f);
    } else {
        CHECK(!app_command(&a, CMD_ARM, 0, 0));
    }
    /* Phase changes must not restart the overall 3-second precharge budget. */
    if (FW_MODE != SAFE_MONITOR_ONLY) {
        fixture(0);
        CHECK(app_command(&a, CMD_ARM, 0, 0));
        fresh(2900);
        app_step(&a, 2900);
        CHECK(a.precharge_phase == 1);
        fresh(3001);
        app_step(&a, 3001);
        CHECK(a.state == FAULT_LATCHED && (a.faults & PRECHARGE_TIMEOUT));
        fixture(0);
        a.state = ASSIST;
        a.power_session = true;
        a.peak_active = true;
        a.peak_seen = true;
        CHECK(app_transition(&a, STANDBY, 900));
        CHECK(!a.peak_active && a.last_peak_ms == 900);
        a.state = SHUTDOWN;
        a.entered_ms = 1000;
        a.sensors.value[TEMP_FET_CH] = 55;
        fresh(1100);
        app_step(&a, 1100);
        CHECK(a.state == COOLDOWN);
        CHECK(!app_command(&a, CMD_REARM, 0, 1100));
        a.sensors.value[TEMP_FET_CH] = 25;
        CHECK(app_command(&a, CMD_REARM, 0, 1100));
        app_step(&a, 1100);
        CHECK(a.state == DISARMED && !a.power_session);
    }
    fixture(0);
    a.monitor.settling = true;
    a.monitor.measurements_valid = false;
    CHECK(app_live_faults(&a, 0) == 0);
    a.power_session = true;
    CHECK(app_live_faults(&a, 0) & SENSOR_INVALID);
    fixture(0);
    CHECK(app_live_faults(&a, 51) & ADC_STALE);
    fixture(0);
    a.outputs.monitor_valid = true;
    a.monitor.config_valid = false;
    CHECK(!app_safe_outputs(&a).monitor_valid);
    fixture(0);
    a.state = SERVICE;
    a.config.service_dump_authorized = true;
    CHECK(FW_MODE == SAFE_MONITOR_ONLY ? !app_safe_outputs(&a).dump : app_safe_outputs(&a).dump);
    a.monitor.measurements_valid = false;
    CHECK(!app_safe_outputs(&a).dump);
    CHECK(app_command(&a, CMD_DISARM, 0, 10));
    CHECK(a.state == DISARMED && !app_safe_outputs(&a).dump);
    if (FW_MODE != SAFE_MONITOR_ONLY) {
        fixture(0);
        a.state = SERVICE;
        a.config.service_dump_authorized = true;
        fresh(251);
        a.command_ms = 0;
        CHECK(app_live_faults(&a, 251) & CAN_TIMEOUT);
        fresh(a.config.discharge_timeout_ms + 1u);
        CHECK(app_live_faults(&a, a.config.discharge_timeout_ms + 1u) & DISCHARGE_TIMEOUT);
    }
    fixture(0);
    /* Sequence fuzzing: malformed frames never change state or power outputs. */
    for (i = 0; i < 256; i++) {
        frame(d, (uint8_t)i, CMD_STATUS, 0);
        d[7] ^= 0x80;
        CHECK(!app_can_receive(&a, 0x501, d, 8, i));
    }
    CHECK(a.state == DISARMED && !app_safe_outputs(&a).gate);
    mock_init();
    bq_init(&b, &io, 0);
    for (i = 0; i < 1500 && b.phase != BQ_READY && b.phase != BQ_FAILED; i++) {
        mock.now = i * 10u;
        bq_tick(&b, mock.now, 25, true, true);
    }
    CHECK(b.phase == BQ_READY);
    CHECK(b.entry == 39);
    CHECK(b.monitor.config_valid);
    CHECK(b.monitor.open_wire_observed);
    CHECK(fabsf(b.monitor.cell_v[8] - 2.2f) < 0.001f);
    CHECK(mock.ram[0x9304] == 0xff && mock.ram[0x9305] == 2);
    mock.corrupt = true;
    bq_tick(&b, mock.now + 10u, 25, true, true);
    CHECK(b.phase == BQ_FAILED);
    CHECK(b.monitor.faults & BQ_CRC);
    CHECK(!b.monitor.config_valid);
    mock_init();
    mock.write_drift = true;
    bq_init(&b, &io, 0);
    bq_tick(&b, 0, 25, true, true);
    bq_tick(&b, 10, 25, true, true);
    bq_tick(&b, 20, 25, true, true);
    CHECK(b.phase == BQ_FAILED);
    CHECK(!b.monitor.config_valid);
    mock_init();
    mock.drop = true;
    bq_init(&b, &io, 0);
    bq_tick(&b, 0, 25, true, true);
    CHECK(b.phase == BQ_FAILED);
    fixture(0);
    telemetry_pack(&a, 7, 4, d);
    CHECK(crc8(d, 7) == d[7]);
    CHECK(d[0] == 1 && d[1] == 4);
    {
        char out_text[200];
        cli_reply(&a, "gate on", out_text, sizeof(out_text));
        CHECK(strstr(out_text, "read-only") != NULL);
    }
    printf("PASS %u assertions, FW_MODE=%u; no hardware operations\n", checks, (unsigned)FW_MODE);
    return 0;
}
int main(void) { return run_tests(); }
