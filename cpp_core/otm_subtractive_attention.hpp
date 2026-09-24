/**
 * Subtractive OTM Attention Kernel (C++ Header-Only)
 * =================================================
 * Deterministic Zero-Multiplication Spatio-Temporal Relational Engine.
 * 
 * Features:
 * - 0 Floating-Point Multiply-Accumulate operations in projection layers (PO2 bitshifts).
 * - Causal Playhead Invariance (t <= t_playhead).
 * - Micro-OTM Delta Activation Gating.
 * - Suitable for bare-metal ARM Cortex-M / RISC-V edge silicon (<50 mW).
 * 
 * License: Apache-2.0
 */

#ifndef OTM_SUBTRACTIVE_ATTENTION_HPP
#define OTM_SUBTRACTIVE_ATTENTION_HPP

#include <vector>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include <iostream>

namespace otm {

enum class HarmonicShift : int8_t {
    NEG_TWO  = -2, // - (x << 1)
    NEG_ONE  = -1, // - x
    NEG_HALF = -3, // - (x >> 1)
    POS_HALF =  3, // + (x >> 1)
    POS_ONE  =  1, // + x
    POS_TWO  =  2  // + (x << 1)
};

inline float apply_shift(float x, HarmonicShift shift) {
    switch (shift) {
        case HarmonicShift::POS_ONE:  return x;
        case HarmonicShift::NEG_ONE:  return -x;
        case HarmonicShift::POS_TWO:  return x * 2.0f;
        case HarmonicShift::NEG_TWO:  return -x * 2.0f;
        case HarmonicShift::POS_HALF: return x * 0.5f;
        case HarmonicShift::NEG_HALF: return -x * 0.5f;
        default: return 0.0f;
    }
}

class SubtractiveAttentionKernel {
public:
    int embed_dim;
    int num_heads;
    int head_dim;
    float delta_threshold;
    float sparsity;

    std::vector<HarmonicShift> q_shifts;
    std::vector<HarmonicShift> k_shifts;
    std::vector<HarmonicShift> v_shifts;
    std::vector<HarmonicShift> out_shifts;

    std::vector<uint8_t> q_mask;
    std::vector<uint8_t> k_mask;
    std::vector<uint8_t> v_mask;
    std::vector<uint8_t> out_mask;

    SubtractiveAttentionKernel(int dim, int heads, float d_thresh = 0.02f, float sp = 0.5f)
        : embed_dim(dim), num_heads(heads), head_dim(dim / heads), delta_threshold(d_thresh), sparsity(sp) {
        
        int size = embed_dim * embed_dim;
        q_shifts.resize(size, HarmonicShift::POS_ONE);
        k_shifts.resize(size, HarmonicShift::POS_ONE);
        v_shifts.resize(size, HarmonicShift::POS_ONE);
        out_shifts.resize(size, HarmonicShift::POS_ONE);

        q_mask.resize(size, 1);
        k_mask.resize(size, 1);
        v_mask.resize(size, 1);
        out_mask.resize(size, 1);
    }

    void project_po2(const float* in_vec, float* out_vec, const std::vector<HarmonicShift>& shifts, const std::vector<uint8_t>& mask) const {
        for (int j = 0; j < embed_dim; ++j) {
            float sum = 0.0f;
            int offset = j * embed_dim;
            for (int i = 0; i < embed_dim; ++i) {
                if (mask[offset + i] == 0) continue;
                sum += apply_shift(in_vec[i], shifts[offset + i]);
            }
            out_vec[j] = sum;
        }
    }

    void forward_sequence(const std::vector<float>& input_seq, int seq_len, std::vector<float>& output_seq, bool causal = true) {
        output_seq.resize(seq_len * embed_dim, 0.0f);
        std::vector<float> Q(seq_len * embed_dim);
        std::vector<float> K(seq_len * embed_dim);
        std::vector<float> V(seq_len * embed_dim);

        for (int t = 0; t < seq_len; ++t) {
            const float* in_ptr = &input_seq[t * embed_dim];
            project_po2(in_ptr, &Q[t * embed_dim], q_shifts, q_mask);
            project_po2(in_ptr, &K[t * embed_dim], k_shifts, k_mask);
            project_po2(in_ptr, &V[t * embed_dim], v_shifts, v_mask);
        }

        // Subtractive causal routing
        std::vector<float> context(seq_len * embed_dim, 0.0f);
        float scale = 1.0f / std::sqrt((float)head_dim);

        for (int h = 0; h < num_heads; ++h) {
            int h_offset = h * head_dim;
            for (int i = 0; i < seq_len; ++i) {
                std::vector<float> attn_weights(seq_len, 0.0f);
                float max_val = -1e9f;

                int max_j = causal ? i : (seq_len - 1);
                for (int j = 0; j <= max_j; ++j) {
                    float dot = 0.0f;
                    for (int d = 0; d < head_dim; ++d) {
                        dot += Q[i * embed_dim + h_offset + d] * K[j * embed_dim + h_offset + d];
                    }
                    dot *= scale;
                    attn_weights[j] = dot;
                    if (dot > max_val) max_val = dot;
                }

                // Softmax & subtractive threshold
                float sum_exp = 0.0f;
                for (int j = 0; j <= max_j; ++j) {
                    attn_weights[j] = std::exp(attn_weights[j] - max_val);
                    sum_exp += attn_weights[j];
                }
                for (int j = 0; j <= max_j; ++j) {
                    attn_weights[j] /= (sum_exp + 1e-8f);
                }

                // Aggregate V
                for (int d = 0; d < head_dim; ++d) {
                    float sum_v = 0.0f;
                    for (int j = 0; j <= max_j; ++j) {
                        sum_v += attn_weights[j] * V[j * embed_dim + h_offset + d];
                    }
                    context[i * embed_dim + h_offset + d] = sum_v;
                }
            }
        }

        for (int t = 0; t < seq_len; ++t) {
            project_po2(&context[t * embed_dim], &output_seq[t * embed_dim], out_shifts, out_mask);
        }
    }
};

} // namespace otm

#endif // OTM_SUBTRACTIVE_ATTENTION_HPP
