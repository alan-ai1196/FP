/* Full-vocabulary correction with sorted sets and optional paid query masses.
 */
#include "address_score.c"

FN const u8 *class_header(const u8 *model) {
  return model + 24 + 5 * val16(model);
}

FN u32 member(const u8 *types, u32 n, u32 stride, u32 token) {
  u32 i = lower_id(types, n, stride, token);
  return i < n && val16(types + stride * i) == token;
}

FN u32 class_state(u32 kind, const u8 *model, const u32 *count, u32 older) {
  if (kind != 5 && kind != 6)
    return history_state(kind, model, count, older);
  const u8 *h = class_header(model);
  if (h[1] & 1)
    return 1;
  if (h[1] & 2)
    return 0;
  return member(h + 16, val16(h + 2), 2, older);
}

FN double delta(const u8 *ids, u32 i, u32 stride, u32 scalar) {
  return (double)(stride == 2 ? scalar : val16(ids + stride * i + 2)) - 1024.;
}

FN double chosen_delta(const u8 *ids, u32 n, u32 stride, u32 scalar,
                       u32 target) {
  u32 i = lower_id(ids, n, stride, target);
  return i < n && val16(ids + i * stride) == target
             ? delta(ids, i, stride, scalar)
             : 0.;
}

FN double class_loss(u32 kind, const u8 *model, u32 state, u32 q, u32 y,
                     const u32 *uni, const u32 *outgoing, const u32 *offset,
                     const u16 *succ, const u32 *freq, u32 denominator) {
  if (kind != 5 && kind != 6)
    return score_one(kind, model, state, q, y, uni, outgoing, offset, succ,
                     freq, denominator);
  const u8 *h = class_header(model);
  if (h[1] & 2)
    state = member(h + 16, val16(h + 2), 2, q);
  double observation =
      (base_count(q, y, offset, succ, freq) + 64. * backoff(model, 0, y, uni)) /
      (outgoing[q] + 64.);
  if (!state)
    return -log(observation);
  u32 n = val16(h + 4), stride = h[0] == 1 ? 2 : 4, scalar = val16(h + 6);
  const u8 *ids = h + 16 + 2 * val16(h + 2);
  double hi = (double)val32(h + 12);
  if (hi >= 2147483648.)
    hi -= 4294967296.;
  double numerator = val32(h + 8) + 4294967296. * hi;
  double sum = 64. * numerator / (16777216. * val32(model + 12));
  u32 begin = offset[q], end = offset[q + 1];
  u32 found = 0;
  if (kind == 6) {
    const u8 *cache = ids + stride * n;
    u32 count = val16(cache);
    const u8 *entries = cache + 2;
    u32 i = lower_id(entries, count, 6, q);
    if (i < count && val16(entries + 6 * i) == q) {
      double scaled = val32(entries + 6 * i + 2);
      sum += scaled < 2147483648. ? scaled : scaled - 4294967296.;
      found = 1;
    }
  }
  if (!found && end - begin <= n) {
    for (u32 i = begin; i < end; i++)
      sum += freq[i] * chosen_delta(ids, n, stride, scalar, succ[i]);
  } else if (!found) {
    for (u32 i = 0; i < n; i++)
      sum += base_count(q, val16(ids + i * stride), offset, succ, freq) *
             delta(ids, i, stride, scalar);
  }
  double mult = 1024. + chosen_delta(ids, n, stride, scalar, y);
  return -log(observation * mult / (1024. + sum / (outgoing[q] + 64.)));
}

#ifdef __CUDACC__
extern "C" __global__ void class_batch(const u16 *tokens, u32 n, const u32 *uni,
                                       const u32 *outgoing, const u32 *offset,
                                       const u16 *succ, const u32 *freq,
                                       u32 denominator, const u8 *model,
                                       u32 kind, double *out) {
  u32 i = blockDim.x * blockIdx.x + threadIdx.x;
  if (i < n)
    out[i] = class_loss(kind, model, class_state(kind, model, uni, tokens[i]),
                        tokens[i + 1], tokens[i + 2], uni, outgoing, offset,
                        succ, freq, denominator);
}
#else
API void class_stream(const u16 *tokens, u32 n, const u32 *uni,
                      const u32 *outgoing, const u32 *offset, const u16 *succ,
                      const u32 *freq, u32 denominator, const u8 *model,
                      u32 kind, double *out) {
  u32 prior = class_state(kind, model, uni, tokens[0]), q = tokens[1];
  for (u32 i = 0; i < n; i++) {
    u32 y = tokens[i + 2];
    out[i] = class_loss(kind, model, prior, q, y, uni, outgoing, offset, succ,
                        freq, denominator);
    prior = class_state(kind, model, uni, q);
    q = y;
  }
}
#endif
