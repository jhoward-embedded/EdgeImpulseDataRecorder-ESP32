# 🎙️ ESP32 Audio Data Collector

A high-speed Serial utility for building machine learning audio datasets. This tool allows you to stream raw 16-bit PCM data from an ESP32, visualize signal levels in real-time, and save recordings into labeled `.wav` files.

## 🚀 Features

* **Live Debug Mode:** A real-time ASCII volume meter to verify microphone gain and wiring without saving files.
* **Bulk Recording:** Optimized workflow for capturing dozens of samples quickly—perfect for "Wake Word" training.
* **High-Speed Transfer:** Uses **921,600 Baud** to ensure 16kHz audio data is captured without packet loss.
* **Automatic Organization:** Files are timestamped and sorted by label (e.g., `command_170921400_1.wav`).

---

## 🛠️ Requirements

### Hardware

* **ESP32** (S3, C3, or Standard DevKit).
* **I2S Microphone** (e.g., INMP441, ICS-43434) or an Analog Mic using the ESP32 ADC.
* **USB Data Cable** (Ensure it is a data cable, not just a charging cable).

### Software

* **Python 3.7+**
* **PySerial** library:
```bash
pip install pyserial

```



---

## 📂 Installation & Setup

1. **Clone the Repository:**
```bash
git clone https://github.com/jhoward-embedded/EdgeImpulseDataRecorder-ESP32.git
cd EdgeImpulseDataRecorder-ESP32

```


2. **Configure the Script:**
Open `audio_collector.py` and update the `PORT` variable to match your ESP32:
```python
PORT = 'COM5'          # Windows
# PORT = '/dev/ttyUSB0' # Linux/Mac

```


3. **ESP32 Firmware:**
Ensure your ESP32 is programmed to:
* Send **raw binary** (2 bytes per sample) when it receives the character `'s'`.
* Send **ASCII integers** (text lines) when it receives the character `'d'`.



---

## 📖 How to Use

Run the script:

```bash
python audio_collector.py

```

### 1. Live Debug Mode

Choose **Option 1** to test your microphone. You will see a level meter like this:
`[##########                                        ] 4200`
If the bar doesn't move when you speak, check your I2S clock (BCLK/WS) and Data (SD) wiring.

### 2. Data Collection

Choose **Option 2** to start building your dataset.

1. Enter a label when prompted (e.g., `alexa`, `background`, `noise`).
2. Press **Enter** to start a 3-second capture.
3. The script will automatically increment the file count and save it to the `dataset_recordings/` folder.
4. Type `q` to stop the batch and return to the main menu.

---

## 📉 Technical Specs

| Parameter | Value |
| --- | --- |
| **Sample Rate** | 16,000 Hz |
| **Bit Depth** | 16-bit Signed Integer (PCM) |
| **Baud Rate** | 921,600 bps |
| **Format** | Mono .WAV (Little Endian) |

---

## 🤝 Contributing

Contributions are welcome! If you'd like to add features like a Spectrogram preview or automatic silence trimming, please open an issue or a Pull Request.

---
