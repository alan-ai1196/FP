/* Exact normalized class odds with sparse current, earlier, or pair exceptions.
 */
#include "address_score.c"

FN u32 nested_member(const u8 *keys, u32 n, u32 token) {
  u32 i = lower_id(keys, n, 2, token);
  return i < n && val16(keys + 2 * i) == token;
}

FN const u8 *after_table(const u8 *table) {
  u32 n = val16(table + 2), stride = table[0] == 3 ? 4u : 2u;
  return table + 4 + stride * n + (n + 1) / 2;
}

FN u32 exception_code(const u8 *table, u32 key) {
  u32 n = val16(table + 2), stride = table[0] == 3 ? 4u : 2u;
  const u8 *keys = table + 4;
  u32 i;
  if (stride == 2) {
    i = lower_id(keys, n, 2, key);
    if (i == n || val16(keys + 2 * i) != key)
      return table[1];
  } else {
    u32 lo = 0, hi = n;
    while (lo < hi) {
      u32 mid = lo + (hi - lo) / 2;
      if (val32(keys + 4 * mid) < key)
        lo = mid + 1;
      else
        hi = mid;
    }
    i = lo;
    if (i == n || val32(keys + 4 * i) != key)
      return table[1];
  }
  return (keys[stride * n + i / 2] >> (4u * (i % 2))) & 15u;
}

FN double exception_odds(u32 code) {
  if (code <= 4)
    return (1. + code) * .25;
  if (code == 5)
    return 1.5;
  return (double)(code - 4);
}

FN const u8 *profile_packet(const u8 *model) {
  const u8 *h = model + 24 + 5 * val16(model);
  return h + 16 + 2 * val16(h);
}

FN u32 profile_rank(const u8 *ids, u32 token) {
  for (u32 i = 0; i < 8; i++)
    if (val16(ids + 2 * i) == token)
      return i;
  return 8;
}

FN u32 profile_width(u32 k) {
  return (k == 1 || k == 8) ? 0u : k == 2 ? 1u : k <= 4 ? 2u : 3u;
}

FN u32 profile_state(const u8 *p, u32 token) {
  u32 row = profile_rank(p + 3, token), k = p[1];
  if (row == 8 || k == 8)
    return row;
  if (k == 1)
    return 0;
  const u8 *labels = p + 3 + (p[2] ? 16 : 32);
  u32 w = profile_width(k), loc = w * row, shift = loc % 8;
  u32 word = labels[loc / 8];
  if (shift + w > 8)
    word |= (u32)labels[loc / 8 + 1] << 8;
  return (word >> shift) & ((1u << w) - 1u);
}

FN u32 nested_state(u32 kind, const u8 *model, const u32 *uni, u32 token) {
  if (kind == 8)
    return profile_state(profile_packet(model), token);
  if (kind != 7)
    return history_state(kind, model, uni, token);
  const u8 *h = model + 24 + 5 * val16(model);
  if (h[13] == 0)
    return 0;
  if (h[13] == 2)
    return token;
  const u8 *t = h + 16 + 2 * val16(h);
  if (t[0] != 1)
    t = after_table(t);
  return exception_code(t, token);
}

FN double nested_loss(u32 kind, const u8 *model, u32 state, u32 q, u32 y,
                      const u32 *uni, const u32 *outgoing, const u32 *offset,
                      const u16 *succ, const u32 *freq, u32 denominator) {
  if (kind != 7 && kind != 8)
    return score_one(kind, model, state, q, y, uni, outgoing, offset, succ,
                     freq, denominator);
  const u8 *h = model + 24 + 5 * val16(model), *ids = h + 16;
  u32 n = val16(h);
  const u8 *t = ids + 2 * n;
  double r = val16(h + 2) / 1024.;
  for (u32 j = 0; j < h[12]; j++) {
    u32 code = t[0] == 1
                   ? state
                   : exception_code(t, t[0] == 2 ? q : ((state << 16) | q));
    r *= exception_odds(code);
    t = after_table(t);
  }
  double denom = outgoing[q] + 64.;
  double base =
      (base_count(q, y, offset, succ, freq) + 64. * backoff(model, 0, y, uni)) /
      denom;
  if (r == 1. && kind != 8)
    return -log(base);
  double back_mass = (val32(h + 4) + 4294967296. * val32(h + 8)) /
                     (16777216. * val32(model + 12));
  u32 begin = offset[q], end = offset[q + 1], total = 0;
  if (end - begin <= n) {
    for (u32 i = begin; i < end; i++)
      if (nested_member(ids, n, succ[i]))
        total += freq[i];
  } else {
    for (u32 i = 0; i < n; i++)
      total += base_count(q, val16(ids + 2 * i), offset, succ, freq);
  }
  double mass = (total + 64. * back_mass) / denom;
  u32 member = nested_member(ids, n, y);
  if (kind == 8 && state < 8) {
    const u8 *p = profile_packet(model);
    u32 col = profile_rank(p + 3 + (p[2] ? 0 : 16), q);
    if (col < 8) {
      const u8 *rates = p + 3 + (p[2] ? 16 : 32) + profile_width(p[1]);
      double target = val16(rates + 2 * (8 * state + col)) / 65536.;
      return -log(base *
                  (member ? target / mass : (1. - target) / (1. - mass)));
    }
  }
  return -log(base * (member ? r : 1.) / (1. + (r - 1.) * mass));
}

#ifdef __CUDACC__
extern "C" __global__ void
nested_batch(const u16 *tokens, u32 n, const u32 *uni, const u32 *outgoing,
             const u32 *offset, const u16 *succ, const u32 *freq,
             u32 denominator, const u8 *model, u32 kind, double *out) {
  u32 i = blockDim.x * blockIdx.x + threadIdx.x;
  if (i < n)
    out[i] = nested_loss(kind, model, nested_state(kind, model, uni, tokens[i]),
                         tokens[i + 1], tokens[i + 2], uni, outgoing, offset,
                         succ, freq, denominator);
}
#else
API void nested_stream(const u16 *tokens, u32 n, const u32 *uni,
                       const u32 *outgoing, const u32 *offset, const u16 *succ,
                       const u32 *freq, u32 denominator, const u8 *model,
                       u32 kind, double *out) {
  u32 state = nested_state(kind, model, uni, tokens[0]), q = tokens[1];
  for (u32 i = 0; i < n; i++) {
    u32 y = tokens[i + 2];
    out[i] = nested_loss(kind, model, state, q, y, uni, outgoing, offset, succ,
                         freq, denominator);
    state = nested_state(kind, model, uni, q);
    q = y;
  }
}
#endif
