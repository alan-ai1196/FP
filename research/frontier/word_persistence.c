#include <math.h>
#include <stdint.h>
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif

/* Losses are relative to the frozen raw-word predictor. For either possible
   class, multiplying the base probability by ell gives its full-word mass. */
API double hidden_fit(uint32_t n, const double *r, const uint8_t *y,
                      const double *x, double *gradient) {
  double a = exp(x[0]), b = exp(x[1]), pi = x[2], h = x[3], w = pi;
  double dw[4] = {0.0, 0.0, 1.0, 0.0};
  double loss = 0.0;
  for (uint32_t j = 0; j < 4; ++j)
    gradient[j] = 0.0;
  for (uint32_t i = 0; i < n; ++i) {
    double den0 = 1.0 + (a - 1.0) * r[i], den1 = 1.0 + (b - 1.0) * r[i];
    double p0 = a * r[i] / den0, p1 = b * r[i] / den1;
    double ell0 = (y[i] ? a : 1.0) / den0, ell1 = (y[i] ? b : 1.0) / den1;
    double ell = (1.0 - w) * ell0 + w * ell1;
    double u = w * ell1 / ell;
    double dl[4] = {p0 - y[i], y[i] - p1, 0.0, 0.0};
    loss -= log(ell);
    for (uint32_t j = 0; j < 4; ++j) {
      gradient[j] -= (ell1 - ell0) / ell * dw[j];
      double du = u * (1.0 - u) * (dw[j] / (w * (1.0 - w)) + dl[j]);
      dw[j] = (1.0 - h) * du + (j == 2 ? h : 0.0) + (j == 3 ? pi - u : 0.0);
    }
    gradient[0] += (1.0 - u) * (p0 - y[i]);
    gradient[1] += u * (p1 - y[i]);
    w = (1.0 - h) * u + h * pi;
  }
  return loss;
}

API double residual_fit(uint32_t n, const double *r, const uint8_t *y,
                        const double *x, double *gradient) {
  double s = 0.0, ds = 0.0, loss = 0.0, rate = x[2];
  gradient[0] = gradient[1] = gradient[2] = 0.0;
  for (uint32_t i = 0; i < n; ++i) {
    double z = x[0] + x[1] * s, odds = exp(z);
    double den = 1.0 + (odds - 1.0) * r[i], diff = odds * r[i] / den - y[i];
    loss += log(den) - y[i] * z;
    gradient[0] += diff;
    gradient[1] += diff * s;
    gradient[2] += diff * x[1] * ds;
    ds = (1.0 - rate) * ds + y[i] - r[i] - s;
    s = (1.0 - rate) * s + rate * (y[i] - r[i]);
  }
  return loss;
}

static double log_odds(double p) { return log(p) - log1p(-p); }

API void hidden_stream(uint32_t n, const double *r, const uint8_t *y,
                       const double *x, uint32_t levels, void *carry,
                       double *forecast) {
  double a = exp(x[0]), b = exp(x[1]), pi = x[2], h = x[3];
  double lo = log_odds(h * pi), hi = log_odds(1.0 - h * (1.0 - pi));
  double step = levels && h < 1.0 ? (hi - lo) / (levels - 1.0) : 0.0;
  uint32_t code = levels == 256 ? *((uint8_t *)carry)
                  : levels ? *((uint16_t *)carry) : 0u;
  double w = levels ? (step ? 1.0 / (1.0 + exp(-(lo + step * code))) : pi)
                    : *((double *)carry);
  for (uint32_t i = 0; i < n; ++i) {
    double den0 = 1.0 + (a - 1.0) * r[i], den1 = 1.0 + (b - 1.0) * r[i];
    double ell0 = (y[i] ? a : 1.0) / den0, ell1 = (y[i] ? b : 1.0) / den1;
    forecast[i] = r[i] * ((1.0 - w) * a / den0 + w * b / den1);
    w = (1.0 - h) * w * ell1 / ((1.0 - w) * ell0 + w * ell1) + h * pi;
    if (step) {
      double grid = (log_odds(w) - lo) / step;
      if (grid < 0.0)
        grid = 0.0;
      if (grid > levels - 1.0)
        grid = levels - 1.0;
      code = (uint32_t)floor(grid + 0.5);
      w = 1.0 / (1.0 + exp(-(lo + step * code)));
    }
  }
  if (levels == 256)
    *((uint8_t *)carry) = (uint8_t)code;
  else if (levels)
    *((uint16_t *)carry) = (uint16_t)code;
  else
    *((double *)carry) = w;
}

API void residual_stream(uint32_t n, const double *r, const uint8_t *y,
                         const double *x, double *carry, double *forecast) {
  double s = *carry, rate = x[2];
  for (uint32_t i = 0; i < n; ++i) {
    double odds = exp(x[0] + x[1] * s);
    forecast[i] = odds * r[i] / (1.0 + (odds - 1.0) * r[i]);
    s = (1.0 - rate) * s + rate * (y[i] - r[i]);
  }
  *carry = s;
}
