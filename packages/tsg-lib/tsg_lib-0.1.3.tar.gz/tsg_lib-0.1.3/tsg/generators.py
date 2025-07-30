import numpy as np
from abc import ABC, abstractmethod

# === Base Class ===
class BaseGenerator(ABC):
    @abstractmethod
    def generate_value(self, last_value):
        """Generate the next value in the series."""
        pass

    def reset(self):
        """Optional reset method."""
        pass

# === Core Generators ===
class LinearTrendGenerator(BaseGenerator):
    def __init__(self, start_value=10.0, up=True):
        self.initial_value = start_value
        self.current_value = start_value
        self.up = up

    def generate_value(self, last_value=None):
        self.current_value += 1 if self.up else -1
        return self.current_value

    def reset(self):
        self.current_value = self.initial_value

class ConstantGenerator(BaseGenerator):
    def generate_value(self, last_value):
        return last_value  # Always constant

class PeriodicTrendGenerator(BaseGenerator):
    def __init__(self, start=10.0, amplitude=1.0, frequency=1.0):
        self.start = start
        self.amplitude = amplitude
        self.frequency = frequency
        self.t = 0

    def generate_value(self, last_value=None):
        value = self.amplitude * np.sin(self.frequency * self.t) + self.start
        self.t += 1
        return value

    def reset(self):
        self.t = 0
