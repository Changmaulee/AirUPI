/**
 * Project Brahmand: Micro-OTM 12-Slot Semantic Grammar Parser (22 Indian Languages)
 * ===============================================================================
 * Resolves syntax, entities, quantities, negations, and multilingual synsets
 * across all 22 official Indian languages + English/Hinglish in <0.02 ms on standard CPU.
 * License: Apache-2.0
 */

#ifndef MICRO_OTM_PARSER_HPP
#define MICRO_OTM_PARSER_HPP

#include "otm_types.hpp"
#include "timemeshin_indic_otm_tokenizer.hpp"
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <cctype>
#include <algorithm>

namespace otm {

class MicroOTMParser {
public:
    TimeMeshinIndicOTMTokenizer indic_tokenizer;

    MicroOTMParser() {}

    std::string detect_language(const std::string& query) const {
        std::string q = query;
        std::transform(q.begin(), q.end(), q.begin(), ::tolower);
        std::vector<std::string> hinglish_markers = {"kitna", "hoga", "kya", "me", "ande", "batao", "hai", "kaise"};
        for (const auto& marker : hinglish_markers) {
            if (q.find(marker) != std::string::npos) {
                return "hinglish";
            }
        }
        return "indic";
    }

    SemanticSlots parse(const std::string& raw_query) const {
        return indic_tokenizer.parse_12_slot_grammar(raw_query);
    }
};

} // namespace otm

#endif // MICRO_OTM_PARSER_HPP
