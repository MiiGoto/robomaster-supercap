/*
 * CAN frames (classic CAN, 11-bit IDs, 1 Mbit/s, little endian).
 *
 * 0x211 board -> robot, 100 Hz  (same layout as the Taobao board the robots use now)
 *   [0..1] u16 input voltage  x100 [V]
 *   [2..3] u16 capacitor (node) voltage x100 [V]
 *   [4..5] u16 input current  x100 [A]
 *   [6..7] u16 target input power x100 [W]
 * 0x212 board -> robot, 20 Hz (Rev B extension; robots that ignore it are unaffected)
 *   [0] state  [1] fault bits  [2..3] i16 bank current x100 [A] (+ = charging)
 *   [4..5] i16 temperature x10 [C]  [6] usable energy [%]  [7] flag bits
 * 0x210 robot -> board (optional, Taobao compatible)
 *   [0..1] u16 chassis power limit x100 [W]; used when the referee UART is not connected
 */
#ifndef SC_CANPROTO_H
#define SC_CANPROTO_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    float vin, vcap, iin, p_target;
} sc_can_status_t;

typedef struct {
    uint8_t state;
    uint8_t faults;
    float   icap;
    float   temp_c;
    uint8_t energy_pct;
    uint8_t flags;
} sc_can_ext_t;

/* flag bits in 0x212 byte 7 */
#define SC_FLAG_REFEREE_OK  0x01u
#define SC_FLAG_CANCMD_OK   0x02u
#define SC_FLAG_EOC         0x04u
#define SC_FLAG_PGOOD       0x08u
#define SC_FLAG_PMOS_EN     0x10u
#define SC_FLAG_NODE_OK     0x20u
#define SC_FLAG_CHG_ON      0x40u

void sc_can_pack_status(const sc_can_status_t *s, uint8_t out[8]);
void sc_can_pack_ext(const sc_can_ext_t *s, uint8_t out[8]);
/* returns true and writes the limit [W] for a valid 0x210 payload */
bool sc_can_parse_cmd(const uint8_t *d, uint8_t len, float *p_limit_w);

#endif
