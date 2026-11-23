/* Each stream starts with a uniform belief. Only purchased feedback is read.
   The likelihood bank has 24 entries in the supplied anonymous column order. */
#include <math.h>
#include <string.h>
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif

typedef unsigned char u8;

static unsigned retained(const u8 *header, unsigned j) {
  return (header[2 + j / 8] >> (j % 8)) & 1u;
}

static unsigned code(const u8 *header, unsigned h, unsigned arm) {
  return (header[2 + h] >> (2 * arm)) & 3u;
}

static void weights(unsigned mode, const u8 *bank, const u8 *header,
                    const double *basis, unsigned rank, const double *state,
                    double *w) {
  double top, total = 0.;
  unsigned keep = 0, rest = 0;
  for (unsigned h = 0; h < 24; h++) {
    double logw = 0.;
    if (mode == 0)
      logw = state[h];
    if (mode == 1 && h)
      logw = state[h - 1];
    if (mode == 2 && h)
      for (unsigned k = 0; k < rank; k++)
        logw += state[k] * basis[23 * k + h - 1];
    if (mode == 4 && h) {
      if (retained(header, h - 1))
        logw = state[keep++];
      else {
        for (unsigned i = 0; i < rank; i++)
          logw += state[i] * basis[(23 - rank) * i + rest];
        rest++;
      }
    }
    if (mode == 3 || mode == 5)
      for (unsigned j = 0; j < 3; j++) {
        unsigned id = mode == 3 ? bank[4 * h + j] : code(header, h, j);
        if (id < 3)
          logw += state[3 * j + id];
      }
    w[h] = logw;
  }
  top = w[0];
  for (unsigned h = 1; h < 24; h++)
    if (w[h] > top)
      top = w[h];
  for (unsigned h = 0; h < 24; h++) {
    w[h] = exp(w[h] - top);
    total += w[h];
  }
  for (unsigned h = 0; h < 24; h++)
    w[h] /= total;
}

static void update(unsigned mode, const u8 *bank, const u8 *header,
                   const double *basis, unsigned rank, double *state,
                   unsigned j, const double *ell) {
  if (mode == 4) {
    unsigned k = 0;
    for (unsigned h = 1; h < 24; h++)
      if (retained(header, h - 1))
        state[k++] += ell[bank[4 * h + j]] - ell[bank[j]];
    return;
  }
  if (mode == 3 || mode == 5) {
    double aligned[4] = {0., 0., 0., 0.};
    if (mode == 5) {
      for (unsigned h = 0; h < 24; h++)
        aligned[code(header, h, j)] = ell[bank[4 * h + j]];
      ell = aligned;
    }
    for (unsigned y = 0; y < 3; y++) {
      double d = ell[y] - ell[3];
      if (j < 3)
        state[3 * j + y] += d;
      else
        for (unsigned i = 0; i < 3; i++)
          state[3 * i + y] -= d;
    }
    return;
  }
  if (mode == 0) {
    for (unsigned h = 0; h < 24; h++)
      state[h] += ell[bank[4 * h + j]];
    return;
  }
  double x[23], ref = ell[bank[j]];
  for (unsigned h = 1; h < 24; h++)
    x[h - 1] = ell[bank[4 * h + j]] - ref;
  if (mode == 1) {
    for (unsigned h = 0; h < 23; h++)
      state[h] += x[h];
  } else {
    for (unsigned k = 0; k < rank; k++) {
      double d = 0.;
      for (unsigned h = 0; h < 23; h++)
        d += x[h] * basis[23 * k + h];
      state[k] += d;
    }
  }
}

API void replay_updates(unsigned mode, unsigned streams, unsigned steps,
                        unsigned rank, const double *basis, const u8 *header,
                        const u8 *bank, const double *word, const u8 *arm,
                        const double *price, const u8 *outcome, double *states,
                        double *out, u8 *decision) {
  unsigned width = mode == 0 ? 24 : (mode == 1 ? 23 : (mode == 2 ? rank : 9));
  for (unsigned s = 0; s < streams; s++) {
    double *state = states + width * s;
    memset(state, 0, width * sizeof(double));
    for (unsigned step = 0; step < steps; step++) {
      unsigned n = s * steps + step, j = arm[n];
      const double *p = word + 4 * n;
      double w[24];
      weights(mode, bank, header, basis, rank, state, w);
      for (unsigned i = 0; i < 4; i++) {
        double q = 0.;
        for (unsigned h = 0; h < 24; h++)
          q += w[h] * p[bank[4 * h + i]];
        out[4 * n + i] = q;
      }
      double threshold = fmax(1. / 32, fmin(29. / 32, out[4 * n + j]));
      decision[n] = (threshold >= price[n]);
      if (decision[n]) {
        double ell[4];
        for (unsigned y = 0; y < 4; y++)
          ell[y] = outcome[n] ? log(p[y]) : log1p(-p[y]);
        update(mode, bank, header, basis, rank, state, j, ell);
      }
    }
  }
}
