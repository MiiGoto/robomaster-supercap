#ifndef REV_A_H
#define REV_A_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define FW_VERSION "0.1.0-rev-a"
enum { SAFE_MONITOR_ONLY, LOW_ENERGY_COMMISSIONING, POWER_STAGE_CONTROL };
#ifndef FW_MODE
#define FW_MODE SAFE_MONITOR_ONLY
#endif
_Static_assert(FW_MODE == SAFE_MONITOR_ONLY || FW_MODE == LOW_ENERGY_COMMISSIONING ||
                   FW_MODE == POWER_STAGE_CONTROL,
               "Unknown firmware mode must not build");
#define CELL_COUNT 9u
#define ADC_COUNT 10u
typedef enum {
    BOOT_SAFE,
    MONITOR_INIT,
    SELF_TEST,
    DISARMED,
    PRECHARGE,
    READY,
    CHARGE,
    STANDBY,
    ASSIST,
    SHUTDOWN,
    COOLDOWN,
    FAULT_LATCHED,
    SERVICE
} fw_state_t;
typedef enum {
    CMD_STATUS,
    CMD_ARM,
    CMD_DISARM,
    CMD_CHARGE,
    CMD_ASSIST,
    CMD_SHUTDOWN,
    CMD_REARM,
    CMD_STANDBY,
    CMD_SERVICE
} command_t;
enum {
    HW_OC = 1u << 0,
    HW_FAULT = 1u << 1,
    BQ_CONFIG = 1u << 2,
    BQ_CRC = 1u << 3,
    CELL_OV = 1u << 4,
    CELL_UV = 1u << 5,
    CELL_IMBALANCE = 1u << 6,
    TEMP_FET = 1u << 7,
    TEMP_INDUCTOR = 1u << 8,
    TEMP_BANK = 1u << 9,
    TEMP_SENSOR_INVALID = 1u << 10,
    BUS_OV = 1u << 11,
    BUS_UV = 1u << 12,
    CAP_OV = 1u << 13,
    CAP_UV = 1u << 14,
    CAN_TIMEOUT = 1u << 15,
    WATCHDOG = 1u << 16,
    PRECHARGE_TIMEOUT = 1u << 17,
    SENSOR_INVALID = 1u << 18,
    CONTACT_SEQUENCE = 1u << 19,
    MONITOR_ALERT = 1u << 20,
    ADC_STALE = 1u << 21,
    CONTROL_TRACKING = 1u << 22,
    DISCHARGE_TIMEOUT = 1u << 23
};
typedef enum {
    BUS_V,
    CAP_V,
    BUS_I,
    CAP_I,
    IL_I,
    TEMP_FET_CH,
    TEMP_L_CH,
    TEMP_BANK_CH,
    BUS_RAW,
    CAP_RAW
} sensor_channel_t;
typedef struct {
    uint16_t raw[ADC_COUNT];
    float value[ADC_COUNT];
    bool valid;
    uint32_t timestamp_ms;
} sensors_t;
typedef struct {
    uint32_t version;
    bool verified;
    float adc_reference_v;
    float gain[ADC_COUNT], offset[ADC_COUNT];
    float ntc_beta, ntc_r25;
    float kp, ki;
    uint32_t crc;
} calibration_t;
typedef struct {
    uint32_t pwm_hz, adc_phase_ticks, deadtime_ticks;
    float bus_min, bus_max, cap_min, cap_max, cap_limit_a, il_limit_a, fast_trip_a;
    float charge_w, assist_w, peak_w, efficiency;
    float temp_warn[3], temp_stop[3], temp_rearm[3];
    uint32_t can_timeout_ms, sensor_timeout_ms, precharge_ms;
    uint32_t peak_ms, repetition_ms, settle_ms, balance_settle_ms;
    uint32_t discharge_timeout_ms;
    bool tuning_verified, commissioning_authorized, service_dump_authorized;
} fw_config_t;
extern const fw_config_t rev_a_config;
typedef struct {
    bool gate, arm, pre_bus, bypass_bus, iso_bus, pre_cap, bypass_cap, iso_cap, dump;
    bool monitor_valid;
} outputs_t;
typedef struct {
    bool config_valid, measurements_valid, open_wire_observed, permissions_healthy, settling;
    float cell_v[CELL_COUNT];
    uint16_t battery_status, safety_a, safety_b, safety_c;
    uint8_t fet_status;
    uint32_t timestamp_ms, faults;
} monitor_t;
typedef struct {
    uint32_t timestamp_ms, faults;
    fw_state_t state;
    sensors_t sensors;
} log_entry_t;
#define LOG_DEPTH 64u
typedef struct {
    fw_state_t state;
    uint32_t entered_ms, faults, first_fault, first_fault_ms, phase_ms, control_ms;
    fw_state_t first_fault_state;
    sensors_t first_fault_snapshot;
    fw_config_t config;
    calibration_t calibration;
    sensors_t sensors;
    monitor_t monitor;
    outputs_t outputs;
    bool hw_fault_clear, referee_permit, self_test_pass;
    bool rearm_pending, power_session, service_confirmed;
    uint8_t sequence;
    bool command_seen;
    uint32_t command_ms;
    float request_w, current_reference, integrator, duty_a, duty_b;
    uint32_t peak_started_ms, last_peak_ms;
    bool peak_active, peak_seen;
    uint8_t precharge_phase;
    float previous_bus_v, previous_cap_v;
    log_entry_t log[LOG_DEPTH];
    uint16_t log_head, log_count;
    bool log_frozen;
    uint32_t reset_cause, command_rejects, control_isr_max_cycles;
    uint8_t reserved_feedback;
    bool monitor_alert_asserted;
} app_t;
float clampf(float value, float low, float high);
uint8_t crc8(const uint8_t *data, size_t size);
uint32_t crc32(const void *data, size_t size);
void calibration_defaults(calibration_t *c);
bool calibration_valid(const calibration_t *c);
void sensors_convert(sensors_t *s, const calibration_t *c);
float sensors_ntc_c(uint16_t code, const calibration_t *c);
float stored_energy_j(float voltage);
float usable_energy_j(float voltage);
float soe_percent(float voltage);
int balance_select(const monitor_t *m, float bank_temp, bool converter_off, int previous);
uint16_t balance_physical_mask(int logical_index);
void app_init(app_t *a, const fw_config_t *config, uint32_t now);
void app_step(app_t *a, uint32_t now);
bool app_command(app_t *a, command_t command, float watts, uint32_t now);
bool app_can_receive(app_t *a, uint16_t id, const uint8_t *data, size_t size, uint32_t now);
void app_fault(app_t *a, uint32_t cause, uint32_t now);
uint32_t app_live_faults(const app_t *a, uint32_t now);
bool app_transition(app_t *a, fw_state_t next, uint32_t now);
outputs_t app_safe_outputs(const app_t *a);
void control_slow(app_t *a, uint32_t now);
void control_fast(app_t *a, float il, float bus, float cap);
void telemetry_pack(const app_t *a, uint8_t page, uint8_t seq, uint8_t data[8]);
void cli_reply(const app_t *a, const char *line, char *output, size_t size);
const char *state_name(fw_state_t state);
#endif
