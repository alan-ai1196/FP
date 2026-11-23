#include <math.h>
#include <stddef.h>
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

/* Registered calibration experiments have at most 2^9 codes and 2^18 pairs. */
API uint32_t packet_for_matches(uint32_t matches, uint32_t n, uint32_t bits) {
  uint32_t levels = 1u << bits, den = 8u * levels;
  uint32_t lo = 0, hi = levels;
  while (hi - lo > 1) {
    uint32_t j = lo + (hi - lo) / 2, x = 5u * levels + 2u * j;
    uint64_t boundary = (uint64_t)x * x + (uint64_t)(den - x) * (den - x);
    if ((uint64_t)matches * den * den >= (uint64_t)n * boundary)
      lo = j;
    else
      hi = j;
  }
  return lo;
}

API uint32_t pair_packet(const uint8_t *pairs, uint32_t n, uint32_t bits) {
  uint32_t matches = 0;
  for (uint32_t i = 0; i < n; ++i)
    matches += (uint32_t)(pairs[2 * i] == pairs[2 * i + 1]);
  return packet_for_matches(matches, n, bits);
}

/* Five positive-side center values for counts 0 through 4, then the fitted
   bias. Reflection supplies the negative side. All six integers are Q12. */
API void calibrated_stream(uint32_t streams, uint32_t steps, int8_t limit,
                           const uint16_t *release, const uint8_t *bits,
                           int8_t *carry, double *output) {
  for (uint32_t i = 0; i < streams; ++i) {
    int8_t s = carry[i];
    for (uint32_t t = 0; t < steps; ++t) {
      int magnitude = s >= 0 ? s : -s;
      uint16_t q = release[magnitude <= 4 && magnitude < limit ? magnitude : 5];
      *output++ = (s >= 0 ? q : 4096 - q) / 4096.0;
      int move = 2 * (*bits++) - 1;
      if (magnitude < limit)
        s = (int8_t)(s + move);
    }
    carry[i] = s;
  }
}

/* Reconstruct the grid posterior from two counts, including on reversed runs.
 */
API void grid_from_counts(uint32_t streams, uint32_t steps, uint32_t components,
                          const double *table, const uint8_t *bits,
                          uint32_t *carry, double *output) {
  const double *lp = table + components, *lq = lp + components;
  const double *prior = lq + components;
  for (uint32_t i = 0; i < streams; ++i) {
    uint32_t ones = carry[2 * i], zeros = carry[2 * i + 1];
    for (uint32_t t = 0; t < steps; ++t) {
      double top = -HUGE_VAL, mass = 0, sum = 0;
      for (uint32_t j = 0; j < components; ++j) {
        double value = prior[j] + ones * lp[j] + zeros * lq[j];
        if (value > top)
          top = value;
      }
      for (uint32_t j = 0; j < components; ++j) {
        double w = exp(prior[j] + ones * lp[j] + zeros * lq[j] - top);
        mass += w;
        sum += w * table[j];
      }
      *output++ = sum / mass;
      uint8_t one = *bits++;
      ones += one;
      zeros += 1u - one;
    }
    carry[2 * i] = ones;
    carry[2 * i + 1] = zeros;
  }
}

/* Cache posterior weights between log-space reconstructions from the counts. */
API void grid_with_weights(uint32_t streams, uint32_t steps,
                           uint32_t components, const double *table,
                           const uint8_t *bits, uint32_t *carry,
                           double *weights, double *output) {
  const double *lp = table + components, *lq = lp + components;
  const double *prior = lq + components;
  for (uint32_t i = 0; i < streams; ++i) {
    uint32_t ones = carry[2 * i], zeros = carry[2 * i + 1];
    double *w = weights + (size_t)i * components;
    for (uint32_t t = 0; t < steps; ++t) {
      if ((ones + zeros) % 128u == 0) {
        double peak = -HUGE_VAL;
        for (uint32_t j = 0; j < components; ++j) {
          w[j] = prior[j] + ones * lp[j] + zeros * lq[j];
          if (w[j] > peak)
            peak = w[j];
        }
        for (uint32_t j = 0; j < components; ++j)
          w[j] = exp(w[j] - peak);
      }
      double positive = 0, mass = 0;
      for (uint32_t j = 0; j < components; ++j) {
        positive += w[j] * table[j];
        mass += w[j];
      }
      *output++ = positive / mass;
      uint8_t one = *bits++;
      double norm = 1.0 / (one ? positive : mass - positive);
      for (uint32_t j = 0; j < components; ++j) {
        double next = w[j] * ((one ? table[j] : 1.0 - table[j]) * norm);
        w[j] = next < 1e-180 ? 0.0 : next;
      }
      ones += one;
      zeros += 1u - one;
    }
    carry[2 * i] = ones;
    carry[2 * i + 1] = zeros;
  }
}
