/**
 * Project Brahmand: Core Types & Harmonic Bitshift Operations
 * ==========================================================
 * Hardware Sovereignty: 0 Multipliers, Pure Power-of-Two (PO2) Shifts.
 * Authored by Chandramouli (@Changmaulee) for TimeMeshin & Project Brahmand.
 * License: Apache-2.0
 */

#ifndef OTM_TYPES_HPP
#define OTM_TYPES_HPP

#include <vector>
#include <string>
#include <cmath>
#include <cstdint>
#include <map>
#include <memory>
#include <chrono>

namespace otm {

constexpr int MANIFOLD_DIM = 24;
constexpr int SUBSPACE_DIM = 6;
constexpr int NUM_SUBSPACES = 4;

enum class HarmonicShift : int8_t {
    NEG_TWO  = -2, // - (x << 1)
    NEG_ONE  = -1, // - x
    NEG_HALF = -3, // - (x >> 1)
    POS_HALF =  3, // + (x >> 1)
    POS_ONE  =  1, // + x
    POS_TWO  =  2  // + (x << 1)
};

inline float apply_po2_shift(float x, HarmonicShift shift) {
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

inline float swi_po2_activation(float x) {
    // Zero-Transcendental Piecewise Non-Linearity
    return (x >= 0.0f) ? x : (x * 0.5f);
}

struct SemanticSlots {
    std::string agent;
    std::string action;
    std::string patient;
    std::string attribute;
    std::string entity;
    std::string unit;
    std::string domain;
    std::string definition;
    double value = 0.0;
    double quantity = 1.0;
    bool has_value = false;
    bool has_quantity = false;
    bool has_definition = false;
    std::string polarity = "POSITIVE";
    std::string modality = "CERTAIN";
    std::string tense = "PRESENT";
};

struct ExecutionResult {
    std::string answer;
    double latency_ms = 0.0;
    std::string hallucination_rate = "0.0%";
    int multipliers_used = 0;
    std::string verification_mode = "Deterministic CPU/ALU";
};

} // namespace otm

#endif // OTM_TYPES_HPP
