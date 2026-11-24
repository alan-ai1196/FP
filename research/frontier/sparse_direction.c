#include <math.h>
#include <stdint.h>
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif

static int16_t q15(double s) {
  double z = 32767.0 * s;
  if (z > 32767.0) z = 32767.0;
  if (z < -32767.0) z = -32767.0;
  return (int16_t)round(z);
}

API void error_grid(uint32_t n, uint32_t d, const double *q, const uint8_t *y,
                    double rate, int16_t *state, double *history) {
  for (uint32_t t=0; t<n; ++t, q+=d) {
    for (uint32_t i=0; i<d; ++i) {
      double s=state[i]/32767.0;
      *history++=s;
      state[i]=q15(s+rate*((i==y[t] ? 1.0 : 0.0)-q[i]-s));
    }
  }
}

/* A row of unmodified categories retains its full total probability.
   Fall back to positive summation when subtracting mass would lose precision. */
API uint32_t subset_stream(uint32_t n, uint32_t d, const double *q,
                           const uint8_t *y, uint32_t count, const uint8_t *col,
                           const double *gamma, double rate, uint32_t packed,
                           void *carry, double *delta) {
  uint32_t repairs=0;
  for (uint32_t t=0; t<n; ++t,q+=d) {
    double adjustment=0.0, applied=0.0;
    for (uint32_t j=0; j<count; ++j) {
      double s=packed ? ((int16_t *)carry)[j]/32767.0 : ((double *)carry)[j];
      double z=gamma[j]*s;
      adjustment+=q[col[j]]*expm1(z);
      if (col[j]==y[t]) applied=z;
    }
    if (adjustment < -0.5) {
      double total=0.0;
      uint32_t j=0;
      for (uint32_t i=0; i<d; ++i) {
        if (j<count && col[j]==i) {
          double s=packed ? ((int16_t *)carry)[j]/32767.0 : ((double *)carry)[j];
          total+=q[i]*exp(gamma[j]*s);
          ++j;
        } else total+=q[i];
      }
      delta[t]=log(total)-applied;
      ++repairs;
    } else delta[t]=log1p(adjustment)-applied;
    for (uint32_t j=0; j<count; ++j) {
      uint32_t i=col[j];
      double s=packed ? ((int16_t *)carry)[j]/32767.0 : ((double *)carry)[j];
      s+=rate*((i==y[t] ? 1.0 : 0.0)-q[i]-s);
      if (packed) ((int16_t *)carry)[j]=q15(s);
      else ((double *)carry)[j]=s;
    }
  }
  return repairs;
}
