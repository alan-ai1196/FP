/* Packed online successors for the delayed-state experiment. The caller owns the
   ring. Only this ring, the current input and fixed parameters cross updates. */
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#ifdef _WIN32
#include <intrin.h>
#define EXPORT __declspec(dllexport)
#define POP(x) ((unsigned)__popcnt64(x))
#else
#define EXPORT __attribute__((visibility("default")))
#define POP(x) ((unsigned)__builtin_popcountll(x))
#endif

EXPORT uint64_t raw_errors(const uint8_t *input, size_t count, uint32_t lag,
                           uint8_t *ring) {
    uint64_t errors = 0;
    size_t pos = 0;
    if (!(lag & 7) && !(count & 7)) {
        memcpy(ring, input, lag / 8);
        for (size_t i = lag / 8; i < count / 8; ++i) {
            unsigned prediction = ring[pos];
            unsigned token = input[i];
            errors += POP(prediction ^ token);
            ring[pos] = (uint8_t)token;
            if (++pos == lag / 8) pos = 0;
        }
        return errors;
    }
    for (size_t i = 0; i < count; ++i) {
        unsigned mask = 1u << (pos & 7);
        unsigned prediction = (ring[pos / 8] & mask) != 0;
        unsigned token = (input[i / 8] >> (i & 7)) & 1;
        if (i >= lag) errors += prediction != token;
        ring[pos / 8] = (uint8_t)((ring[pos / 8] & ~mask) | (token ? mask : 0));
        if (++pos == lag) pos = 0;
    }
    return errors;
}

#ifndef FP_RAW_ONLY
static uint64_t low(unsigned n) { return (UINT64_C(1) << n) - 1; }

static uint64_t read_bits(const uint8_t *data, size_t pos, unsigned n) {
    uint64_t word = 0;
    unsigned done = 0;
    while (done < n) {
        unsigned shift = (unsigned)(pos & 7);
        unsigned take = 8 - shift < n - done ? 8 - shift : n - done;
        word |= (((uint64_t)data[pos / 8] >> shift) & low(take)) << done;
        done += take;
        pos += take;
    }
    return word;
}

static void write_bits(uint8_t *data, size_t pos, unsigned n, uint64_t word) {
    while (n) {
        unsigned shift = (unsigned)(pos & 7);
        unsigned take = 8 - shift < n ? 8 - shift : n;
        unsigned mask = (unsigned)low(take);
        data[pos / 8] = (uint8_t)((data[pos / 8] & ~(mask << shift)) |
                                  (((unsigned)word & mask) << shift));
        word >>= take;
        n -= take;
        pos += take;
    }
}

static unsigned syndrome(uint64_t word, const uint64_t masks[6]) {
    unsigned s = 0;
    for (unsigned i = 0; i < 6; ++i)
        s |= (POP(word & masks[i]) & 1u) << i;
    return s;
}

#ifdef FP_MATRIX
static uint64_t encode_matrix(uint64_t word, const uint64_t masks[6],
                              const uint8_t *columns, const uint8_t *parent) {
    unsigned s = syndrome(word, masks);
    while (s) {
        unsigned coordinate = parent[s];
        word ^= UINT64_C(1) << coordinate;
        s ^= columns[coordinate];
    }
    return word >> 6;
}

static uint64_t decode(uint64_t code, const uint64_t masks[6]) {
    uint64_t data = code << 6;
    return data | syndrome(data, masks);
}

EXPORT uint64_t matrix_errors(const uint8_t *input, size_t count, uint32_t lag,
                              uint8_t *ring, const uint8_t *columns, const uint8_t *parent) {
    uint64_t masks[6] = {0};
    for (unsigned p = 0; p < 63; ++p)
        for (unsigned i = 0; i < 6; ++i)
            if ((columns[p] >> i) & 1) masks[i] |= UINT64_C(1) << p;
#define ENCODE_WORD(w) encode_matrix(w, masks, columns, parent)
#else
static uint64_t encode(uint64_t word, const uint64_t masks[6]) {
    unsigned error = syndrome(word, masks);
    if (error) word ^= UINT64_C(1) << (error - 1);
    uint64_t out = 0;
    unsigned index = 0;
    for (unsigned p = 1; p <= 32; p *= 2) {
        out |= ((word >> p) & low(p - 1)) << index;
        index += p - 1;
    }
    return out;
}

static uint64_t decode(uint64_t code, const uint64_t masks[6]) {
    uint64_t word = 0;
    for (unsigned p = 1; p <= 32; p *= 2) {
        word |= (code & low(p - 1)) << p;
        code >>= p - 1;
    }
    unsigned s = syndrome(word, masks);
    for (unsigned i = 0; i < 6; ++i)
        word |= (uint64_t)((s >> i) & 1) << ((1u << i) - 1);
    return word;
}

EXPORT uint64_t coded_errors(const uint8_t *input, size_t count, uint32_t lag,
                             uint8_t *ring) {
    uint64_t masks[6] = {0};
    for (unsigned p = 1; p <= 63; ++p)
        for (unsigned i = 0; i < 6; ++i)
            if ((p >> i) & 1) masks[i] |= UINT64_C(1) << (p - 1);
#define ENCODE_WORD(w) encode(w, masks)
#endif
    uint64_t errors = 0;
    size_t slot = 0, age = 0, pos = 0;
    while (pos < count) {
        unsigned width = lag - age < 63 ? (unsigned)(lag - age) : 63;
        unsigned stored = width == 63 ? 57 : width;
        unsigned observed = count - pos < width ? (unsigned)(count - pos) : width;
        uint64_t old = read_bits(ring, slot, stored);
        uint64_t prediction = width == 63 ? decode(old, masks) : old;
        uint64_t input_word = read_bits(input, pos, observed);
        if (pos >= lag) errors += POP((prediction ^ input_word) & low(observed));
        if (observed == width)
            write_bits(ring, slot, stored, width == 63 ? ENCODE_WORD(input_word) : input_word);
        pos += observed;
        age += observed;
        slot += stored;
        if (age == lag) { age = 0; slot = 0; }
    }
    return errors;
}
#endif
