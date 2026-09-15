import math
import unittest

from tools.validate_vertex import (
    VertexSettings,
    calculate_vertex,
    rolling_population_band,
    rolling_sma,
    vertex_control,
)


class VertexControlTests(unittest.TestCase):
    def test_first_delayed_value_is_zero(self) -> None:
        result = vertex_control([10.0], [9.0], [9.5])
        self.assertEqual(result, [0.0])

    def test_new_running_highs_create_negative_imbalance(self) -> None:
        settings = VertexSettings(control_period=2)
        result = vertex_control(
            highs=[3.0, 2.0, 1.0],
            lows=[3.0, 2.0, 1.0],
            closes=[30.0, 20.0, 10.0],
            settings=settings,
        )
        self.assertAlmostEqual(result[2], -2.1, places=12)

    def test_new_running_lows_create_positive_imbalance(self) -> None:
        settings = VertexSettings(control_period=2)
        result = vertex_control(
            highs=[1.0, 2.0, 3.0],
            lows=[1.0, 2.0, 3.0],
            closes=[10.0, 20.0, 30.0],
            settings=settings,
        )
        self.assertAlmostEqual(result[2], 5.0 / 6.0, places=12)

    def test_exact_mode_does_not_use_current_bar(self) -> None:
        settings = VertexSettings(control_period=3, use_previous_bar=True)
        baseline = vertex_control([1, 2, 3], [1, 2, 3], [1, 2, 3], settings)
        changed = vertex_control([1, 2, 300], [1, 2, -300], [1, 2, 999], settings)
        self.assertEqual(baseline[-1], changed[-1])

    def test_mismatched_lengths_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            vertex_control([1.0], [1.0, 2.0], [1.0])


class RollingCalculationTests(unittest.TestCase):
    def test_sma_warmup(self) -> None:
        self.assertEqual(rolling_sma([1.0, 2.0, 3.0], 2), [None, 1.5, 2.5])

    def test_population_bands(self) -> None:
        values = [1.0, 2.0, 3.0]
        upper = rolling_population_band(values, 3, 2.0, upper=True)
        lower = rolling_population_band(values, 3, 2.0, upper=False)
        expected_width = 2.0 * math.sqrt(2.0 / 3.0)
        self.assertAlmostEqual(upper[-1], 2.0 + expected_width, places=12)
        self.assertAlmostEqual(lower[-1], 2.0 - expected_width, places=12)

    def test_complete_series_warmups(self) -> None:
        values = list(range(20))
        result = calculate_vertex(values, values, [float(v + 1) for v in values])
        self.assertIsNone(result.signal[3])
        self.assertIsNotNone(result.signal[4])
        self.assertIsNone(result.upper[10])
        self.assertIsNotNone(result.upper[11])


if __name__ == "__main__":
    unittest.main()
