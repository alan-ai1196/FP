#include <stdint.h>
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif

/* The input and output are stream-major. All releases precede the next update.
 */
API void counter_stream(uint32_t streams, uint32_t steps, int8_t limit,
                        const uint8_t *bits, int8_t *carry, double *output) {
  for (uint32_t i = 0; i < streams; ++i) {
    int8_t s = carry[i];
    for (uint32_t t = 0; t < steps; ++t) {
      double p = 0.5 + s * 0.125;
      if (s < -1 || s == -limit)
        p = 0.25;
      if (s > 1 || s == limit)
        p = 0.75;
      *output++ = p;
      int move = 2 * (*bits++) - 1;
      if (s > -limit && s < limit)
        s = (int8_t)(s + move);
    }
    carry[i] = s;
  }
}

API void graph_stream(uint32_t streams, uint32_t steps, const uint8_t *table,
                      const double *emit, const uint8_t *bits, uint8_t *carry,
                      double *output) {
  for (uint32_t i = 0; i < streams; ++i) {
    uint8_t s = carry[i];
    for (uint32_t t = 0; t < steps; ++t) {
      *output++ = emit[s];
      s = table[2 * s + (*bits++)];
    }
    carry[i] = s;
  }
}

API void half_count_stream(uint32_t streams, uint32_t steps,
                           const uint8_t *bits, uint32_t *carry,
                           double *output) {
  for (uint32_t i = 0; i < streams; ++i) {
    uint32_t successes = carry[2 * i], n = carry[2 * i + 1];
    for (uint32_t t = 0; t < steps; ++t) {
      *output++ = (successes + 0.5) / (n + 1.0);
      successes += *bits++;
      ++n;
    }
    carry[2 * i] = successes;
    carry[2 * i + 1] = n;
  }
}
