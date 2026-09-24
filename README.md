# Project Brahmaand 🌌 &bull; TimeMeshin ⚡
### Sovereign, Non-Autoregressive Edge Intelligence via 24-Dimensional Topological Cartridges, Zero-Multiplication Subtractive Meshes, 22 Indian Language OTM Tokenizer, and Stateless 802.11 Layer-2 TimeMesh Wi-Fi Protocol

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22800741.svg)](https://doi.org/10.5281/zenodo.22800741)
[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1%20(Free%20Research%20%2F%20Commercial%20Paid)-orange.svg)](LICENSE)
[![Commercial: Rate Card](https://img.shields.io/badge/Commercial%20Licensing-Enterprise%20OEM-brightgreen.svg)](COMMERCIAL.md)
[![Hardware Target: RP2040 / ESP32](https://img.shields.io/badge/Hardware-%E2%82%B9150%20Microcontrollers%20(264KB%20SRAM)-blue)](#)
[![Inference Cost](https://img.shields.io/badge/Cloud%20Inference%20Cost-%240.00-success)](#)

---

## 🎮 Live Interactive Web Simulators (100% Client-Side)

Experience the engines running live in your browser at **\$0.00 cloud inference cost**:
* 📻 **[Live TimeMesh Wi-Fi Sovereign Soundbox Simulator](web_deployment/timemesh_wifi_soundbox_simulator.html)** (Blast 802.11 payment packets & hear native Pan-Indic voice output in $<1\text{ ms}$).
* ⚡ **[16-Agent Sovereign Micro-AI Studio](web_deployment/brahmand_pico_16agent_studio.html)** (Live Web REPL and Raspberry Pi Pico RP2040 agent mesh).
* 📊 **[100% Client-Side WebAssembly HUD](web_deployment/index.html)** (Live token fertility benchmarks and local CPU latency telemetry).

---

## 📖 Architectural Overview

**Project Brahmaand** is a sovereign, offline-first neuro-symbolic intelligence architecture designed to run on ultra-low-power edge silicon (such as the **Raspberry Pi Pico RP2040 / Cortex-M0+**, \$1 ESP32 chips, and embedded microcontrollers $<50\text{ mW}$) at **\$0.00 cloud inference cost**.

```
                               ┌──────────────────────────────────────────────┐
                               │            INCOMING AUDIO / INPUT            │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                      ┌────────────────────────────────────────────────────────────────┐
                      │             TIMEMESHIN INDIC OTM TOKENIZER LAYER               │
                      │  • 22 Scheduled Indian Languages + Code-Mixed (Hinglish/etc.)  │
                      │  • 62.7% Token Bloat Reduction (7.35 ➔ 2.74 tokens/word)       │
                      │  • Native Pan-Indic Numeral Translation (०-९, ০-৯ ➔ 0-9)       │
                      └───────────────────────────────┬────────────────────────────────┘
                                                      │
                                                      ▼
                      ┌────────────────────────────────────────────────────────────────┐
                      │          TIMEMESHIN DETERMINISTIC TEMPORAL PLAYHEAD            │
                      │  • Ground-truth memory anchored strictly to timestamp (t ≤ T)  │
                      │  • Zero state drift & Zero context hallucination               │
                      │  • B-Frame speculative OCC branching + R-Frame causal rewinds  │
                      └───────────────────────────────┬────────────────────────────────┘
                                                      │
                                                      ▼
                      ┌────────────────────────────────────────────────────────────────┐
                      │             SHOWLLM / BRAHMAAND BARE-METAL ENGINE              │
                      │  • Subtractive PO2 Bitshift Mesh (< 0.35 ms CPU Latency)       │
                      │  • 24-D Continuous Topological Manifolds (M²⁴ / SCM)           │
                      │  • 20.0 KB SRAM Microcontroller Execution ($0.00 Cloud Cost)   │
                      └────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Benchmark Results

```text
===================================================================================
AGGREGATE 22-LANGUAGE INDIC TOKENIZER BENCHMARK:
  • Total Words Evaluated:         141
  • TimeMeshin OTM Tokens:         386 (Avg Fertility: 2.74 tokens/word)
  • Standard Byte-level BPE:       1036 (Avg Fertility: 7.35 tokens/word)
  • Total Token Bloat Reduction:   62.7% (Akshara preservation across all 22 languages)
  • Average CPU Latency:           354 microseconds (< 0.35 ms)
  • Hallucination Rate:            0.0% (Exact Hardware ALU Execution)
===================================================================================
TIMEMESH-OVER-WIFI (RAW 802.11 LAYER-2 ACTION FRAMES):
  • Average Packet Payload Size:   45 to 89 Bytes (Max Allowed: 250 Bytes)
  • Wireless Transmission Latency: ~0.75 milliseconds (Zero Router / Zero Handshake)
  • On-Chip TimeMeshVM Latency:    ~64 microseconds (< 0.08 ms)
  • Total End-to-End Latency:      < 1.0 millisecond (Instantaneous!)
===================================================================================
```

---

## 🇮🇳 The 22 Scheduled Indian Languages Supported

| Language Family | Languages (ISO 639 Codes) |
| :--- | :--- |
| **Indo-Aryan (15)** | Hindi (`hi`), Bengali (`bn`), Marathi (`mr`), Gujarati (`gu`), Punjabi (`pa`), Odia (`or`), Assamese (`as`), Maithili (`mai`), Dogri (`doi`), Konkani (`kok`), Nepali (`ne`), Sindhi (`sd`), Sanskrit (`sa`), Kashmiri (`ks`), Urdu (`ur`) |
| **Dravidian (4)** | Tamil (`ta`), Telugu (`te`), Kannada (`kn`), Malayalam (`ml`) |
| **Tibeto-Burman (2)** | Bodo (`brx`), Manipuri / Meitei (`mni`) |
| **Austroasiatic (1)** | Santali (`sat`) |
| **Lingua & Code-Mixed** | English (`en`), Hinglish, Tanglish, Kanglish |

---

## 📂 Repository Layout

```text
brahmaand/
├── web_deployment/
│   ├── timemesh_wifi_soundbox_simulator.html # Live Interactive Soundbox Web Simulator
│   ├── brahmand_pico_16agent_studio.html    # 16-Agent Micro-AI Studio Web REPL
│   └── index.html                           # 100% Client-Side WebAssembly HUD
├── python_mesh/
│   ├── timemeshin_indic_otm_tokenizer.py    # 22-Language Akshara & OTM Tokenizer
│   ├── test_and_benchmark_22_indic_languages.py # Automated 22-language validation
│   ├── brahmand_pipeline.py                 # Full Thinker-Speaker sovereign pipeline
│   └── node_proportional_otm.py             # Event-driven neural mesh
├── cpp_core/
│   ├── timemeshin_indic_otm_tokenizer.hpp   # Bare-metal C++17 22-language tokenizer
│   ├── micro_otm_parser.hpp                 # 12-slot semantic intent engine
│   ├── otm_subtractive_attention.hpp        # Zero-multiplier subtractive attention
│   ├── otm_subtractive_ffn.hpp              # Zero-multiplier SwiPO2 FFN
│   └── brahmand_sovereign_model.hpp         # Unified native C++ sovereign model
├── micropython/
│   ├── indic_otm_tokenizer.py               # Lightweight Pico RP2040 tokenizer
│   └── main.py                              # Live interactive Pico REPL engine
├── paper/
│   └── brahmand_paper.tex                   # Academic LaTeX manuscript
├── COMMERCIAL.md                            # Enterprise OEM Licensing Terms & Rate Cards
├── LICENSE                                  # Business Source License 1.1 (BSL 1.1)
└── README.md
```

---

## 📜 Dual-Licensing Terms

* **Open-Source / Academic Track:** Licensed under **Business Source License 1.1 (BSL 1.1)**. 100% free for educational, academic research, evaluation, and non-commercial personal testing. Automatically converts to **Apache License 2.0** on **2030-01-01**.
* **Commercial Enterprise Track:** Production deployment on revenue-generating hardware (including FinTech soundboxes, POS terminals, IoT sensor fleets) or commercial cloud SaaS backends requires a paid commercial enterprise license. See [COMMERCIAL.md](COMMERCIAL.md) for tiered OEM rate cards.
* **Author & Inventor:** Chandramouli ([@Changmaulee](https://github.com/Changmaulee)) &bull; Dr. Changmaulee Labs &bull; `yellowbridgeconnections@gmail.com`.
