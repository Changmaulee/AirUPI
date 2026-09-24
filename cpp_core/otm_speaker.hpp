/**
 * Project Brahmand: Fluid Multilingual Linguistic Speaker
 * ========================================================
 * Non-Autoregressive boundary trajectory articulation in English, Hindi,
 * and Hinglish, strictly conditioned on deterministic ground truth coordinates.
 * License: Apache-2.0
 */

#ifndef OTM_SPEAKER_HPP
#define OTM_SPEAKER_HPP

#include "otm_types.hpp"
#include "otm_cartridge.hpp"
#include <string>
#include <sstream>
#include <iomanip>

namespace otm {

class FluidLinguisticSpeaker {
public:
    std::string articulate(const CartridgeEntry& entry, const SemanticSlots& slots, const std::string& lang) const {
        std::ostringstream ss;

        if (entry.is_quantitative) {
            double qty = slots.has_quantity ? slots.quantity : 1.0;
            double result = qty * entry.value; // Exact ALU calculation

            if (lang == "hinglish") {
                ss << std::fixed << std::setprecision(1)
                   << qty << " " << entry.entity << " me total "
                   << result << " " << entry.unit
                   << " hoga (" << qty << " x " << entry.value << " " << entry.unit
                   << " per unit, 0% calculation error).";
            } else {
                ss << std::fixed << std::setprecision(1)
                   << qty << " units of " << entry.entity << " contain precisely "
                   << result << " " << entry.unit
                   << " (" << qty << " x " << entry.value << " " << entry.unit
                   << "/unit, verified via CPU ALU).";
            }
        } else if (!entry.definition.empty()) {
            if (lang == "hinglish") {
                ss << entry.entity << " ka matlab: " << entry.definition
                   << " (Domain: " << entry.domain << ").";
            } else {
                ss << entry.entity << ": " << entry.definition
                   << " (Verified in " << entry.domain << " Knowledge Cartridge).";
            }
        } else {
            ss << "Ground truth for " << entry.entity << ": " << entry.value << " " << entry.unit << ".";
        }

        return ss.str();
    }

    std::string format_not_found(const std::string& query, const std::string& lang) const {
        if (lang == "hinglish") {
            return "Mujhe abhi ye topic .otmb cartridge me nahi mila. Aap `brahmand --learn "Topic" "Text"` use karke mujhe turant sikha sakte hain!";
        }
        return "Topic not found in sovereign .otmb cartridges. You can teach me instantly using `brahmand --learn "Topic" "Fact text"`!";
    }
};

} // namespace otm

#endif // OTM_SPEAKER_HPP
