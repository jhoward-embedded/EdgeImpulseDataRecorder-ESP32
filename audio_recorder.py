import serial
import wave
import struct
import os
import time

# --- Configuration ---
PORT = 'COM5'         # Change this to your ESP32's COM port
BAUD = 921600         # Must match the ESP32 baud rate
SAMPLE_RATE = 16000
RECORD_SECONDS = 3   # Duration for each bulk recording
OUTPUT_DIR = "dataset_recordings"

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def live_debug(ser):
    """
    Tells ESP32 to enter debug mode and displays a real-time volume meter.
    """
    print("\n--- LIVE MIC CHECK (Press Ctrl+C to return to menu) ---")
    ser.write(b'd')  # Send 'd' command to ESP32 for debug mode
    ser.flushInput()
    
    try:
        while True:
            # In debug mode, we expect ASCII lines (Serial.println)
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                try:
                    val = abs(int(line))
                    # Create a simple visual meter using hashtags
                    # Adjust 'val // 500' if the meter is too sensitive or not sensitive enough
                    meter_level = min(val // 400, 50) 
                    meter = "#" * meter_level
                    print(f"[{meter:<50}] {val}", end='\r')
                except ValueError:
                    continue
    except KeyboardInterrupt:
        print("\n\nExiting Debug Mode...")
        ser.write(b's')  # Send 's' to switch back to streaming mode
        time.sleep(0.5)
        ser.flushInput()

def record_sample(ser, file_path):
    """
    Tells ESP32 to stream raw binary data and saves it to a .wav file.
    """
    samples = []
    total_samples = SAMPLE_RATE * RECORD_SECONDS
    
    ser.write(b's')  # Ensure ESP32 is in streaming mode
    time.sleep(0.1)
    ser.flushInput()
    
    print(f"--- Recording {RECORD_SECONDS} seconds ---")
    print("Capturing binary data...")

    while len(samples) < total_samples:
        # Read 2 bytes (16-bit PCM sample)
        chunk = ser.read(2)
        if len(chunk) == 2:
            # Unpack Little Endian signed short
            sample = struct.unpack('<h', chunk)[0]
            # Safety clip to avoid struct.error (though unpack handles this better)
            sample = max(min(sample, 32767), -32768)
            samples.append(sample)
    
    # Save as WAV
    with wave.open(file_path, 'wb') as obj:
        obj.setnchannels(1)   # Mono
        obj.setsampwidth(2)   # 16-bit
        obj.setframerate(SAMPLE_RATE)
        # Pack list into binary string for WAV format
        bin_data = struct.pack('<' + ('h' * len(samples)), *samples)
        obj.writeframes(bin_data)
    
    print(f"SUCCESS: Saved to {file_path}\n")

def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to ESP32 on {PORT}")
        time.sleep(2) # Wait for ESP32 boot
    except Exception as e:
        print(f"ERROR: Could not open serial port {PORT}. {e}")
        return

    while True:
        print("\n" + "="*30)
        print(" ESP32 AUDIO DATA COLLECTOR")
        print("="*30)
        print("1. Live Debug (Check Mic Wiring/Level)")
        print("2. Bulk Recording (10s segments)")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ")

        if choice == '1':
            live_debug(ser)
        
        elif choice == '2':
            label = input("Enter label for files (e.g., 'wakeword' or 'noise'): ").strip()
            if not label: label = "sample"
            
            count = 1
            while True:
                filename = f"{label}_{int(time.time())}_{count}.wav"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                print(f"\nReady to record sample #{count}")
                cmd = input("Press Enter to START recording (or 'q' to stop batch): ")
                
                if cmd.lower() == 'q':
                    break
                
                record_sample(ser, filepath)
                count += 1
                
        elif choice == '3':
            print("Closing connection...")
            ser.close()
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
