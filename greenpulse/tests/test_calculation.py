import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from calculation import CalculationEngine

# Mock config
class MockConfig:
    def get(self, key, default=None):
        defaults = {
            "grass_type": "Univerzális keverék",
            "soil_type": "Vályog",
            "shade_percentage": 0,
            "min_watering_amount": 5,
            "max_watering_amount": 25
        }
        return defaults.get(key, default)

import config
config.config = MockConfig()

class TestCalculation(unittest.TestCase):
    def setUp(self):
        self.engine = CalculationEngine()

    def test_needs_watering_dry_hot(self):
        # Hot day, no rain history, no forecast rain
        # Increased parameters to ensure ET > min_amount (5mm over 3 days)
        current = {
            'temperature': 35,
            'humidity': 30,
            'wind_speed': 10,
            'rain_amount': 0
        }
        forecast = {
            'total_rain_next_24h': 0
        }
        history = [
            {'precipitation': 0},
            {'precipitation': 0},
            {'precipitation': 0}
        ]
        
        required, amount, reason = self.engine.calculate_needs(current, forecast, history)
        print(f"Dry/Hot: Required={required}, Amount={amount}, Reason={reason}")
        self.assertTrue(required)
        self.assertGreater(amount, 5)

    def test_no_watering_rainy(self):
        # Raining now, forecast rain
        current = {
            'temperature': 20,
            'humidity': 80,
            'wind_speed': 2,
            'rain_amount': 5
        }
        forecast = {
            'total_rain_next_24h': 10
        }
        history = [
            {'precipitation': 0},
            {'precipitation': 0},
            {'precipitation': 0}
        ]
        
        required, amount, reason = self.engine.calculate_needs(current, forecast, history)
        print(f"Rainy: Required={required}, Amount={amount}, Reason={reason}")
        self.assertFalse(required)
        self.assertEqual(amount, 0)

    def test_no_watering_recent_rain(self):
        # Recently rained a lot
        current = {
            'temperature': 25,
            'humidity': 50,
            'wind_speed': 3,
            'rain_amount': 0
        }
        forecast = {
            'total_rain_next_24h': 0
        }
        history = [
            {'precipitation': 15},
            {'precipitation': 10},
            {'precipitation': 0}
        ]
        
        required, amount, reason = self.engine.calculate_needs(current, forecast, history)
        print(f"Recent Rain: Required={required}, Amount={amount}, Reason={reason}")
        self.assertFalse(required)

if __name__ == '__main__':
    unittest.main()
