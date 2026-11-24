/* Finite kernels for the installed instances. Python checks byte and accumulator bounds. */
#include <stdint.h>
#if defined(_WIN32)
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif

API void pair_rec(uint32_t count, uint8_t degree, const int8_t *coef,
                  int8_t *ring, uint8_t *cursor, int8_t *out) {
    uint8_t head = *cursor;
    for (uint32_t t = 0; t < count; ++t) {
        int32_t next = 0;
        uint8_t pos = head;
        out[t] = ring[head];
        for (uint8_t j = 0; j < degree; ++j) {
            next += coef[j] * ring[pos];
            if (++pos == degree) pos = 0;
        }
        ring[head] = (int8_t)next;
        if (++head == degree) head = 0;
    }
    *cursor = head;
}

API void pair_table(uint32_t count, uint16_t period, const int8_t *table,
                    uint16_t *cursor, int8_t *out) {
    uint16_t pos = *cursor;
    for (uint32_t t = 0; t < count; ++t) {
        out[t] = table[pos];
        if (++pos == period) pos = 0;
    }
    *cursor = pos;
}

API void pair_divisors(uint32_t count, uint16_t period, uint8_t terms,
                       int8_t base, const uint16_t *divisors, const int8_t *weights,
                       uint16_t *cursor, int8_t *out) {
    uint16_t pos = *cursor;
    for (uint32_t t = 0; t < count; ++t) {
        int32_t value = base;
        for (uint8_t j = 0; j < terms; ++j)
            if (pos % divisors[j] == 0) value += weights[j];
        out[t] = (int8_t)value;
        if (++pos == period) pos = 0;
    }
    *cursor = pos;
}

/* Layout is [time][stream]. State is preserved between chunks. Each observed
   report is followed by a raw action. The caller supplies identity for no move. */
API void report_stream(uint32_t count, uint32_t streams, uint8_t q,
                       const uint8_t *edges, const double *positive,
                       const uint8_t *reports, const uint8_t *actions,
                       double *belief, double *out) {
    for (uint32_t t = 0; t < count; ++t) {
        for (uint32_t i = 0; i < streams; ++i) {
            uint32_t event = t * streams + i;
            double *w = belief + i * q;
            double forecast = 0.0, normalizer = 0.0;
            for (uint8_t j = 0; j < q; ++j) {
                forecast += w[j] * positive[j];
                w[j] *= reports[event] ? positive[j] : 1.0 - positive[j];
                normalizer += w[j];
            }
            out[event] = forecast;
            const uint8_t *move = edges + actions[event] * q;
            for (uint8_t j = 0; j < q; ++j) w[j] /= normalizer;
            for (uint8_t j = 0; j < q; ++j) {
                uint8_t h = move[j];
                if (j < h) {
                    double temp = w[h];
                    w[h] = w[j];
                    w[j] = temp;
                }
            }
        }
    }
}
