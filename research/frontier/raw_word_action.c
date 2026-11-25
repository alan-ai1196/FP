/* Exact one-name refits on a chronological tape with two or four readout rows. */
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

#define K 17
typedef int Counts[4][K];
typedef struct {
    int n, rows, mode;
    const uint16_t *x;
    const uint8_t *y;
    uint8_t *action, *state;
    int *offset, *occurrence, *changed;
    double *cell[K], *total;
    uint64_t visits;
} Tape;

static int step(int mode, int s, int a) {
    if (mode == 2) return (2 * s + a) & 3;
    return a < 2 ? a : s ^ (a - 2);
}

/* Enumerate only rows whose state changes. Keep the original state intact
   until all occurrences have been compared, including adjacent repetitions. */
static int alternative(Tape *t, int name, int a, Counts ct) {
    int count = 0, last = -1, different = 0;
    int lo = t->offset[name], hi = t->offset[name + 1];
    for (int p = lo; p < hi; ++p) {
        int i = t->occurrence[p], end = p + 1 < hi ? t->occurrence[p + 1] : t->n;
        if (t->mode == 2) {
            int previous = i ? (t->x[i-1] == name ? a : t->action[t->x[i-1]]) : 0;
            int s = 2 * previous + a;
            int limit = i + 2 < end ? i + 2 : end;
            for (int j = i; j < limit; ++j) {
                if (j != i) s = 2 * a + t->action[t->x[j]];
                int old = t->state[j], y = t->y[j];
                if (old != s) {
                    --ct[old][y]; ++ct[s][y];
                    t->changed[count++] = j;
                }
                ++t->visits;
            }
        } else {
            int previous = i ? t->state[i-1] : 0;
            if (last == i) previous ^= different;
            different = step(t->mode, previous, a) ^ t->state[i];
            last = i;
            if (!different) continue;
            while (last < end) {
                if (last != i && t->action[t->x[last]] < 2) break;
                int old = t->state[last], y = t->y[last];
                --ct[old][y]; ++ct[1-old][y];
                t->changed[count++] = last++;
                ++t->visits;
            }
        }
    }
    return count;
}

static double evidence(const Tape *t, Counts ct) {
    double out = 0.0;
    for (int s = 0; s < t->rows; ++s) {
        int sum = 0;
        for (int k = 0; k < K; ++k) {
            sum += ct[s][k];
            out += t->cell[k][ct[s][k]];
        }
        out -= t->total[sum];
    }
    return out;
}

static void rising(double *out, int n, double alpha) {
    out[0] = 0;
    for (int i = 0; i < n; ++i) out[i+1] = out[i] + log(alpha + i);
}

/* Inputs are validated by the caller; mode 0 = four maps, 1/2 = learned-bit suffix. */
EXPORT int fit_actions(int n, int d, int mode, const uint16_t *x, const uint8_t *y,
                       const double *alpha, int distinct, const int *order,
                       int default_action, double penalty, int sweeps,
                       uint8_t *action, int *moves, double *history, uint64_t *visits) {
    Tape t = {0};
    Counts ct = {{0}}, trial;
    int result = -1, global[K] = {0};
    t.n = n; t.rows = mode == 2 ? 4 : 2; t.mode = mode;
    t.x = x; t.y = y; t.action = action;
    t.state = (uint8_t *)malloc((size_t)n);
    t.offset = (int *)calloc((size_t)d + 1, sizeof(int));
    t.occurrence = (int *)malloc((size_t)n * sizeof(int));
    t.changed = (int *)malloc((size_t)n * sizeof(int));
    int *cursor = (int *)malloc((size_t)d * sizeof(int));
    /* Total length of the K class tables is n + K, plus n+1 row totals. */
    double *cells = (double *)malloc(((size_t)2*n + K + 1) * sizeof(double));
    if (!t.state || !t.offset || !t.occurrence || !t.changed || !cursor || !cells) goto cleanup;
    int state = 0;
    for (int i = 0; i < n; ++i) {
        ++t.offset[x[i]+1]; ++global[y[i]];
        state = step(mode, state, action[x[i]]);
        t.state[i] = (uint8_t)state; ++ct[state][y[i]];
    }
    for (int a = 0; a < d; ++a) t.offset[a+1] += t.offset[a];
    memcpy(cursor, t.offset, (size_t)d * sizeof(int));
    for (int i = 0; i < n; ++i) t.occurrence[cursor[x[i]]++] = i;
    int pos = 0, overrides = 0;
    double mass = 0;
    for (int k = 0; k < K; ++k) {
        t.cell[k] = cells + pos; pos += global[k] + 1; mass += alpha[k];
        rising(t.cell[k], global[k], alpha[k]);
    }
    t.total = cells + pos; rising(t.total, n, mass);
    for (int a = 0; a < d; ++a) overrides += action[a] != default_action;
    double value = evidence(&t, ct);
    history[0] = value - overrides * penalty;
    for (int pass = 0; pass < sweeps; ++pass) {
        int accepted = 0;
        for (int j = 0; j < distinct; ++j) {
            int a = order[(pass & 1) ? distinct-1-j : j], old = action[a], best = old;
            double best_score = value - (old != default_action) * penalty;
            for (int candidate = 0; candidate < (mode ? 2 : 4); ++candidate) {
                if (candidate == old) continue;
                memcpy(trial, ct, sizeof(ct));
                alternative(&t, a, candidate, trial);
                double score = evidence(&t, trial) - (candidate != default_action) * penalty;
                if (score > best_score + 1e-8) { best_score = score; best = candidate; }
            }
            if (best != old) {
                int changed = alternative(&t, a, best, ct);
                action[a] = (uint8_t)best;
                for (int k = 0; k < changed; ++k) {
                    int i = t.changed[k];
                    t.state[i] = (uint8_t)(mode == 2 ?
                        2 * (i ? action[x[i-1]] : 0) + action[x[i]] : 1 - t.state[i]);
                }
                overrides += (best != default_action) - (old != default_action);
                value = best_score + (best != default_action) * penalty;
                ++accepted;
            }
        }
        moves[pass] = accepted;
        history[pass+1] = value - overrides * penalty;
        result = pass + 1;
        if (!accepted) break;
    }
    *visits = t.visits;
cleanup:
    free(cells); free(cursor); free(t.changed); free(t.occurrence); free(t.offset); free(t.state);
    return result;
}

EXPORT void states(int n, int mode, int initial, const uint16_t *x,
                   const uint8_t *action, uint8_t *out) {
    int state = initial;
    for (int i = 0; i < n; ++i) {
        state = step(mode, state, action[x[i]]);
        out[i] = (uint8_t)state;
    }
}
