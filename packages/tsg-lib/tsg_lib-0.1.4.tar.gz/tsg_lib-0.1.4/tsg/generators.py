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
    def __init__(self, start_value=10.0, slope=1.0):
        """
        A linear trend generator: x_t = x_{t-1} + slope

        Parameters:
        - start_value: initial value of the series
        - slope: change per step (can be negative, zero, or fractional)
        """
        self.initial_value = start_value
        self.current_value = start_value
        self.slope = slope

    def generate_value(self, last_value=None):
        self.current_value += self.slope
        return self.current_value

    def reset(self):
        self.current_value = self.initial_value


class ConstantGenerator(BaseGenerator):
    def generate_value(self, last_value):
        """
        Always returns the last value, simulating a constant time series.
        Useful as a baseline or in environments where no variation is expected.
        """
        return last_value  # Always constant


class PeriodicTrendGenerator(BaseGenerator):
    def __init__(self, start_value=10.0, amplitude=1.0, frequency=1.0):
        """
        Simulates a periodic signal using a sine wave.

        Parameters:
        - start_value: vertical offset (baseline level of the signal)
        - amplitude: height of the wave above/below the baseline
        - frequency: angular frequency (controls how fast the signal oscillates)
        """
        self.start_value = start_value
        self.amplitude = amplitude
        self.frequency = frequency
        self.t = 0  # Internal time step counter

    def generate_value(self, last_value=None):
        """
        Generates the next value in the sine wave based on time step `t`.
        """
        value = self.amplitude * np.sin(self.frequency * self.t) + self.start_value
        self.t += 1
        return value

    def reset(self):
        """
        Resets the internal time step counter.
        """
        self.t = 0



class OrnsteinUhlenbeckGenerator(BaseGenerator):
    def __init__(self, mu=0.0, theta=0.15, sigma=0.2, dt=1.0, start_value=0.0):
        """
        OU process generator.

        Parameters:
        - mu: long-term mean
        - theta: speed of mean reversion
        - sigma: volatility
        - dt: time step size
        - start_value: initial value
        """
        self.mu = mu
        self.theta = theta
        self.sigma = sigma
        self.dt = dt
        self.start_value = start_value
        self.current_value = start_value

    def generate_value(self, last_value=None):
        if last_value is None:
            last_value = self.current_value

        noise = np.random.normal()
        new_value = (
            last_value +
            self.theta * (self.mu - last_value) * self.dt +
            self.sigma * np.sqrt(self.dt) * noise
        )

        self.current_value = new_value
        return new_value

    def reset(self):
        self.current_value = self.start_value


class RandomWalkGenerator(BaseGenerator):
    def __init__(self, start_value=0.0, mu=0.0, sigma=1.0):
        """
        Simulates a random walk:
        x_t = x_{t-1} + mu + sigma * ε_t, where ε_t ~ N(0, 1)

        Parameters:
        - start_value: initial value
        - mu: drift (expected change per step)
        - sigma: standard deviation of noise (volatility)
        """
        self.start_value = start_value
        self.mu = mu
        self.sigma = sigma
        self.current_value = start_value

    def generate_value(self, last_value=None):
        """
        Generates the next value in the random walk.
        If last_value is None, continues from internal state.
        """
        if last_value is None:
            last_value = self.current_value

        noise = np.random.normal()
        new_value = last_value + self.mu + self.sigma * noise
        self.current_value = new_value
        return new_value

    def reset(self):
        """Resets the generator to its initial value."""
        self.current_value = self.start_value


