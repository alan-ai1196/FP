/* Binary hidden-state filtering and smoothing. Every observation is scored
   before its word-dependent transition is applied. */
#include <math.h>
#include <stddef.h>

#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API
#endif

API void forward(int n, const double *e0, const double *e1, const double *r,
                 double *filtered, double *loss) {
  double state = 0.5;
  for (int t = 0; t < n; ++t) {
    double p = (1.0 - state) * e0[t] + state * e1[t];
    loss[t] = -log(p);
    filtered[t] = state * e1[t] / p;
    state = r[t] + (1.0 - 2.0 * r[t]) * filtered[t];
  }
}

API void smooth(int n, const double *e0, const double *e1, const double *r,
                const double *filtered, double *posterior, double *switches) {
  double next0 = 1.0, next1 = 1.0;
  for (int t = n - 1; t >= 0; --t) {
    double f = filtered[t];
    double b0 = (1.0 - r[t]) * next0 + r[t] * next1;
    double b1 = r[t] * next0 + (1.0 - r[t]) * next1;
    double total = (1.0 - f) * b0 + f * b1;
    posterior[t] = f * b1 / total;
    switches[t] = r[t] * ((1.0 - f) * next1 + f * next0) / total;
    next0 = e0[t] * b0;
    next1 = e1[t] * b1;
    double scale = next0 + next1;
    next0 /= scale;
    next1 /= scale;
  }
  switches[n - 1] = 0.0;
}

enum { LEVELS = 16, COINS = 256 };

static void allocate(double z, double mass, const double *grid, double *dest) {
  int hi = 0;
  while (hi < LEVELS && grid[hi] < z)
    ++hi;
  if (hi == 0 || hi == LEVELS || grid[hi] == z) {
    dest[hi == LEVELS ? LEVELS - 1 : hi] += mass;
    return;
  }
  int lo = hi - 1;
  double x = grid[lo], y = grid[hi];
  double a = (z - x) * y * (1.0 - y);
  double right = floor(COINS * a / (a + (y - z) * x * (1.0 - x)) + 0.5) / COINS;
  dest[lo] += mass * (1.0 - right);
  dest[hi] += mass * right;
}

API void finite_gate_scores(int n, const double *e0, const double *e1,
                            const double *r, double *det_loss,
                            double *random_loss) {
  double grid[LEVELS], live[LEVELS] = {0};
  for (int i = 0; i < LEVELS; ++i) {
    double a = (double)(i + 1), b = (double)(LEVELS - i);
    grid[i] = a * a / (a * a + b * b);
  }
  allocate(0.5, 1.0, grid, live);
  int index = LEVELS / 2;
  for (int t = 0; t < n; ++t) {
    double left = (LEVELS - index) * e0[t], right = (index + 1) * e1[t];
    double total = left + right;
    double p = total / (LEVELS + 1.0);
    det_loss[t] = -log(p);
    double z = (r[t] * left + (1.0 - r[t]) * right) / total;
    index = (int)floor(LEVELS * z);
    if (index >= LEVELS)
      index = LEVELS - 1;
    double following[LEVELS] = {0};
    random_loss[t] = 0.0;
    for (int i = 0; i < LEVELS; ++i) {
      if (live[i] == 0.0)
        continue;
      double v = grid[i];
      p = (1.0 - v) * e0[t] + v * e1[t];
      random_loss[t] -= live[i] * log(p);
      z = r[t] + (1.0 - 2.0 * r[t]) * v * e1[t] / p;
      allocate(z, live[i], grid, following);
    }
    double sum = 0.0;
    for (int i = 0; i < LEVELS; ++i)
      sum += following[i];
    for (int i = 0; i < LEVELS; ++i)
      live[i] = following[i] / sum;
  }
}
