/* A row contains m noisy reads of each input coordinate followed by one target bit.
   Packet = dimension, reads per input, presence flag, little-endian mask and offset. */
#include <stdint.h>
#if defined(_WIN32)
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif

#define Q31 UINT32_C(2147483648)
typedef struct {
    uint32_t magnitude;
    uint8_t position, seen, ones, negative;
} Carry;

static uint8_t flag(const uint8_t *packet, unsigned int i) {
    return (uint8_t)((packet[3 + i / 8] >> (i % 8)) & 1);
}

static void reset(const uint8_t *packet, Carry *s) {
    s->magnitude = packet[2] ? Q31 : 0;
    s->position = s->seen = s->ones = 0;
    s->negative = packet[2] ? flag(packet, (unsigned int)packet[0] - 1) : 0;
}

API void affine_reset(const uint8_t *packet, uint32_t streams, Carry *state) {
    for (uint32_t j = 0; j < streams; ++j) reset(packet, &state[j]);
}

API uint32_t affine_carry_size(void) { return (uint32_t)sizeof(Carry); }

static double probability(uint32_t magnitude, uint8_t negative) {
    double signed_bias = negative ? -(double)magnitude : (double)magnitude;
    return 0.5 - signed_bias / (4.0 * Q31);
}

API void affine_stream(const uint8_t *packet, const uint32_t *bias, uint32_t steps,
                       uint32_t streams, const uint8_t *bits, Carry *state,
                       double *out) {
    for (uint32_t t = 0; t < steps; ++t) {
        for (uint32_t j = 0; j < streams; ++j) {
            Carry *s = &state[j];
            uint32_t idx = t * streams + j;
            if (s->position == packet[0] - 1) {
                out[idx] = probability(s->magnitude, s->negative);
                reset(packet, s);
                continue;
            }
            int margin = (int)s->seen - 2 * (int)s->ones;
            out[idx] = probability(bias[margin < 0 ? -margin : margin], (uint8_t)(margin < 0));
            s->ones = (uint8_t)(s->ones + bits[idx]);
            if (++s->seen == packet[1]) {
                if (packet[2] && flag(packet, s->position)) {
                    int net = (int)s->seen - 2 * (int)s->ones;
                    uint64_t weight = bias[net < 0 ? -net : net];
                    s->negative ^= (uint8_t)(net < 0);
                    s->magnitude = (uint32_t)(((uint64_t)s->magnitude * weight + Q31 / 2) / Q31);
                }
                ++s->position;
                s->seen = s->ones = 0;
            }
        }
    }
}
