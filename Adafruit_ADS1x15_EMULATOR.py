import random

class SimulatedADS1115:
    def __init__(self):
        self.gain = 1
        self.base_pressure = random.uniform(900, 950)               # Base pressure to go off of
        self.drift = [random.uniform(-0.1, 0.1) for _ in range(4)]  # Make each cylinder drift slightly
        self.last_pressure = [self.base_pressure] * 4

    def read_adc(self, channel, gain=1):
        """
        Simulates an ADC reading with realistic small variations, mimicking a well-functioning engine.
        """

        # Making pressure fluctuate with a sort of noise
        noise = random.uniform(-1.0, 1.0)
        drift = self.drift[channel]
        
        # Update pressure here
        pressure = self.last_pressure[channel] + drift + noise
        
        # Keep pressure from going insanely out of range
        pressure = max(850, min(1050, pressure))

        self.last_pressure[channel] = pressure

        # Convert pressure to voltage to emulate the adafruit sensor
        voltage = (pressure * 3.5 / 1000) + 0.5     # Convert pressure to voltage
        raw_value = int((voltage / 4.096) * 32767)  # Convert to raw ADC value

        return raw_value
