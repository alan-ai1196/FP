/* One packed model, shared byte layout and FP64 observed-token score on CPU and
 * GPU. */
#ifdef __CUDACC__
#define FN static __device__ __forceinline__
#else
#include <math.h>
#define FN static inline
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif
#endif
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

FN u32 val16(const u8 *p) { return (u32)p[0] | ((u32)p[1] << 8); }
FN u32 val24(const u8 *p) { return val16(p) | ((u32)p[2] << 16); }
FN u32 val32(const u8 *p) { return val24(p) | ((u32)p[3] << 24); }

FN u32 lower_id(const u8 *p, u32 n, u32 stride, u32 token) {
  u32 lo = 0, hi = n;
  while (lo < hi) {
    u32 mid = lo + (hi - lo) / 2;
    if (val16(p + mid * stride) < token)
      lo = mid + 1;
    else
      hi = mid;
  }
  return lo;
}

FN u32 address(const u8 *p, const u32 *unigram, u32 token) {
  u32 mode = p[2];
  if (!mode)
    return 0;
  const u8 *table = p + 24 + 8 * val16(p);
  if (mode == 2)
    return (table[token / 8] >> (token % 8)) & 1u;
  u32 n = val16(p + 4);
  u32 stride = mode == 3 ? 3 : 2;
  u32 index = lower_id(table, n, stride, token);
  u32 changed = index < n && val16(table + stride * index) == token;
  u32 bit = p[3];
  if (mode == 3 && changed)
    return table[stride * index + 2];
  if ((mode == 3 && bit == 5) || (mode != 3 && bit == 2)) {
    u32 cutoff = val32(p + 8);
    bit = (unigram[token] > cutoff ||
           (unigram[token] == cutoff && token <= val16(p + 6)));
    if (mode == 3)
      bit *= 4;
  }
  return bit ^ changed;
}

FN u32 base_count(u32 q, u32 y, const u32 *offset, const u16 *successor,
                  const u32 *freq) {
  u32 lo = offset[q], end = offset[q + 1], hi = end;
  while (lo < hi) {
    u32 mid = lo + (hi - lo) / 2;
    if ((u32)successor[mid] < y)
      lo = mid + 1;
    else
      hi = mid;
  }
  return lo < end && successor[lo] == y ? freq[lo] : 0;
}

FN double backoff(const u8 *p, u32 state, u32 y, const u32 *unigram) {
  u32 n = val16(p), stride = p[2] ? 8u : 5u;
  const u8 *table = p + 24;
  u32 i = lower_id(table, n, stride, y);
  if (i < n && val16(table + i * stride) == y) {
    const u8 *mass = table + i * stride + 2;
    if (p[2] != 3)
      return val24(mass + 3 * state) / 16777216.0;
    return ((4 - state) * val24(mass) + state * val24(mass + 3)) / 67108864.0;
  }
  double bucket =
      p[2] == 3
          ? ((4 - state) * val32(p + 16) + state * val32(p + 20)) / 67108864.0
          : val32(p + 16 + 4 * state) / 16777216.0;
  return bucket * ((unigram[y] + 1.0) / val32(p + 12));
}

FN double higher_order(const u8 *p, u32 older, u32 q, u32 y, double base) {
  u32 n = val32(p), target = (older << 16) | q;
  const u8 *index = p + 9, *entries = index + 12 * n;
  u32 lo = 0, hi = n;
  while (lo < hi) {
    u32 mid = lo + (hi - lo) / 2;
    const u8 *row = index + 12 * mid;
    u32 key = (val16(row) << 16) | val16(row + 2);
    if (key < target)
      lo = mid + 1;
    else
      hi = mid;
  }
  if (lo == n)
    return base;
  const u8 *row = index + 12 * lo;
  if (val16(row) != older || val16(row + 2) != q)
    return base;
  u32 start = val32(row + 4);
  u32 limit = lo + 1 < n ? val32(row + 16) : val32(p + 4);
  u32 item = start + lower_id(entries + 6 * start, limit - start, 6, y);
  u32 count = item < limit && val16(entries + 6 * item) == y
                  ? val32(entries + 6 * item + 2)
                  : 0;
  return (count + p[8] * base) / (val32(row + 8) + (double)p[8]);
}

FN double score_one(u32 kind, const u8 *model, u32 state, u32 query, u32 target,
                    const u32 *unigram, const u32 *outgoing, const u32 *offset,
                    const u16 *successor, const u32 *freq, u32 denominator) {
  u32 observed = base_count(query, target, offset, successor, freq);
  double prior = kind == 1 || kind == 3
                     ? backoff(model, kind == 1 ? state : 0, target, unigram)
                     : (unigram[target] + 1.0) / denominator;
  double prob = (observed + 64.0 * prior) / (outgoing[query] + 64.0);
  if (kind == 2)
    prob = higher_order(model, state, query, target, prob);
  if (kind == 3)
    prob =
        higher_order(model + 24 + 5 * val16(model), state, query, target, prob);
  return -log(prob);
}

#ifdef __CUDACC__
extern "C" __global__ void score_batch(const u16 *tokens, u32 n,
                                       const u32 *unigram, const u32 *outgoing,
                                       const u32 *offset, const u16 *successor,
                                       const u32 *freq, u32 denominator,
                                       const u8 *model, u32 kind, double *out) {
  u32 i = blockDim.x * blockIdx.x + threadIdx.x;
  if (i >= n)
    return;
  u32 old = tokens[i];
  u32 state = kind == 1 ? address(model, unigram, old) : old;
  out[i] = score_one(kind, model, state, tokens[i + 1], tokens[i + 2], unigram,
                     outgoing, offset, successor, freq, denominator);
}
#else
API void score_stream(const u16 *tokens, u32 n, const u32 *unigram,
                      const u32 *outgoing, const u32 *offset,
                      const u16 *successor, const u32 *freq, u32 denominator,
                      const u8 *model, u32 kind, double *out) {
  u32 state = kind == 1 ? address(model, unigram, tokens[0]) : tokens[0];
  u32 query = tokens[1];
  for (u32 i = 0; i < n; ++i) {
    u32 target = tokens[i + 2];
    out[i] = score_one(kind, model, state, query, target, unigram, outgoing,
                       offset, successor, freq, denominator);
    state = kind == 1 ? address(model, unigram, query) : query;
    query = target;
  }
}
#endif
