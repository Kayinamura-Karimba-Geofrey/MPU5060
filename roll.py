import serial
import time
import re

# Replace with your Arduino COM port, e.g. 'COM3' (Windows) or '/dev/ttyUSB0' (Linux/Mac)
port = 'COM7'
baud_rate = 115200

# Open serial connection
arduino = serial.Serial(port, baud_rate, timeout=1)
time.sleep(2)  # Wait for connection to stabilize

print("Reading roll and pitch from Arduino... Press Ctrl+C to stop.\n")

try:
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()

            # Try to extract roll and pitch values using regex
            match = re.search(r'Roll:\s*(-?\d+\.?\d*)\s*\|\s*Pitch:\s*(-?\d+\.?\d*)', line)
            if match:
                roll = float(match.group(1))
                pitch = float(match.group(2))
                print(f"Roll: {roll:.2f}°, Pitch: {pitch:.2f}°")
except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    arduino.close()
