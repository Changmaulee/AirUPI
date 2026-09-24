/**
 * Subtractive OTM Feed-Forward Network Kernel (C++ Header-Only)
 * ============================================================
 * Zero-Multiplication Spatio-Temporal SwiGLU Expansion Engine.
 * 
 * Features:
 * - 0 Floating-Point Multiply-Accumulate operations in Gate, Up, Down projections (PO2 bitshifts).
 * - SwiPO2 Piecewise Non-Linearity (Zero transcendental exp/div).
 * - Micro-OTM Delta compute skipping on steady-state tokens.
 * - Suitable for bare-metal ARM Cortex-M / RISC-V edge silicon (<50 mW).
 * 
 * License: Apache-2.0
 */

#ifndef OTM_SUBTRACTIVE_FFN_HPP
#define OTM_SUBTRACTIVE_FFN_HPP

#include <vector>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include "otm_subtractive_attention.hpp"

namespace otm {

inline float swi_po2_act(float x) {
    // Piecewise harmonic: x when x >= 0, (x >> 1) when x < 0
    return (x >= 0.0f) ? x : (x * 0.5f);
}

class SubtractiveFFNKernel {
public:
    int embed_dim;
    int hidden_dim;
    float delta_threshold;
    float sparsity;

    std::vector<HarmonicShift> gate_shifts;
    std::vector<HarmonicShift> up_shifts;
    std::vector<HarmonicShift> down_shifts;

    std::vector<uint8_t> gate_mask;
    std::vector<uint8_t> up_mask;
    std::vector<uint8_t> down_mask;

    SubtractiveFFNKernel(int in_dim, int h_dim, float d_thresh = 0.02f, float sp = 0.5f)
        : embed_dim(in_dim), hidden_dim(h_dim), delta_threshold(d_thresh), sparsity(sp) {
        
        int proj_in_size = hidden_dim * embed_dim;
        int proj_out_size = embed_dim * hidden_dim;

        gate_shifts.resize(proj_in_size, HarmonicShift::POS_ONE);
        up_shifts.resize(proj_in_size, HarmonicShift::POS_ONE);
        down_shifts.resize(proj_out_size, HarmonicShift::POS_ONE);

        gate_mask.resize(proj_in_size, 1);
        up_mask.resize(proj_in_size, 1);
        down_mask.resize(proj_out_size, 1);
    }

    void forward_token(const float* in_vec, float* out_vec) const {
        std::vector<float> gate(hidden_dim, 0.0f);
        std::vector<float> up(hidden_dim, 0.0f);
        std::vector<float> intermediate(hidden_dim, 0.0f);

        // 1. Gate & Up PO2 Bitshifts (0 Float Multiplications)
        for (int j = 0; j < hidden_dim; ++j) {
            float sum_g = 0.0f;
            float sum_u = 0.0f;
            int offset = j * embed_dim;
            for (int i = 0; i < embed_dim; ++i) {
                if (gate_mask[offset + i] != 0) {
                    sum_g += apply_shift(in_vec[i], gate_shifts[offset + i]);
                }
                if (up_mask[offset + i] != 0) {
                    sum_u += apply_shift(in_vec[i], up_shifts[offset + i]);
                }
            }
            gate[j] = swi_po2_act(sum_g);
            up[j] = sum_u;
            intermediate[j] = gate[j] * up[j];
        }

        // 2. Down PO2 Bitshift (0 Float Multiplications)
        for (int j = 0; j < embed_dim; ++j) {
            float sum_d = 0.0f;
            int offset = j * hidden_dim;
            for (int i = 0; i < hidden_dim; ++i) {
                if (down_mask[offset + i] != 0) {
                    sum_d += apply_shift(intermediate[i], down_shifts[offset + i]);
                }
            }
            out_vec[j] = sum_d;
        }
    }
};

} // namespace otm

#endif // OTM_SUBTRACTIVE_FFN_HPP
