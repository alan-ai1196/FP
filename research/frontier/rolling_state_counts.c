/* Count the observed sign before updating each candidate's own causal address. */
#include <stddef.h>
#include <stdint.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

EXPORT void state_counts(const uint8_t *models, size_t model_count,
                         const uint8_t *tape, size_t warm, size_t length,
                         uint32_t *out) {
    for (size_t m = 0; m < model_count; ++m) {
        const uint8_t *table = models + 8 * m;
        uint32_t *cells = out + 8 * m;
        uint8_t state = 0;
        for (size_t i = 0; i < warm; ++i) {
            state = table[2 * state + tape[i]];
        }
        for (size_t j = 0; j < length; ++j) {
            unsigned cell = 2u * state + tape[warm + j];
            ++cells[cell];
            state = table[cell];
        }
    }
}
