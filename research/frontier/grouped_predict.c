#include <math.h>
#include <stddef.h>
#include <stdint.h>

#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif

/* One packed decision for each possible first bit. */
API void purchase(uint32_t n, uint8_t policy, const uint8_t *first,
                  uint8_t *action) {
  for (uint32_t i = 0; i < n; ++i)
    action[i] = (uint8_t)((policy >> first[i]) & 1u);
}

static double factor(uint32_t t, uint32_t k, uint32_t degree,
                     const int16_t *coeff) {
  uint32_t last = degree < t ? degree : t;
  double z = 2.0 * k - t, before = 1.0, current = z / (t + 1.0);
  double sum = 0.0;
  for (uint32_t j = 0; j < last; ++j) {
    sum += coeff[j] * current;
    if (j + 1 < last) {
      double after = (2.0 * z * current - (t - (double)j) * before) /
                     (t + 2.0 + j);
      before = current;
      current = after;
    }
  }
  return 1.0 + (2.0 / 32767.0) * sum;
}

API void harmonic_stream(uint32_t streams, uint32_t steps, uint32_t degree,
                         const int16_t *coeff, const uint8_t *history,
                         const uint8_t *bits, uint32_t *carry, double *out) {
  for (uint32_t i = 0; i < streams; ++i) {
    const int16_t *row = coeff + history[i] * degree;
    uint32_t t = carry[2 * i], k = carry[2 * i + 1];
    for (uint32_t j = 0; j < steps; ++j) {
      double kt = (k + 0.5) / (t + 1.0);
      *out++ = kt * factor(t + 1, k + 1, degree, row) /
               factor(t, k, degree, row);
      k += *bits++;
      ++t;
    }
    carry[2 * i] = t;
    carry[2 * i + 1] = k;
  }
}

/* At depth zero this is the universal half-count forecast. For positive
   depth the triangular array contains the conditional prefix forecasts. */
API void prefix_stream(uint32_t streams, uint32_t steps, uint32_t depth,
                       const double *table, const uint8_t *history,
                       const uint8_t *bits, uint32_t *carry, double *out) {
  size_t triangle = (size_t)depth * (depth + 1u) / 2u;
  for (uint32_t i = 0; i < streams; ++i) {
    const double *row = table + history[i] * triangle;
    uint32_t t = carry[2 * i], k = carry[2 * i + 1];
    for (uint32_t j = 0; j < steps; ++j) {
      *out++ = t < depth ? row[(size_t)t * (t + 1u) / 2u + k]
                         : (k + 0.5) / (t + 1.0);
      k += *bits++;
      ++t;
    }
    carry[2 * i] = t;
    carry[2 * i + 1] = k;
  }
}

/* Each atom has its probability, log mass, log success and log failure.
   Conditional weights are recovered in log space every 64 draws or on every
   query for the two-count version. An extra component is the half-count rule. */
static void grid_posterior(uint32_t t, uint32_t k, uint32_t atoms,
                           const double *table, double floor_log, double *w) {
  uint32_t zeros = t - k;
  double kt = lgamma(k + 0.5) + lgamma(zeros + 0.5) - lgamma(t + 1.0)
              - 1.1447298858494001741; /* log(pi) */
  w[atoms] = floor_log + kt;
  double high = w[atoms];
  for (uint32_t a = 0; a < atoms; ++a) {
    const double *entry = table + 4 * a;
    w[a] = entry[1] + (k ? k * entry[2] : 0.0)
                    + (zeros ? zeros * entry[3] : 0.0);
    if (w[a] > high)
      high = w[a];
  }
  double sum = 0.0;
  for (uint32_t a = 0; a <= atoms; ++a) {
    w[a] = exp(w[a] - high);
    sum += w[a];
  }
  for (uint32_t a = 0; a <= atoms; ++a)
    w[a] /= sum;
}

API void grid_stream(uint32_t streams, uint32_t steps, uint32_t stride,
                     double floor_log, const uint16_t *offsets,
                     const double *table, const uint8_t *history,
                     const uint8_t *bits, uint32_t *carry, double *weights,
                     double *out) {
  for (uint32_t i = 0; i < streams; ++i) {
    uint32_t row = history[i], start = offsets[row];
    uint32_t atoms = (uint32_t)offsets[row + 1] - start;
    const double *entries = table + 4 * start;
    double *w = weights + (size_t)i * stride;
    uint32_t t = carry[2 * i], k = carry[2 * i + 1];
    for (uint32_t j = 0; j < steps; ++j) {
      if (stride == 0 || t % 64 == 0)
        grid_posterior(t, k, atoms, entries, floor_log, w);
      double kt = (k + 0.5) / (t + 1.0);
      double yes = w[atoms] * kt, no = w[atoms] * (1.0 - kt);
      for (uint32_t a = 0; a < atoms; ++a) {
        double p = entries[4 * a];
        yes += w[a] * p;
        no += w[a] * (1.0 - p);
      }
      *out++ = yes / (yes + no);
      uint32_t y = *bits++;
      if (stride) {
        double normalizer = y ? yes : no;
        for (uint32_t a = 0; a < atoms; ++a) {
          double p = entries[4 * a];
          w[a] *= (y ? p : 1.0 - p) / normalizer;
        }
        w[atoms] *= (y ? kt : 1.0 - kt) / normalizer;
      }
      k += y;
      ++t;
    }
    carry[2 * i] = t;
    carry[2 * i + 1] = k;
  }
}
