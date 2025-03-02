import time
import os
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Uncomment the following line to use the Adafruit Pressure Sensor
# import Adafruit_ADS1x15
from Adafruit_ADS1x15_EMULATOR import SimulatedADS1115 as ADS1115

class PressureCheckApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pressure Check")
        
        # Uncomment the following line to set the Analog to Digital Converter to use the Adafruit Pressure Sensor
        # self.adc = Adafruit_ADS1x15.ADS1115()

        # Uncomment the following line to set the Analog to Digital Converter to use the Adafruit Pressure Emulator
        self.adc = ADS1115()

        self.previous_readings = [0] * 4            # Store previous readings for each cylinder (default 0)
        self.history = [[] for _ in range(4)]       # Store historical readings for each cylinder
        self.create_widgets()

    def create_widgets(self):
        # Define frames
        self.control_frame = tk.Frame(self.root)
        self.graph_frame = tk.Frame(self.root)

        # Place frames on gui
        self.control_frame.grid(row=0, column=0, padx=10, pady=10)
        self.graph_frame.grid(row=0, column=1, padx=10, pady=10)

        # Control frame

        self.cylinders_label = tk.Label(self.control_frame, text="Number of cylinders (1-4):")
        self.cylinders_label.pack(pady=10)

        self.cylinders_entry = tk.Entry(self.control_frame)
        self.cylinders_entry.pack(pady=5)

        self.test_type_label = tk.Label(self.control_frame, text="Test type (1:compression/2:butterfly):")
        self.test_type_label.pack(pady=10)

        self.test_type_entry = tk.Entry(self.control_frame)
        self.test_type_entry.pack(pady=5)

        self.start_button = tk.Button(self.control_frame, text="Start Test", command=self.start_test)
        self.start_button.pack(pady=20)

        self.output_text = tk.Text(self.control_frame, height=10, width=50)
        self.output_text.pack(pady=10)

        # Graph frame

        self.fig, self.ax = plt.subplots()
        self.ax.set_ylim(-10, 10)

        self.canvas = FigureCanvasTkAgg(self.fig, self.graph_frame)
        self.canvas.get_tk_widget().pack()

        self.bar_container = None

        self.fig2, self.ax2 = plt.subplots()
        self.ax2.set_ylim(0, 200)           # Adjust this if readings fall outside of expected psi frame
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Pressure (psi)')
        self.ax2.set_title('Cylinder Pressure Over Time')

        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.graph_frame)
        self.canvas2.get_tk_widget().pack()

    def start_test(self):
        try:
            cylinders = int(self.cylinders_entry.get())
            if cylinders < 1 or cylinders > 4:
                raise ValueError
            test_type = self.test_type_entry.get().strip().lower()
            if test_type not in ["1", "2"]:
                raise ValueError

            self.cylinders = cylinders
            self.test_type = test_type

            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Running {'compression' if test_type == '1' else 'butterfly'} test on {cylinders} cylinders...\n")

            self.run_test()
        except ValueError:
            messagebox.showerror("Invalid Input", "Enter valid inputs. Cylinders should be between 1 and 4, and test type should be '1' or '2'.")

    def read_sensors(self):
        readings = []
        for i in range(self.cylinders):
            voltage = self.adc.read_adc(i, gain=1) * (4.096 / 32767.0)      # Read voltage
            pressure_kpa = (voltage - 0.5) * (1000 / 3.5)                   # Convert voltage to pressure in kPa
            pressure_psi = pressure_kpa / 6.895                             # Convert kPa to PSI
            readings.append(pressure_psi)
        return readings

    def run_test(self):
        def update_readings():
            readings = self.read_sensors()

            differences = [readings[i] - self.previous_readings[i] for i in range(self.cylinders)]

            self.previous_readings = readings

            self.output_text.delete(1.0, tk.END)

            if self.test_type == "1":
                self.output_text.insert(tk.END, "Compression readings:\n")
            else:
                self.output_text.insert(tk.END, "Butterfly airflow readings:\n")

            for i, pressure in enumerate(readings, start=1):
                self.output_text.insert(tk.END, f"Cylinder {i}: {pressure:.2f} psi\n")

            # Update bar graphs
            if self.bar_container is not None:
                for bar, height in zip(self.bar_container, differences):
                    bar.set_height(height*20)
            else:
                self.bar_container = self.ax.bar(range(1, self.cylinders + 1), differences, color='blue', width=0.4)

            self.ax.set_xlabel('Cylinder')
            self.ax.set_ylabel('Pressure Difference (psi)')
            self.ax.set_title(f"{'Compression' if self.test_type == '1' else 'Butterfly'} Pressure Test")

            # Update histopryh graoph
            for i in range(self.cylinders):
                self.history[i].append(readings[i])

            self.ax2.clear()
            for i in range(self.cylinders):
                self.ax2.plot(self.history[i], label=f'Cyl {i + 1}')
            self.ax2.legend(loc='upper right')

            self.canvas.draw()
            self.canvas2.draw()

            self.root.after(250, update_readings)

        update_readings()

def main():
    root = tk.Tk()
    app = PressureCheckApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
