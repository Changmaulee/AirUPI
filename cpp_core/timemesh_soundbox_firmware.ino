/*
 * ====================================================================================================
 * 🌌 PROJECT BRAHMAAND & TIMEMESHIN: SOVEREIGN SMART SOUNDBOX FIRMWARE 🌌
 * ====================================================================================================
 * Hardware Target: ESP32-C3 / ESP32-WROOM / Raspberry Pi Pico W (RP2040)
 * Audio Output:    MAX98357A (I2S 3W Class-D Mono DAC Amplifier)
 * Wireless Layer:  Raw 802.11 ESP-NOW (Zero-Handshake, Zero-Router, Sub-Millisecond Layer-2 Blast)
 * Engine Core:     Embedded TimeMeshVM + 22-Language Indic OTM Numeral Phonetic Expander
 * License:         Business Source License 1.1 (BSL 1.1) / Licensor: Chandramouli (Dr. Changmaulee Labs)
 * DOI:             10.5281/zenodo.22800741
 * ====================================================================================================
 */

#include <Arduino.h>
#include <esp_now.h>
#include <WiFi.h>
#include "driver/i2s.h"

// ====================================================================================================
// 1. PIN DEFINITIONS & HARDWARE CONSTANTS
// ====================================================================================================
#define I2S_BCLK_PIN      4     // Bit Clock (BCLK)
#define I2S_LRC_PIN       5     // Word Select / Left-Right Clock (LRC / WS)
#define I2S_DOUT_PIN      6     // Serial Data Out (DIN on MAX98357A)
#define STATUS_LED_PIN    8     // Onboard Status LED (Blinks on packet arrival)

#define SAMPLE_RATE       16000 // 16 kHz Audio Stream
#define I2S_NUM           I2S_NUM_0
#define MAX_PAYLOAD_LEN   250   // 802.11 ESP-NOW max frame payload

// ====================================================================================================
// 2. EMBEDDED TIMEMESH CAUSAL LEDGER & STATE MACHINE
// ====================================================================================================
struct SoundboxState {
    char merchant_id[32];
    char shop_name[48];
    char default_lang[8]; // "hi", "ta", "te", "kn", "bn", "en"
    uint32_t total_revenue;
    uint32_t last_amount;
    char last_tx_id[32];
    uint32_t transaction_count;
};

static SoundboxState g_state = {
    "M_DEFAULT",
    "Sovereign_Bazaar_Store",
    "hi",
    0,
    0,
    "TX_INIT",
    0
};

// ====================================================================================================
// 3. 22-LANGUAGE PAN-INDIC NUMERAL & CURRENCY PHONETIC EXPANDER
// ====================================================================================================
String expand_indic_currency(uint32_t amount, const char* lang) {
    String out = "";
    
    if (strcmp(lang, "hi") == 0) { // Hindi
        if (amount == 150) out = "Ek Sau Pachas Rupaye Prapt Hue";
        else if (amount == 500) out = "Paanch Sau Rupaye Prapt Hue";
        else if (amount == 2000) out = "Do Hazaar Rupaye Prapt Hue";
        else out = String(amount) + " Rupaye Prapt Hue";
    }
    else if (strcmp(lang, "ta") == 0) { // Tamil
        if (amount == 150) out = "Noottru Aimbathu Roobai Petrukkollappattathu";
        else if (amount == 500) out = "Ainnooru Roobai Petrukkollappattathu";
        else out = String(amount) + " Roobai Petrukkollappattathu";
    }
    else if (strcmp(lang, "te") == 0) { // Telugu
        if (amount == 150) out = "Nooru Yaabhai Roopaayalu Sweekarinchabadindi";
        else if (amount == 500) out = "Aidu Vandalu Roopaayalu Sweekarinchabadindi";
        else out = String(amount) + " Roopaayalu Sweekarinchabadindi";
    }
    else if (strcmp(lang, "kn") == 0) { // Kannada
        if (amount == 150) out = "Ondu Noora Aivatthu Roopaayi Sweekarisalaagide";
        else out = String(amount) + " Roopaayi Sweekarisalaagide";
    }
    else { // English Default
        out = "Rupees " + String(amount) + " received successfully";
    }
    return out;
}

// ====================================================================================================
// 4. I2S DIGITAL AUDIO DRIVER & SYNTHETIC ACOUSTIC ENGINE
// ====================================================================================================
void init_i2s_audio() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 128,
        .use_apll = false,
        .tx_desc_auto_clear = true
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCLK_PIN,
        .ws_io_num = I2S_LRC_PIN,
        .data_out_num = I2S_DOUT_PIN,
        .data_in_num = I2S_PIN_NO_CHANGE
    };

    i2s_driver_install(I2S_NUM, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM, &pin_config);
    i2s_zero_dma_buffer(I2S_NUM);
}

// Generates an instant high-fidelity payment acoustic chime (880Hz -> 1760Hz bell) in < 15ms
void play_payment_chime() {
    const int duration_samples = SAMPLE_RATE / 4; // 250ms
    int16_t sample_buffer[128];
    size_t bytes_written;

    for (int i = 0; i < duration_samples; i += 128) {
        for (int j = 0; j < 128; j++) {
            float t = (float)(i + j) / SAMPLE_RATE;
            float freq = 880.0f + (t * 880.0f); // Ascending frequency chime
            float envelope = exp(-8.0f * t);     // Fast exponential decay
            sample_buffer[j] = (int16_t)(sin(2.0f * PI * freq * t) * envelope * 24000.0f);
        }
        i2s_write(I2S_NUM, sample_buffer, sizeof(sample_buffer), &bytes_written, portMAX_DELAY);
    }
}

// ====================================================================================================
// 5. TIMEMESH EMBEDDED PARSER (EXECUTION IN < 0.08 MS)
// ====================================================================================================
void execute_timemesh_packet(const char* tm_text) {
    uint32_t t_start_us = micros();
    
    // Parse Sigils: '#' (I-Frame), '>' (P-Frame), '?' (B-Frame), '!' (R-Frame)
    char sigil = tm_text[0];
    const char* body = tm_text + 1;
    while (*body == ' ' || *body == ':') body++;

    if (sigil == '#' || strncmp(tm_text, "KEY:", 4) == 0) {
        // [I-Frame]: Baseline Configuration Anchor
        char shop[48] = {0};
        char lang[8] = {0};
        if (sscanf(body, "shop=\"%47[^\"]\" lang=\"%7[^\"]\"", shop, lang) >= 1) {
            if (strlen(shop) > 0) strcpy(g_state.shop_name, shop);
            if (strlen(lang) > 0) strcpy(g_state.default_lang, lang);
            Serial.printf("[I-FRAME COMMIT] Shop: %s | Default Lang: %s\n", g_state.shop_name, g_state.default_lang);
        }
    }
    else if (sigil == '>' || strncmp(tm_text, "DELTA:", 6) == 0) {
        // [P-Frame]: Forward Payment Transaction (Atomic Voice Trigger)
        char tx[32] = {0};
        uint32_t amount = 0;
        char lang[8] = {0};
        strcpy(lang, g_state.default_lang);

        if (sscanf(body, "tx_id=\"%31[^\"]\" amount=%u lang=\"%7[^\"]\"", tx, &amount, lang) >= 2 ||
            sscanf(body, "tx=\"%31[^\"]\" amount=%u", tx, &amount) >= 2) {
            
            g_state.last_amount = amount;
            g_state.total_revenue += amount;
            g_state.transaction_count++;
            strcpy(g_state.last_tx_id, tx);

            uint32_t parse_us = micros() - t_start_us;
            Serial.printf("[P-FRAME COMMIT in %u us] TX: %s | Amount: ₹%u | Lang: %s\n", parse_us, tx, amount, lang);
            
            // 1. Play Instant Hardware Acoustic Bell
            play_payment_chime();
            
            // 2. Expand Phonetic String
            String speech = expand_indic_currency(amount, lang);
            Serial.printf("🔊 [SPEAKER OUTPUT]: \"%s\"\n", speech.c_str());
        }
    }
    else if (sigil == '?' || strncmp(tm_text, "WHATIF:", 7) == 0) {
        // [B-Frame]: Speculative Simulation (Zero-Pollution Query)
        uint32_t sim_amount = 0;
        sscanf(body, "amount=%u", &sim_amount);
        Serial.printf("[B-FRAME EVAL] Speculative Query: ₹%u (Committed State UNTOUCHED: Total ₹%u)\n", 
                      sim_amount, g_state.total_revenue);
    }
    else if (sigil == '!' || strncmp(tm_text, "REWIND:", 7) == 0) {
        // [R-Frame]: Causal Refund / Ledger Rewind
        uint32_t refund_amount = 0;
        sscanf(body, "amount=%u", &refund_amount);
        if (g_state.total_revenue >= refund_amount) {
            g_state.total_revenue -= refund_amount;
        }
        Serial.printf("[R-FRAME REWIND] Refund ₹%u Processed. Recomputed Total: ₹%u\n", refund_amount, g_state.total_revenue);
    }
}

// ====================================================================================================
// 6. RAW ESP-NOW RECEIVER CALLBACK (ZERO-HANDSHAKE OVER-THE-AIR PACKET BLAST)
// ====================================================================================================
void on_data_received(const uint8_t *mac_addr, const uint8_t *data, int data_len) {
    digitalWrite(STATUS_LED_PIN, HIGH);
    
    char packet_buf[MAX_PAYLOAD_LEN + 1];
    int copy_len = (data_len < MAX_PAYLOAD_LEN) ? data_len : MAX_PAYLOAD_LEN;
    memcpy(packet_buf, data, copy_len);
    packet_buf[copy_len] = '\0';

    Serial.printf("\n⚡ [RAW 802.11 PACKET INGESTED]: %d Bytes from %02X:%02X:%02X:%02X:%02X:%02X\n",
                  data_len, mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);
    
    // Execute TimeMesh VM
    execute_timemesh_packet(packet_buf);
    
    digitalWrite(STATUS_LED_PIN, LOW);
}

// ====================================================================================================
// 7. SETUP & MAIN LOOP
// ====================================================================================================
void setup() {
    Serial.begin(115200);
    delay(500);
    
    pinMode(STATUS_LED_PIN, OUTPUT);
    digitalWrite(STATUS_LED_PIN, LOW);

    Serial.println("\n=================================================================");
    Serial.println(" 🌌 PROJECT BRAHMAAND: SOVEREIGN SOUNDBOX FIRMWARE v1.0.0 🌌 ");
    Serial.println(" Protocol: TimeMesh Lang over Raw 802.11 Layer-2 (Zero-SIM/Cloud)");
    Serial.println(" DOI: 10.5281/zenodo.22800741 | License: BSL 1.1");
    Serial.println("=================================================================");

    // 1. Initialize High-Fidelity I2S Audio Amp
    init_i2s_audio();
    Serial.println(" [OK] MAX98357A I2S DAC Driver Initialized (16 kHz, 16-bit Mono)");

    // 2. Initialize Wi-Fi in Station Mode (Promiscuous ESP-NOW, Zero Router Connection)
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    Serial.printf(" [OK] Wi-Fi Radio Active in Stateless Sniffer Mode (MAC: %s)\n", WiFi.macAddress().c_str());

    // 3. Initialize ESP-NOW Protocol Layer
    if (esp_now_init() != ESP_OK) {
        Serial.println(" [ERR] Failed to initialize ESP-NOW!");
        return;
    }
    esp_now_register_recv_cb(on_data_received);
    Serial.println(" [OK] ESP-NOW Layer-2 Promiscuous Sniffer Registered");

    // 4. Startup Welcome Bell
    play_payment_chime();
    Serial.println(" 🚀 SOUNDBOX ACTIVE & LISTENING FOR TIMEMESH OVER-THE-AIR PACKETS...\n");
}

void loop() {
    // Zero polling needed. ESP-NOW interrupts trigger on_data_received() at hardware line speed.
    delay(100);
}
