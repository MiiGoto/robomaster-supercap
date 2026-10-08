#ifndef BQ76942_H
#define BQ76942_H
#include "rev_a.h"
typedef struct {
    uint16_t address;
    uint8_t width;
    uint8_t bytes[2];
} bq_profile_entry_t;
typedef struct {
    bool (*transfer)(void *context, const uint8_t tx[3], uint8_t rx[3]);
    void (*delay_us)(void *context, uint32_t us);
    void *context;
} bq_transport_t;
typedef enum {
    BQ_IDENTITY,
    BQ_ENTER,
    BQ_WRITE_PROFILE,
    BQ_EXIT,
    BQ_WAIT_SCAN,
    BQ_RELEASE,
    BQ_READY,
    BQ_FAILED
} bq_phase_t;
typedef struct {
    bq_transport_t io;
    bq_phase_t phase;
    unsigned entry;
    monitor_t monitor;
    uint32_t entered_ms, last_scan_ms, communication_fault;
    bool cow_seen, cow_completed, initial_por;
    uint16_t balance_mask;
    int balance_logical;
    uint32_t balance_started_ms, balance_stop_ms;
} bq_t;
void bq_init(bq_t *b, const bq_transport_t *io, uint32_t now);
void bq_tick(bq_t *b, uint32_t now, float bank_temp, bool converter_off, bool sensors_valid);
bool bq_byte(bq_t *b, uint8_t address, bool write, uint8_t *value);
bool bq_subcommand(bq_t *b, uint16_t command, uint8_t *buffer, size_t *length);
bool bq_profile_readback(bq_t *b, const bq_profile_entry_t *entry, bool write);
extern const bq_profile_entry_t bq_profile[];
extern const size_t bq_profile_count;
#endif
