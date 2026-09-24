/**
 * Project Brahmand: 24-D Spatio-Temporal Manifold Embeddings (M^24)
 * ===============================================================
 * Deterministic geometric coordinate grounding across 4 orthogonal subspaces:
 *   - Subspace 0 (0..5):   Structural Subspace
 *   - Subspace 1 (6..11):  Causal-Temporal Subspace (t <= t_playhead)
 *   - Subspace 2 (12..17): Quantitative Subspace
 *   - Subspace 3 (18..23): Action Subspace
 * License: Apache-2.0
 */

#ifndef OTM_MANIFOLD_HPP
#define OTM_MANIFOLD_HPP

#include "otm_types.hpp"
#include <vector>
#include <cmath>
#include <string>

namespace otm {

class SpatioTemporalManifold {
public:
    int manifold_dim;
    
    SpatioTemporalManifold(int dim = MANIFOLD_DIM) : manifold_dim(dim) {}

    // Embed token / entity into 24-D coordinate space deterministically
    std::vector<float> embed(uint32_t token_id, int seq_pos, float timestamp = 0.0f) const {
        std::vector<float> vec(manifold_dim, 0.0f);
        
        // Subspace 0: Structural identity hash
        for (int i = 0; i < SUBSPACE_DIM; ++i) {
            float phase = ((token_id * 17 + i * 31) % 1000) / 1000.0f;
            vec[i] = std::sin(phase * 3.14159265f);
        }
        
        // Subspace 1: Causal-Temporal Order & Playhead Lineage
        for (int i = 0; i < SUBSPACE_DIM; ++i) {
            float t_val = (float)(seq_pos + 1) * 0.1f + timestamp * 0.01f;
            vec[SUBSPACE_DIM + i] = (i % 2 == 0) ? std::cos(t_val) : std::sin(t_val);
        }
        
        // Subspace 2: Quantitative scale (default zero-centered)
        for (int i = 0; i < SUBSPACE_DIM; ++i) {
            vec[2 * SUBSPACE_DIM + i] = 0.0f;
        }
        
        // Subspace 3: Action & Modality
        for (int i = 0; i < SUBSPACE_DIM; ++i) {
            vec[3 * SUBSPACE_DIM + i] = ((token_id % 7) == 0) ? 1.0f : -1.0f;
        }
        
        return vec;
    }

    // Expand 24-D manifold vector to hidden dimension via PO2 bitshift projections
    void project_to_hidden(const std::vector<float>& m_vec, std::vector<float>& hidden_vec, int hidden_dim) const {
        hidden_vec.resize(hidden_dim, 0.0f);
        for (int h = 0; h < hidden_dim; ++h) {
            float val = 0.0f;
            for (int m = 0; m < manifold_dim; ++m) {
                int pattern = (h * manifold_dim + m) % 6;
                switch (pattern) {
                    case 0: val += m_vec[m]; break;
                    case 1: val -= m_vec[m]; break;
                    case 2: val += m_vec[m] * 0.5f; break;
                    case 3: val -= m_vec[m] * 0.5f; break;
                    case 4: val += m_vec[m] * 2.0f; break;
                    case 5: val -= m_vec[m] * 2.0f; break;
                }
            }
            hidden_vec[h] = val;
        }
    }
};

} // namespace otm

#endif // OTM_MANIFOLD_HPP
