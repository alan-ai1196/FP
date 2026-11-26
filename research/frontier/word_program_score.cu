#include <cuda_fp16.h>

template <class Key>
__device__ unsigned lower_index(const Key* keys, unsigned lo, unsigned hi, Key name) {
    while (lo < hi) {
        unsigned mid = lo + (hi - lo) / 2;
        if (keys[mid] < name) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

__device__ float discounted_count(const unsigned* ptr, const unsigned short* ids,
                                  const unsigned short* counts, unsigned row, unsigned short y) {
    unsigned hi = ptr[row + 1];
    unsigned at = lower_index(ids, ptr[row], hi, y);
    return (at < hi && ids[at] == y) ? (float)counts[at] - 0.9f : 0.0f;
}

template <bool mixed>
__device__ __forceinline__ float read_cell(const void* cells, unsigned at) {
    if (mixed) return __half2float(((const __half*)cells)[at]);
    return ((const float*)cells)[at];
}

__device__ unsigned compact_rank(const unsigned char* packet, unsigned short id) {
    const unsigned short* sorted = ((const unsigned short*)packet) + 64;
    unsigned pos = lower_index(sorted, 0u, 64u, id);
    return pos < 64 && sorted[pos] == id ? packet[256 + pos] : 64u;
}

__device__ float point_probability(unsigned short b, unsigned short y, bool seen, unsigned high,
    const unsigned* high_ptr, const unsigned short* high_y, const unsigned short* high_count,
    const float2* high_weights, const unsigned* low_ptr, const unsigned short* low_y,
    const unsigned short* low_count, const float2* low_weights, const float2* lexical) {
    float2 lex = lexical[y], low = low_weights[b];
    float prob = fmaf(low.x, discounted_count(low_ptr, low_y, low_count, b, y), low.y * lex.x);
    if (seen) {
        float2 weights = high_weights[high];
        prob = fmaf(weights.x, discounted_count(high_ptr, high_y, high_count, high, y), weights.y * prob);
    }
    return fmaf(0.9375f, prob, 0.0625f * lex.y);
}

__device__ __forceinline__ unsigned field(const unsigned char* p, unsigned off, unsigned size) {
    unsigned at = off >> 3, shift = off & 7u, word = p[at];
    if (shift + size > 8) word |= (unsigned)p[at + 1] << 8;
    if (shift + size > 16) word |= (unsigned)p[at + 2] << 16;
    return (word >> shift) & ((1u << size) - 1u);
}

__device__ __forceinline__ int coefficient(const unsigned char* p, unsigned at) {
    int v = (int)field(p,at,14);
    return v >= 8192 ? v - 16384 : v;
}

__device__ __forceinline__ int member(const unsigned char* p, unsigned off, unsigned index, unsigned size) {
    return index < size && field(p,off+index,1) ? -1 : 1;
}

__device__ __forceinline__ int op_value(unsigned op, int a, int b) {
    return op == 0 ? 1 : (op == 1 ? a : (op == 2 ? b : a*b));
}

// The layout admits two growth atoms, one new 16-name table, two 12-sign
// heads, and one reader at each child. All learned fields live in the packet.
__device__ __forceinline__ float3 packet_logits(const unsigned char* p, int a, int b, unsigned j) {
    unsigned root = min(j,12u);
    int x = root < 12 ? coefficient(p,7+14*root) : 0;
    x += a * coefficient(p,240) * member(p,254,root,12);
    #pragma unroll
    for (unsigned at = 326; at < 374; at += 24) {
        unsigned ref = field(p,at+20,4);
        unsigned head = ref == 0 ? 254 : 302+12*(ref-1);
        x += op_value(field(p,at,2),a,b) * coefficient(p,at+2) * member(p,head,root,12);
    }
    int child = j>=12 ? op_value(field(p,381,2),a,b)*coefficient(p,383)*member(p,397,min(j-12,12u),12) : 0;
    int deep = j>=24 ? op_value(field(p,416,2),a,b)*coefficient(p,418)*member(p,432,min(j-24,12u),12) : 0;
    return make_float3(x/4096.f,child/4096.f,deep/4096.f);
}

#define ARGUMENTS const unsigned short* raw, unsigned n, unsigned fixed, unsigned high_rows, \
    const unsigned* contexts, const unsigned* high_ptr, const unsigned short* high_y, \
    const unsigned short* high_count, const float2* high_weights, const unsigned* low_ptr, \
    const unsigned short* low_y, const unsigned short* low_count, const float2* low_weights, \
    const float2* lexical, const unsigned char* ranks, const unsigned char* first_bit, \
    const unsigned char* second_bit, const float* shifts, const float* factors, \
    const void* cells, float* nll

template <int mode, bool mixed>
__device__ void evaluate(ARGUMENTS) {
    unsigned t = blockDim.x * blockIdx.x + threadIdx.x;
    if (t >= n) return;
    unsigned pos = fixed ? 0 : t;
    unsigned short a = raw[pos], b = raw[pos + 1], y = fixed ? (unsigned short)t : raw[t + 2];
    unsigned history = (unsigned)a * 50257u + b;
    unsigned high = lower_index(contexts, 0, high_rows, history);
    bool seen = high < high_rows && contexts[high] == history;
    float prob = point_probability(b,y,seen,high,high_ptr,high_y,high_count,high_weights,
                                   low_ptr,low_y,low_count,low_weights,lexical);
    float loss = -logf(prob);
    if (mode == 6) {
        const unsigned short* names = (const unsigned short*)cells;
        const unsigned char* p = (const unsigned char*)cells + 128;
        unsigned ia=64, ib=64, iy=36;
        for (unsigned k=0; k<64; ++k) {
            unsigned short id=names[k];
            if (id==a) ia=k;
            if (id==b) ib=k;
            if (id==y) iy=min(36u,k);
        }
        int first=member(p,175,ib,65), second=member(p,286,min(16u,ia),16);
        float3 observed=packet_logits(p,first,second,iy);
        float3 tail=packet_logits(p,first,second,36);
        float f0=expf(tail.x), f1=expf(tail.y), f2=expf(tail.z);
        float root=f0, m1=1.f, d1=f1, m2=1.f, d2=f2;
        for (unsigned k=0; k<36; ++k) {
            float q=point_probability(b,names[k],seen,high,high_ptr,high_y,high_count,high_weights,
                                      low_ptr,low_y,low_count,low_weights,lexical);
            float3 delta=packet_logits(p,first,second,k);
            root=fmaf(q,expf(delta.x)-f0,root);
            if (iy>=12) {
                if (k<12) m1-=q;
                d1=fmaf(q,(k>=12 ? expf(delta.y) : 0.f)-f1,d1);
            }
            if (iy>=24) {
                if (k<24) m2-=q;
                d2=fmaf(q,(k>=24 ? expf(delta.z) : 0.f)-f2,d2);
            }
        }
        loss += logf(root)-observed.x;
        if (iy>=12) loss += logf(d1/m1)-observed.y;
        if (iy>=24) loss += logf(d2/m2)-observed.z;
        nll[t]=loss;
        return;
    }
    if (mode) {
        unsigned older = second_bit[min(16u, mode == 5 ? compact_rank(ranks,a) : (unsigned)ranks[a])];
        unsigned state = 2u * first_bit[mode == 5 ? compact_rank(ranks,b) : ranks[b]] + older;
        unsigned j = min(36u, mode == 5 ? compact_rank(ranks,y) : (unsigned)ranks[y]);
        unsigned level = (j >= 12) + (j >= 24);
        unsigned row = seen ? high : high_rows + (unsigned)b;
        float normalizer;
        if (mode == 1) {
            const float* weight = factors + state * 111u;
            float mass = 0.f, root = 0.f, m1 = 0.f, d1 = 0.f, m2 = 0.f, d2 = 0.f;
            #pragma unroll
            for (unsigned k = 0; k < 37; ++k) {
                float q = read_cell<mixed>(cells, row * 37u + k);
                mass += q;
                root = fmaf(q, weight[k], root);
                if (k >= 12 && level >= 1) {
                    m1 += q;
                    d1 = fmaf(q, weight[37 + k], d1);
                }
                if (k >= 24 && level == 2) {
                    m2 += q;
                    d2 = fmaf(q, weight[74 + k], d2);
                }
            }
            normalizer = logf(root / mass);
            if (level >= 1) normalizer += logf(d1 / m1);
            if (level == 2) normalizer += logf(d2 / m2);
        } else if (mode == 5) {
            const unsigned short* ids = (const unsigned short*)ranks;
            const float* w = factors + state * 111u;
            float root = w[36], m1 = 1.f, d1 = w[73], m2 = 1.f, d2 = w[110];
            for (unsigned k = 0; k < 36; ++k) {
                float q = point_probability(b,ids[k],seen,high,high_ptr,high_y,high_count,high_weights,
                                             low_ptr,low_y,low_count,low_weights,lexical);
                root = fmaf(q,w[k]-w[36],root);
                if (level >= 1) {
                    if (k < 12) m1 -= q;
                    d1 = fmaf(q,(k >= 12 ? w[37+k] : 0.f)-w[73],d1);
                }
                if (level == 2) {
                    if (k < 24) m2 -= q;
                    d2 = fmaf(q,(k >= 24 ? w[74+k] : 0.f)-w[110],d2);
                }
            }
            normalizer = logf(root);
            if (level >= 1) normalizer += logf(d1/m1);
            if (level == 2) normalizer += logf(d2/m2);
        } else {
            unsigned address = mode == 2 ? 4u * row + state :
                (seen ? high : high_rows + 2u * (unsigned)b + older);
            if (mode == 4) {
                const float2 scale = ((const float2*)factors)[state * 3u + level];
                normalizer = fmaf((float)((const unsigned short*)cells)[address * 3u + level], scale.y, scale.x);
            } else normalizer = read_cell<mixed>(cells, address * 3u + level);
        }
        loss += normalizer - shifts[state * 37u + j];
    }
    nll[t] = loss;
}

#define KERNEL(name, mode, mixed) extern "C" __global__ void name(ARGUMENTS) { \
    evaluate<mode,mixed>(raw,n,fixed,high_rows,contexts,high_ptr,high_y,high_count,high_weights, \
        low_ptr,low_y,low_count,low_weights,lexical,ranks,first_bit,second_bit,shifts,factors,cells,nll); \
}
KERNEL(base_score, 0, false)
KERNEL(group_fp32, 1, false)
KERNEL(group_mixed, 1, true)
KERNEL(all_states_fp32, 2, false)
KERNEL(all_states_mixed, 2, true)
KERNEL(reachable_fp32, 3, false)
KERNEL(reachable_mixed, 3, true)
KERNEL(reachable_u16, 4, false)
KERNEL(on_demand, 5, false)
KERNEL(packed_program, 6, false)
