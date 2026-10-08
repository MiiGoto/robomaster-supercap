#include "board.h"
app_t app;

static bq_t monitor;

int main(void) {
    uint32_t previous = 0;
    bq_transport_t transport = {board_spi_transfer, board_delay_us, 0};
    app_init(&app, &rev_a_config, 0);
    /* Factory defaults before DMA/interrupts. */
    board_init();
    app.reset_cause = board_reset_cause();
    bq_init(&monitor, &transport, HAL_GetTick());
    if (app.reset_cause & 24u)
        app_fault(&app, WATCHDOG, HAL_GetTick());
    for (;;) {
        uint32_t now = HAL_GetTick(), faults, key;
        app.hw_fault_clear = HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_12) == GPIO_PIN_SET;
        app.referee_permit = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_5) == GPIO_PIN_SET;
        app.monitor_alert_asserted = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_11) == GPIO_PIN_RESET;
        /* ALERT is a request to read cause registers, not proof of a specific fault.
         * Physical DCHG/DDSG/PA12 remain the independent fast shutdown path. */
        if (app.monitor_alert_asserted && monitor.phase == BQ_READY)
            monitor.last_scan_ms = now - 100u;
        board_snapshot(&app.sensors);
        sensors_convert(&app.sensors, &app.calibration);
        key = __get_PRIMASK();
        __disable_irq();
        faults = pending_faults;
        pending_faults = 0;
        __set_PRIMASK(key);
        if (faults)
            app_fault(&app, faults, now);
        /* Faulted monitor is retained for diagnosis. Provisioning never repeats
         * silently and cannot rearm;
               a fresh safe reset/review is needed for BQ failure. */
        bool balancing_allowed = !app.power_session && !app.outputs.gate &&
                                 !app_safe_outputs(&app).dump &&
                                 (app.state == DISARMED || app.state == SERVICE);
        bq_tick(&monitor, now, app.sensors.value[TEMP_BANK_CH], balancing_allowed,
                app.sensors.valid);
        app.monitor = monitor.monitor;
        now = HAL_GetTick();
        board_snapshot(&app.sensors);
        sensors_convert(&app.sensors, &app.calibration);
        key = __get_PRIMASK();
        __disable_irq();
        faults = pending_faults;
        pending_faults = 0;
        __set_PRIMASK(key);
        if (faults)
            app_fault(&app, faults, now);
        board_foreground_io(now);
        if (now - previous >= 1u) {
            app_step(&app, now);
            previous = now;
        }
        board_apply_outputs(&app);
        /* A completed bounded foreground iteration is the heartbeat condition.
         * Fault-latched diagnostic operation is healthy software, not gate permission. */
        board_heartbeat(HAL_GetTick());
    }
}
