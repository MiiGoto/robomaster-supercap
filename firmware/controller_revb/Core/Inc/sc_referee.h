/*
 * Referee system serial parser (RoboMaster 2026 University Series Communication Protocol V1.0.0, 2025-12-03).
 * Frame: SOF 0xA5 | data_length u16 | seq u8 | CRC8 | cmd_id u16 | data | CRC16 (all little endian).
 * Used: 0x0201 robot status (chassis power limit @10, PM output bits @12),
 *       0x0202 power/heat (buffer energy @8).
 */
#ifndef SC_REFEREE_H
#define SC_REFEREE_H

#include <stdbool.h>
#include <stdint.h>

#define SC_REF_MAX_DATA 128u

typedef struct {
    uint16_t chassis_power_limit;   /* W */
    uint16_t buffer_energy;         /* J */
    bool     chassis_output_on;     /* PM chassis port has 24 V */
    uint32_t t_status_ms;           /* last 0x0201 */
    uint32_t t_power_ms;            /* last 0x0202 */
    bool     have_status;
    bool     have_power;
    uint32_t frames_ok;
    uint32_t crc_errors;
} sc_referee_data_t;

typedef struct {
    uint8_t  buf[5 + 2 + SC_REF_MAX_DATA + 2];
    uint16_t idx;
    uint16_t need;          /* total frame length once the header is valid */
    sc_referee_data_t data;
} sc_referee_t;

void    sc_referee_init(sc_referee_t *r);
/* feed one received byte; returns the cmd_id of a completed valid frame, 0 otherwise */
uint16_t sc_referee_feed(sc_referee_t *r, uint8_t byte, uint32_t now_ms);

uint8_t  sc_crc8(const uint8_t *p, uint32_t n);
uint16_t sc_crc16(const uint8_t *p, uint32_t n);

#endif
