/* Packed, shared history lookups and mass-preserving corrections on disjoint
 * outputs. */
#include "address_score.c"

typedef struct {
  const u8 *map[3], *head[2], *raw;
  u32 slots[3], nmap, nhead, source, source_map, tau, rows, use_raw;
} SharedModel;

FN SharedModel parse_shared(const u8 *base) {
  SharedModel m;
  const u8 *p = base + 24 + 5 * val16(base);
  m.source = val16(p);
  m.nmap = p[2];
  m.nhead = p[3];
  m.source_map = p[4];
  m.tau = p[5];
  m.rows = val32(p + 8);
  p += 12;
  u32 varied = 0;
  for (u32 i = 0; i < m.nmap; i++) {
    m.map[i] = p;
    m.slots[i] = varied;
    if (p[0])
      varied++;
    u32 n = val16(p + 2), stride = 0;
    if (p[0] == 1)
      stride = 2 * n + (n + 1) / 2;
    if (p[0] == 2)
      stride = (50257 + 1) / 2;
    if (p[0] == 3)
      stride = 6 * n;
    p += 4 + stride;
  }
  for (u32 i = 0; i < m.nhead; i++) {
    m.head[i] = p;
    p += 10 + (p[0] == 2 ? 12 : (p[0] == 1 ? 54 : 6));
  }
  m.raw = p;
  m.use_raw = (varied > 2 || m.rows);
  return m;
}

FN u32 raw_address(const u8 *map, u32 u, const u32 *counts) {
  u32 mode = map[0], fallback = map[1], n = val16(map + 2);
  const u8 *p = map + 4;
  if (mode == 0)
    return fallback;
  if (mode == 3) {
    u32 z = 0;
    for (u32 j = 0; j < n; j++) {
      u32 f = val32(p + 6 * j);
      z += (counts[u] < f || (counts[u] == f && u > val16(p + 6 * j + 4)));
    }
    return z;
  }
  u32 index = u;
  if (mode == 1) {
    index = lower_id(p, n, 2, u);
    if (index == n || val16(p + 2 * index) != u)
      return fallback;
    p += 2 * n;
  }
  return (p[index / 2] >> (4 * (index % 2))) & 15u;
}

FN u32 save_shared(const SharedModel *m, u32 u, const u32 *counts) {
  if (m->use_raw)
    return u;
  u32 state = 0;
  for (u32 i = 0; i < m->nmap; i++) {
    if (m->map[i][0])
      state |= raw_address(m->map[i], u, counts) << (4 * m->slots[i]);
  }
  return state;
}

FN u32 saved_code(const SharedModel *m, u32 i, u32 state, const u32 *counts) {
  const u8 *map = m->map[i];
  if (!map[0])
    return map[1];
  if (m->use_raw)
    return raw_address(map, state, counts);
  return (state >> (4 * m->slots[i])) & 15u;
}

FN double source_odds(u32 s) {
  const u8 numer[9] = {1, 2, 3, 4, 5, 6, 8, 12, 16};
  return numer[s] * .25;
}

FN const u8 *raw_row(const SharedModel *m, u32 group, u32 older, u32 q) {
  u32 lo = 0, hi = m->rows;
  while (lo < hi) {
    u32 mid = lo + (hi - lo) / 2;
    const u8 *r = m->raw + 13 * mid;
    u32 u = val16(r + 1);
    if (r[0] < group ||
        (r[0] == group && (u < older || (u == older && val16(r + 3) < q))))
      lo = mid + 1;
    else
      hi = mid;
  }
  if (lo == m->rows)
    return 0;
  const u8 *p = m->raw + 13 * lo;
  return p[0] == group && val16(p + 1) == older && val16(p + 3) == q ? p + 5
                                                                     : 0;
}

FN double pooled_probability(const u8 *base, u32 q, u32 y, const u32 *unigram,
                             const u32 *outgoing, const u32 *offset,
                             const u16 *successor, const u32 *freq) {
  return (base_count(q, y, offset, successor, freq) +
          64.0 * backoff(base, 0, y, unigram)) /
         (outgoing[q] + 64.0);
}

FN double signed_fixed(const u8 *p) {
  u32 value = val16(p);
  return (value < 32768 ? (double)value : (double)value - 65536.0) / 1024.0;
}

FN double shared_loss(const u8 *base, const SharedModel *m, u32 state, u32 q,
                      u32 y, const u32 *unigram, const u32 *outgoing,
                      const u32 *offset, const u16 *succ, const u32 *freq) {
  double observed =
      pooled_probability(base, q, y, unigram, outgoing, offset, succ, freq);
  double prob = observed;
  for (u32 g = 0; g < m->nhead; g++) {
    const u8 *h = m->head[g];
    u32 index = 0;
    while (index < 4 && val16(h + 2 + 2 * index) != y)
      index++;
    if (index == 4)
      continue;
    u32 code = h[0] ? saved_code(m, h[1], state, unigram) : 0;
    const u8 *t = h + 10;
    double mass = 0., adjusted = 0., weighted_y = 0.;
    double x = h[0] == 2 ? log(source_odds(code)) : 0.;
    for (u32 j = 0; j < 4; j++) {
      u32 id = val16(h + 2 + 2 * j);
      double p = j == index ? observed
                            : pooled_probability(base, q, id, unigram, outgoing,
                                                 offset, succ, freq);
      double odds = 1.;
      if (j < 3) {
        if (h[0] == 2)
          odds = exp(signed_fixed(t + 2 * j) + x * signed_fixed(t + 6 + 2 * j));
        else
          odds = val16(t + 6 * code + 2 * j) / 1024.0;
      }
      mass += p;
      adjusted += p * odds;
      if (j == index)
        weighted_y = p * odds;
    }
    double conditional = weighted_y / adjusted;
    const u8 *r = raw_row(m, g, state, q);
    if (r) {
      u32 total = val16(r) + val16(r + 2) + val16(r + 4) + val16(r + 6);
      conditional = (val16(r + 2 * index) + m->tau * conditional) /
                    (total + (double)m->tau);
    }
    prob = mass * conditional;
    break;
  }
  if (m->source != 65535) {
    double rho = source_odds(saved_code(m, m->source_map, state, unigram));
    if (rho != 1.) {
      double ref = y == m->source
                       ? observed
                       : pooled_probability(base, q, m->source, unigram,
                                            outgoing, offset, succ, freq);
      prob *= (y == m->source ? rho : 1.) / (1. + (rho - 1.) * ref);
    }
  }
  return -log(prob);
}

#ifdef __CUDACC__
extern "C" __global__ void shared_batch(const u16 *tokens, u32 n,
                                        const u32 *unigram, const u32 *outgoing,
                                        const u32 *offset, const u16 *succ,
                                        const u32 *freq, u32 denominator,
                                        const u8 *base, u32 kind, double *out) {
  (void)denominator;
  (void)kind;
  u32 i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i >= n)
    return;
  SharedModel m = parse_shared(base);
  u32 state = save_shared(&m, tokens[i], unigram);
  out[i] = shared_loss(base, &m, state, tokens[i + 1], tokens[i + 2], unigram,
                       outgoing, offset, succ, freq);
}
#else
API void shared_stream(const u16 *tokens, u32 n, const u32 *unigram,
                       const u32 *outgoing, const u32 *offset, const u16 *succ,
                       const u32 *freq, u32 denominator, const u8 *base,
                       u32 kind, double *out) {
  (void)denominator;
  (void)kind;
  SharedModel m = parse_shared(base);
  u32 state = save_shared(&m, tokens[0], unigram), q = tokens[1];
  for (u32 i = 0; i < n; i++) {
    u32 y = tokens[i + 2];
    out[i] = shared_loss(base, &m, state, q, y, unigram, outgoing, offset, succ,
                         freq);
    state = save_shared(&m, q, unigram);
    q = y;
  }
}
#endif
