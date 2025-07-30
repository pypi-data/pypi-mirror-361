import pytest
import numpy as np
from tsg.generators import (
    LinearTrendGenerator,
    ConstantGenerator,
    PeriodicTrendGenerator,
    RandomWalkGenerator,
    OrnsteinUhlenbeckGenerator,
)
from tsg.modifiers import GaussianNoise

# === LINEAR TREND GENERATOR ===

def test_linear_trend_generator_up():
    """
    Test that LinearTrendGenerator increases by 1 at each step (slope=1).
    """
    gen = LinearTrendGenerator(start_value=100, slope=1)
    values = [gen.generate_value() for _ in range(5)]
    assert values == [101, 102, 103, 104, 105]

def test_linear_trend_generator_down():
    """
    Test that LinearTrendGenerator decreases by 1 at each step (slope=-1).
    """
    gen = LinearTrendGenerator(start_value=100, slope=-1)
    values = [gen.generate_value() for _ in range(5)]
    assert values == [99, 98, 97, 96, 95]

def test_linear_trend_generator_reset_restores_initial_state():
    """
    Ensure LinearTrendGenerator resets correctly to its initial value.
    """
    gen = LinearTrendGenerator(start_value=50, slope=1)
    for _ in range(3): gen.generate_value()
    gen.reset()
    assert gen.generate_value() == 51  # After reset: 50 + 1

# === CONSTANT GENERATOR ===

def test_constant_generator():
    """
    ConstantGenerator always returns the last value passed to it.
    """
    gen = ConstantGenerator()
    val = gen.generate_value(123.45)
    assert val == 123.45
    for _ in range(3):
        assert gen.generate_value(val) == 123.45

# === PERIODIC TREND GENERATOR ===

def test_periodic_trend_generator_repeatable():
    """
    PeriodicTrendGenerator should produce a repeating sine pattern.
    With frequency=π/2, the values should follow [10.0, 11.0, 10.0, 9.0].
    """
    gen = PeriodicTrendGenerator(start_value=10.0, amplitude=1.0, frequency=np.pi / 2)
    values = [gen.generate_value() for _ in range(4)]
    expected = [10.0, 11.0, 10.0, 9.0]  # sin(0), sin(pi/2), sin(pi), sin(3pi/2)
    np.testing.assert_allclose(values, expected, rtol=1e-5)

# === RANDOM WALK GENERATOR ===

def test_random_walk_generator_drift_and_noise():
    """
    RandomWalkGenerator with sigma=0 should act like a pure drift.
    With mu=1.0, values should increase linearly from start_value.
    """
    gen = RandomWalkGenerator(start_value=0.0, mu=1.0, sigma=0.0)
    values = [gen.generate_value() for _ in range(5)]
    expected = [1.0, 2.0, 3.0, 4.0, 5.0]
    np.testing.assert_allclose(values, expected, rtol=1e-5)

def test_random_walk_generator_with_noise_has_variation():
    """
    RandomWalkGenerator with sigma > 0 should show variation in outputs.
    """
    gen = RandomWalkGenerator(start_value=0.0, mu=0.0, sigma=1.0)
    values = [gen.generate_value() for _ in range(10)]
    assert all(isinstance(v, float) for v in values)
    assert len(set(values)) > 1  # Not all values should be identical

# === ORNSTEIN-UHLENBECK GENERATOR ===

def test_ou_generator_mean_reversion():
    """
    OU process with no noise should revert toward its long-term mean (mu).
    Starting below mu should produce an increasing trend.
    """
    gen = OrnsteinUhlenbeckGenerator(mu=10.0, theta=0.5, sigma=0.0, dt=1.0, start_value=0.0)
    values = [gen.generate_value() for _ in range(5)]
    assert all(values[i] < values[i+1] for i in range(len(values)-1))

def test_ou_generator_stochasticity():
    """
    OU process with noise should fluctuate and eventually cross the mean.
    We expect it to go below and/or above the initial value depending on direction.
    """
    gen = OrnsteinUhlenbeckGenerator(mu=0.0, theta=0.3, sigma=1.0, dt=1.0, start_value=5.0)
    values = [gen.generate_value() for _ in range(100)]
    assert any(v < 0.0 for v in values)  # Should cross below mean
    assert len(set(values)) > 1          # Ensure variation

# === NOISE MODIFIER ===

def test_gaussian_noise_perturbs_base():
    """
    GaussianNoise should apply perturbations to its base generator.
    We check that output is still float and deviates from base trend.
    """
    base_gen = LinearTrendGenerator(start_value=100, slope=1)
    noisy_gen = GaussianNoise(base_gen, mu=0.0, sigma=1.0)

    noisy_values = [noisy_gen.generate_value(None) for _ in range(5)]
    assert all(isinstance(p, float) for p in noisy_values)

    # Check that noise caused deviation from the clean linear trend
    diffs = [abs(p - (101 + i)) for i, p in enumerate(noisy_values)]
    assert any(diff > 0 for diff in diffs)
