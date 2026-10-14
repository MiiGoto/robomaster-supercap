/*
 * Rev B supercap control board - configuration constants.
 *
 * Hardware values come from hardware/revb/control_board (schematic 2026-10-11).
 * Every threshold here is a PROTOTYPE ASSUMPTION: confirm on the bench before
 * connecting a robot.
 */
#ifndef SC_CONFIG_H
#define SC_CONFIG_H

/* ---------------- timing */
#define SC_TICK_HZ              1000u     /* control tick (TIM6) */
#define SC_CAN_STATUS_HZ        100u      /* 0x211 (Taobao compatible) */
#define SC_CAN_EXT_HZ           20u       /* 0x212 (Rev B extension) */

/* ---------------- analog front end */
#define SC_VREFINT_CAL_MV       3000.0f   /* VREFINT_CAL measured at VDDA = 3.0 V */
#define SC_DIV_VNODE            11.0f     /* 100k / 10k */
#define SC_DIV_VIN              11.0f     /* 100k / 10k (VIN_C, after the series PMOS) */
#define SC_IIN_V_PER_A          0.24f     /* INA240A1 (G=20) x R4 12 mOhm */
#define SC_ICAP_V_PER_A         0.040f    /* INA240A1 (G=20) x R114 2 mOhm, + = charging the bank */
#define SC_NTC_R25              10000.0f
#define SC_NTC_B                3380.0f
#define SC_NTC_RFIX             10000.0f  /* NTC to 3V3, RFIX to GND */

/* ---------------- LM5176 input current limit via ISNS offset (sheet 1) */
#define SC_ISNS_TH_V            0.050f    /* LM5176 ISNS limit threshold (typ) */
#define SC_R_SHUNT_IN           0.012f    /* R4 */
#define SC_R_ISNS               100.0f    /* R5 */
#define SC_R_OFS_E              6800.0f   /* R7 emitter resistor */
#define SC_R_OFS_B              1000.0f   /* R6 base resistor */
#define SC_R_OFS_BPD            100000.0f /* R8 base pull-down */
#define SC_VBE                  0.62f     /* MMBT5551 Vbe at ~0.1-0.4 mA (calibrate) */
#define SC_DAC_VMAX_FRAC        0.94f     /* buffered DAC output headroom: usable up to ~VDDA-0.2 V */
#define SC_ILIM_HW_MAX_A        (SC_ISNS_TH_V / SC_R_SHUNT_IN)   /* 4.17 A, DAC = 0 */

/* ---------------- power target */
#define SC_P_DEFAULT_W          40.0f     /* no referee data and no CAN command */
#define SC_P_MARGIN_W           2.0f      /* stay below the referee limit */
#define SC_BUF_REF_J            40.0f     /* below this buffer energy, reduce power */
#define SC_K_BUF_W_PER_J        1.5f
#define SC_P_MAX_W              110.0f    /* hardware/thermal ceiling */
#define SC_P_MIN_RUN_W          5.0f      /* below this the charger stays off */
#define SC_P_RAMP_W_PER_S       150.0f    /* soft start / step limit */
#define SC_SRC_TIMEOUT_MS       500u      /* referee UART or CAN command freshness */
#define SC_TRIM_KI              2.0f      /* power trim integral gain [A per (A*s)] */
#define SC_TRIM_MAX_A           1.0f
#define SC_TRIM_LEAK_A_PER_S    0.5f

/* ---------------- end of charge (bank balancing clamps can bypass ~0.6 A only) */
#define SC_V_EOC                25.5f     /* above this, bank charge current is limited */
#define SC_I_EOC_A              0.5f
#define SC_EOC_PERIOD_MS        100u
#define SC_EOC_TON_MIN_MS       5u

/* ---------------- protection / permission thresholds */
#define SC_VIN_START_MIN        20.0f
#define SC_VIN_RUN_MIN          19.0f
#define SC_VIN_MAX              28.3f     /* hardware comparator trips at ~28.8 V */
#define SC_VNODE_SW_OV          26.8f     /* LM5176 CV = 26.33 V, hardware comparator ~27.8 V */
#define SC_VNODE_SW_OV_CLEAR    26.4f
#define SC_IIN_OC_A             5.0f
#define SC_IIN_OC_MS            50u
#define SC_T_MAX_C              85.0f
#define SC_T_RESUME_C           70.0f
#define SC_T_SENSOR_MIN_C       (-30.0f)
#define SC_T_SENSOR_MAX_C       150.0f
#define SC_VDDA_MIN             3.0f
#define SC_VDDA_MAX             3.6f
#define SC_START_CHECK_MS       5u        /* PMOS on -> readback check -> EN_CHG */
#define SC_VIN_OK_MS            200u      /* input must be stable this long before start */
#define SC_RETRY_MS             2000u     /* auto retry delay after a non-latched fault */
#define SC_BOOT_MS              100u      /* ADC settling */

/* ---------------- CAN */
#define SC_CAN_ID_CMD           0x210u    /* robot -> board: power limit (Taobao board compatible) */
#define SC_CAN_ID_STATUS        0x211u    /* board -> robot: Vin, Vcap, Iin, Ptarget (Taobao compatible) */
#define SC_CAN_ID_EXT           0x212u    /* board -> robot: state, faults, Icap, temp (Rev B) */

/* ---------------- debug
 * 0 (default): the watchdog keeps running when the debugger halts the core, so a halt resets the MCU
 *              within ~200 ms and EN_CHG / EN_PMOS return to OFF (safe with the power stage live).
 * 1: freeze the watchdog in debug halt - only for bench work with the power stage NOT energized. */
#define SC_DEBUG_FREEZE_IWDG    0

/* ---------------- usable energy window for the % figure in 0x212 */
#define SC_V_EMPTY              14.0f     /* chassis stops below ~14 V (robot memo) */
#define SC_V_FULL               26.2f

#endif
