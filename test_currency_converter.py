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

if __name__ == "__main__":
    unittest.main()