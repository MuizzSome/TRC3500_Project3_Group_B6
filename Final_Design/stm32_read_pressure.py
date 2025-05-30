import serial
import time
import os
import csv
import matplotlib.pyplot as plt

# --- Configuration ---
PORT = 'COM7'
BAUD_RATE = 115200
TIMEOUT = 1
N_SAMPLES = 1000
DELAY_BETWEEN_SAMPLES = 0.05  # seconds
SUBFOLDER = 'pressure_sense_data'
MAX_FILES = 5
TRACKER_FILE = os.path.join(SUBFOLDER, 'current_index.txt')

def get_next_file_index():
    if not os.path.exists(SUBFOLDER):
        os.makedirs(SUBFOLDER)
    if not os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'w') as f:
            f.write('1')
        return 1
    else:
        with open(TRACKER_FILE, 'r') as f:
            index = int(f.read().strip())
        next_index = 1 if index >= MAX_FILES else index + 1
        with open(TRACKER_FILE, 'w') as f:
            f.write(str(next_index))
        return next_index

def plot_adc_data(values, title):
    a0_vals = [v[0] for v in values]
    a3_vals = [v[1] for v in values]
    plt.figure(figsize=(10, 5))
    plt.plot(a0_vals, label="A0", color='b')
    plt.plot(a3_vals, label="A3", color='r')
    plt.title(title)
    plt.xlabel("Sample Number")
    plt.ylabel("ADC Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    try:
        file_index = get_next_file_index()
        filename = f'adc_data_{file_index}.csv'
        filepath = os.path.join(SUBFOLDER, filename)

        with serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            time.sleep(2)
            ser.reset_input_buffer()
            values = []
            print(f"Recording {N_SAMPLES} ADC samples (0.5s interval) to {filename}...")

            while len(values) < N_SAMPLES:
                line = ser.readline().decode().strip()

                if not line:
                    continue

                if "ADC A0" in line and "A3" in line:
                    try:
                        parts = line.replace("ADC", "").replace("=", "").replace(",", "").split()
                        val_a0 = int(parts[1])
                        val_a3 = int(parts[3])
                        values.append((val_a0, val_a3))
                        print(f"Sample {len(values)}: A0 = {val_a0}, A3 = {val_a3}")
                        time.sleep(DELAY_BETWEEN_SAMPLES)
                    except (ValueError, IndexError):
                        print("Malformed ADC line:", line)

        # Save to CSV
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Sample Number", "ADC A0", "ADC A3"])
            for i, (val_a0, val_a3) in enumerate(values, start=1):
                writer.writerow([i, val_a0, val_a3])


        print(f"\nSaved {N_SAMPLES} ADC samples to {filepath}")

        # Plot the data
        plot_adc_data(values, title=f"ADC Data (File: {filename})")

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")

if __name__ == "__main__":
    main()
