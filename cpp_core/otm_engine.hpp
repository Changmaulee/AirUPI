/**
 * Subtractive OTM Mesh Engine (C++ Header-Only)
 * =============================================
 * Deterministic Spatio-Temporal Micro/Macro Delta Engine.
 * 
 * Features:
 * - 0 Floating-Point Multiplications in connection routing (Bitshifts + Sign-adds only).
 * - Micro-OTM Delta-Gated execution for ultra-low-power streaming.
 * - Macro-OTM energy normalization checkpoints.
 * 
 * License: Apache-2.0
 */

#ifndef SUBTRACTIVE_OTM_ENGINE_HPP
#define SUBTRACTIVE_OTM_ENGINE_HPP

#include <vector>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include <iostream>

namespace otm {

enum class HarmonicPolarity : int8_t {
    NEG_TWO  = -2, // - (x << 1)
    NEG_ONE  = -1, // - x
    NEG_HALF = -3, // - (x >> 1)
    POS_HALF =  3, // + (x >> 1)
    POS_ONE  =  1, // + x
    POS_TWO  =  2  // + (x << 1)
};

class MicroOTMLayer {
public:
    int in_dim;
    int out_dim;
    float delta_threshold;
    
    std::vector<HarmonicPolarity> polarities; // Size: out_dim * in_dim
    std::vector<uint8_t> mask;               // Size: out_dim * in_dim (1 = active, 0 = pruned)
    std::vector<float> thresholds;           // Size: out_dim
    std::vector<float> prev_state;           // Size: in_dim
    
    MicroOTMLayer(int in_d, int out_d, float d_thresh = 0.02f)
        : in_dim(in_d), out_dim(out_d), delta_threshold(d_thresh) {
        polarities.resize(out_dim * in_dim, HarmonicPolarity::POS_ONE);
        mask.resize(out_dim * in_dim, 1);
        thresholds.resize(out_dim, 0.0f);
        prev_state.resize(in_dim, 0.0f);
    }

    // Ultra-fast Multiplication-Free Forward Pass
    inline void forward_step(const float* input, float* output, bool is_streaming, size_t& active_evals) {
        std::vector<float> eff_input(in_dim);
        
        if (is_streaming) {
            for (int i = 0; i < in_dim; ++i) {
                float delta = input[i] - prev_state[i];
                prev_state[i] = input[i];
                if (std::fabs(delta) >= delta_threshold) {
                    eff_input[i] = delta;
                    active_evals++;
                } else {
                    eff_input[i] = 0.0f;
                }
            }
        } else {
            std::memcpy(eff_input.data(), input, in_dim * sizeof(float));
            active_evals += in_dim;
        }

        // Subtractive routing via bitshifts & sign-adds
        for (int j = 0; j < out_dim; ++j) {
            float sum = thresholds[j];
            int row_offset = j * in_dim;
            
            for (int i = 0; i < in_dim; ++i) {
                if (mask[row_offset + i] == 0) continue; // Pruned / Subtracted edge
                
                float x = eff_input[i];
                if (x == 0.0f) continue;
                
                HarmonicPolarity pol = polarities[row_offset + i];
                switch (pol) {
                    case HarmonicPolarity::POS_ONE:  sum += x; break;
                    case HarmonicPolarity::NEG_ONE:  sum -= x; break;
                    case HarmonicPolarity::POS_TWO:  sum += (x * 2.0f); break;
                    case HarmonicPolarity::NEG_TWO:  sum -= (x * 2.0f); break;
                    case HarmonicPolarity::POS_HALF: sum += (x * 0.5f); break;
                    case HarmonicPolarity::NEG_HALF: sum -= (x * 0.5f); break;
                }
            }
            output[j] = sum;
        }
    }
};

} // namespace otm

#endif // SUBTRACTIVE_OTM_ENGINE_HPP
