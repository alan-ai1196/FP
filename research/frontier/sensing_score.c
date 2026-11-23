/* A new name is read at each causal input stage; only the encoded state is
 * carried forward. */
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif
#include <stdint.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;

static inline u32 bits(const u8 *p, u32 i, u32 width) {
  u32 loc = i * width, shift = loc % 8, value = p[loc / 8];
  if (shift + width > 8)
    value |= (u32)p[loc / 8 + 1] << 8;
  return (value >> shift) & ((1u << width) - 1u);
}

API void sense_batch(const u8 *model, const u8 *row, const u8 *col,
                     const u8 *task, u32 n, u8 *action, u16 *confidence) {
  u32 kind = model[0], states = model[1], tasks = model[2], channels = model[3];
  const u8 *tables = model + 4;
  u32 nbytes = kind == 1   ? 3u
               : kind == 2 ? 8u
               : kind == 4 ? 6u
               : kind == 5 ? 9u
                           : 0u;
  const u8 *policy = tables + nbytes;
  u32 entries = kind == 5 ? states : states * tasks;
  const u8 *prob = policy + (2 * entries + 7) / 8;
  for (u32 i = 0; i < n; i++) {
    u32 first = 0, s = 0;
    if (kind == 1)
      first = bits(tables, row[i], 1);
    else if (kind == 4)
      first = bits(tables, row[i], 3);
    else if (kind == 2 || kind == 3 || kind == 5)
      first = row[i];
    if (kind == 1)
      s = bits(tables + 1, 8 * first + col[i], 1);
    else if (kind == 2)
      s = bits(tables, 8 * first + col[i], 1);
    else if (kind == 3 || kind == 5)
      s = 8 * first + col[i];
    else if (kind == 4)
      s = first ^ bits(tables + 3, col[i], 3);
    u32 j = task[i], key = tasks * s + j;
    if (kind == 5) {
      u32 block = tables[j] + bits(tables + 3, 8 * j + s / 8, 2);
      key = 8 * block + s % 8;
    }
    action[i] = (u8)bits(policy, key, 2);
    for (u32 z = 0; z < channels; z++) {
      u32 offset = 2 * (channels * key + z);
      confidence[channels * i + z] =
          (u16)(prob[offset] | ((u32)prob[offset + 1] << 8));
    }
  }
}
