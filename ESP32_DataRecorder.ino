#include <driver/i2s.h>

#define I2S_WS 32
#define I2S_SCK 26
#define I2S_SD 33
#define SAMPLE_RATE 16000

// --- BOOST CONFIGURATION ---
// 14 is a good middle ground. Use 12 for maximum loudness.
#define BIT_SHIFT 14 
// Multiply the result to amplify even further (1 to 8 range)
#define DIGITAL_GAIN 4 

bool debugMode = false;

void setup() {
  Serial.begin(921600); 
  
  const i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .dma_buf_count = 8,
    .dma_buf_len = 1024,
    .use_apll = false
  };

  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  const i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK, .ws_io_num = I2S_WS, .data_out_num = -1, .data_in_num = I2S_SD
  };
  i2s_set_pin(I2S_NUM_0, &pin_config);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'd') debugMode = true;
    if (c == 's') debugMode = false;
  }

  int32_t raw_sample;
  size_t bytes_read;
  i2s_read(I2S_NUM_0, &raw_sample, 4, &bytes_read, portMAX_DELAY);
  
  if (bytes_read > 0) {
    // 1. Shift the 24-bit data from the 32-bit container
    // Shifting less (14 vs 16) makes the base signal louder
    int32_t processed = raw_sample >> BIT_SHIFT;

    // 2. Apply Digital Gain
    processed = processed * DIGITAL_GAIN;

    // 3. Safety Clamp (The "Hard Limiter")
    // This prevents the number from exceeding 16-bit limits (-32768 to 32767)
    if (processed > 32767)  processed = 32767;
    if (processed < -32768) processed = -32768;

    int16_t pcm_sample = (int16_t)processed;

    if (debugMode) {
      // Show the boosted value in Serial Plotter
      Serial.println(pcm_sample); 
    } else {
      // Send binary data to Python
      Serial.write((uint8_t)(pcm_sample & 0xFF));
      Serial.write((uint8_t)((pcm_sample >> 8) & 0xFF));
    }
  }
}
