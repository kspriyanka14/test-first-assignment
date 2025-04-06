import unittest
from datetime import datetime
from currency_converter import CurrencyConverter


class TestBasicConversion(unittest.TestCase):
    def setUp(self):
        self.converter = CurrencyConverter()

    def test_basic_functionality(self):
        # Test 1: Basic rate retrieval
        rate = self.converter.get_rate("USD", "EUR")
        self.assertIsNotNone(rate)
        self.assertAlmostEqual(rate, 0.91, places=2)

        # Test 2: Same currency returns 1.0
        rate = self.converter.get_rate("USD", "USD")
        self.assertEqual(rate, 1.0)

        # Test 3: Cross rate calculation through USD using existing rates
        rate = self.converter.get_rate("EUR", "GBP")
        self.assertIsNotNone(rate)
        expected_rate = 1.10 * 0.77  # EUR→USD→GBP = EUR→USD × USD→GBP = 1.10 × 0.77
        self.assertAlmostEqual(rate, expected_rate, places=4)

        # Test 4: Test various cross-rate calculation paths
        self.converter.exchange_rates.clear()

        # Direct rate path
        self.converter.exchange_rates[("USD", "EUR")] = 0.90
        rate = self.converter.get_rate("USD", "EUR")
        self.assertAlmostEqual(rate, 0.90, places=2)

        # Path: from_currency -> USD -> to_currency
        self.converter.exchange_rates[("JPY", "USD")] = 0.009
        self.converter.exchange_rates[("USD", "EUR")] = 0.90
        rate = self.converter.get_rate("JPY", "EUR")
        self.assertAlmostEqual(rate, 0.009 * 0.90, places=4)

        # Test error path: no valid rate
        self.converter.exchange_rates.clear()
        with self.assertRaises(ValueError):
            self.converter.get_rate("XYZ", "EUR")

        # Test invalid types for currencies
        with self.assertRaises(ValueError):
            self.converter.get_rate(123, "EUR")


class TestConversionFeatures(unittest.TestCase):
    def setUp(self):
        self.converter = CurrencyConverter()

    def test_conversion_features(self):
        # Test 1: Basic conversion with explicit user_id
        result = self.converter.convert(100, "USD", "EUR", "user1")
        self.assertEqual(result["original_amount"], 100)
        self.assertEqual(result["from_currency"], "USD")
        self.assertEqual(result["to_currency"], "EUR")
        self.assertAlmostEqual(result["converted_amount"], 91.0, places=2)

        # Test 2: Conversion without user_id
        result = self.converter.convert(100, "USD", "EUR")
        self.assertEqual(result["from_currency"], "USD")
        self.assertEqual(result["to_currency"], "EUR")

        # Test 3: Case insensitivity
        result = self.converter.convert(100, "usd", "eur")
        self.assertEqual(result["from_currency"], "USD")
        self.assertEqual(result["to_currency"], "EUR")

        # Test 4: Invalid amount (negative) raises ValueError
        with self.assertRaises(ValueError):
            self.converter.convert(-50, "USD", "EUR")

        # Test 5: Result contains timestamp
        result = self.converter.convert(100, "USD", "EUR")
        self.assertIn("timestamp", result)
        # Try to parse it as a date to make sure it's valid
        timestamp = result["timestamp"]
        try:
            datetime.fromisoformat(timestamp)
            valid_timestamp = True
        except ValueError:
            valid_timestamp = False
        self.assertTrue(valid_timestamp)

        # Test 6: Custom decimal places in formatting
        result = self.converter.convert(100, "USD", "EUR")
        formatted = self.converter.format_result(result, decimal_places=3)
        self.assertIn("100.000 USD = 91.000 EUR", formatted)


class TestUserHistory(unittest.TestCase):
    def setUp(self):
        self.converter = CurrencyConverter()

    def test_user_history(self):
        # Test 1: Initially empty history
        history = self.converter.get_user_history("user123")
        self.assertEqual(history, [])

        # Test 2: Conversion adds to history
        self.converter.convert(100, "USD", "EUR", "user123")
        history = self.converter.get_user_history("user123")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["original_amount"], 100)

        # Test 3: Multiple conversions are recorded
        self.converter.convert(200, "USD", "GBP", "user123")
        self.converter.convert(50, "EUR", "USD", "user123")
        history = self.converter.get_user_history("user123")
        self.assertEqual(len(history), 3)

        # Test 4: Conversion without user_id doesn't affect history
        self.converter.convert(300, "USD", "EUR")
        history = self.converter.get_user_history("user123")
        self.assertEqual(len(history), 3)  # Still 3, not 4

        # Test 5: Clear history works
        result = self.converter.clear_user_history("user123")
        self.assertTrue(result)
        history = self.converter.get_user_history("user123")
        self.assertFalse(history)  # Empty list is falsy

        # Test 6: Get supported currencies
        currencies = self.converter.get_supported_currencies()
        self.assertIsInstance(currencies, list)
        self.assertIn("USD", currencies)
        self.assertIn("EUR", currencies)

        # Test 7: Adding a new currency through update_exchange_rate
        self.converter.update_exchange_rate("USD", "CAD", 1.35)
        currencies = self.converter.get_supported_currencies()
        self.assertIn("CAD", currencies)


if __name__ == "__main__":
    unittest.main()
