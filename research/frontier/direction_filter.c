#include <math.h>
#include <stdint.h>

#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif

/* Emit the loss correction to the raw-word model. All words in a category
   share the same multiplier, including the complementary vocabulary. */
API void direction_stream(uint32_t n, uint32_t d, const double *q,
                          const uint8_t *targets, const double *input,
                          const double *output, double gain, double rate,
                          double spread, uint32_t quantized, void *carry,
                          double *delta) {
  double s = quantized ? *((int16_t *)carry) * spread / 32767.0 : *((double *)carry);
  int16_t code = quantized ? *((int16_t *)carry) : 0;
  for (uint32_t t = 0; t < n; ++t, q += d) {
    double expected = 0.0, total = 0.0, z = gain * s;
    uint32_t y = targets[t];
    for (uint32_t c = 0; c < d; ++c) {
      expected += q[c] * input[c];
      total += q[c] * exp(z * output[c]);
    }
    delta[t] = log(total) - z * output[y];
    s += rate * (input[y] - expected - s);
    if (quantized && spread > 0.0) {
      double grid = s * 32767.0 / spread;
      grid = grid < -32767.0 ? -32767.0 : (grid > 32767.0 ? 32767.0 : grid);
      code = (int16_t)round(grid);
      s = code * spread / 32767.0;
    }
  }
  if (quantized)
    *((int16_t *)carry) = code;
  else
    *((double *)carry) = s;
}

API void diagonal_stream(uint32_t n, uint32_t d, const double *q,
                         const uint8_t *targets, const double *gain,
                         double rate, double *carry, double *delta) {
  for (uint32_t t = 0; t < n; ++t, q += d) {
    uint32_t y = targets[t];
    double sum = 0.0, applied = carry[y] * gain[y];
    for (uint32_t c = 0; c < d; ++c) {
      sum += q[c] * exp(carry[c] * gain[c]);
      carry[c] += rate * (((c == y) ? 1.0 : 0.0) - q[c] - carry[c]);
    }
    delta[t] = log(sum) - applied;
  }
}
