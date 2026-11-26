/* Depth-first marginal evidence of a partially revealed binary automaton.
   Each prefix total uses only that prefix, even when collected in one tape
   pass. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

typedef struct {
  int n, neutral;
  double beta;
  const uint8_t *words;
  int *dest, *count, *incoming;
  double *mass, *roundoff;
  uint64_t *branches;
  int overflow;
} Tree;

static void visit(Tree *g, int t, int state, int rows, int used,
                  double weight) {
  if (g->overflow)
    return;
  int letter = g->words[t], key = 2 * state + letter;
  double emission =
      g->neutral ? 0.5
                 : (g->count[key] + 1.0) /
                       (g->count[2 * state] + g->count[2 * state + 1] + 2.0);
  double w = weight * emission;
  size_t bin = (size_t)t * g->n + (rows - 1);
  double y = w - g->roundoff[bin];
  double total = g->mass[bin] + y;
  g->roundoff[bin] = (total - g->mass[bin]) - y;
  g->mass[bin] = total;
  if (g->branches[t] == UINT64_MAX) {
    g->overflow = 1;
    return;
  }
  ++g->branches[t];
  if (t + 1 == g->n)
    return;
  ++g->count[key];
  if (g->dest[key] >= 0) {
    visit(g, t + 1, g->dest[key], rows, used, w);
  } else {
    double denominator = used + 1 + g->beta;
    for (int j = 0; j <= rows; ++j) {
      double numerator = j == rows ? g->beta : (double)g->incoming[j];
      ++g->incoming[j];
      g->dest[key] = j;
      visit(g, t + 1, j, rows + (j == rows), used + 1,
            w * numerator / denominator);
      --g->incoming[j];
    }
    g->dest[key] = -1;
  }
  --g->count[key];
}

EXPORT int birth_tree(int n, const uint8_t *words, double beta, int neutral,
                      double *mass, uint64_t *branches) {
  if (n < 1 || !(beta > 0))
    return 0;
  Tree g = {0};
  g.n = n;
  g.words = words;
  g.beta = beta;
  g.neutral = neutral;
  g.mass = mass;
  g.branches = branches;
  size_t bins = (size_t)n * (size_t)n;
  g.roundoff = (double *)calloc(bins, sizeof(double));
  g.dest = (int *)malloc((size_t)2 * n * sizeof(int));
  g.count = (int *)calloc((size_t)2 * n, sizeof(int));
  g.incoming = (int *)calloc((size_t)n, sizeof(int));
  if (g.roundoff && g.dest && g.count && g.incoming) {
    for (size_t i = 0; i < (size_t)2 * n; ++i)
      g.dest[i] = -1;
    g.incoming[0] = 1;
    memset(mass, 0, bins * sizeof(double));
    memset(branches, 0, (size_t)n * sizeof(uint64_t));
    visit(&g, 0, 0, 1, 0, 1.0);
  } else
    g.overflow = 1;
  free(g.incoming);
  free(g.count);
  free(g.dest);
  free(g.roundoff);
  return !g.overflow;
}
