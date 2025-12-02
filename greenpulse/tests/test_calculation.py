import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import calculation
from calculation import CalculationEngine

# Mock config
class MockConfig:
    def __init__(self):
        self.data = {
            "grass_type": "Univerzális keverék",
            "soil_type": "Vályog",
            "shade_percentage": 0,
            "min_watering_amount": 5,
            "max_watering_amount": 25
        }

    def get(self, key, default=None):
        return self.data.get(key, default)

import config
config.config = MockConfig()

class TestCalculation(unittest.TestCase):
    def setUp(self):
        # Patch the config object in calculation module
        calculation.config = MockConfig()
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

class TestSoilTypes(unittest.TestCase):
    def setUp(self):
        # Patch the config object in calculation module
        self.mock_config = MockConfig()
        calculation.config = self.mock_config
        
    def test_sandy_soil(self):
        # Sandy soil (Homokos) -> Factor 0.8 -> Effective supply reduced -> Higher deficit
        self.mock_config.data["soil_type"] = "Homokos"
        engine_sand = CalculationEngine()
        
        # Scenario: Moderate rain, normally enough for Loam, but maybe not for Sand
        # ET = 5mm/day -> 3 days = 15mm needed
        # Rain = 15mm. 
        # Loam: 15 - 15 = 0 deficit.
        # Sand: 15 - (15 * 0.8) = 15 - 12 = 3mm deficit. (Still < min 5mm)
        # Let's adjust to make it trigger.
        # ET = 20mm needed. Rain = 20mm.
        # Loam: 20 - 20 = 0.
        # Sand: 20 - 16 = 4. (Close)
        
        # Let's try: ET=10mm. Rain=10mm.
        # Loam: 10 - 10 = 0.
        # Sand: 10 - 8 = 2.
        
        # We need a case where Sand triggers watering but Loam doesn't.
        # Min amount is 5.
        # Deficit > 5.
        # Sand Deficit = Need - (Supply * 0.8) > 5
        # Loam Deficit = Need - Supply <= 5
        
        # Let Need = 30. Supply = 25.
        # Loam: 30 - 25 = 5. (Borderline, usually > 5 needed) -> False
        # Sand: 30 - (25 * 0.8) = 30 - 20 = 10. -> True
        
        # Setup weather for higher ET
        # Temp 40, Wind 20 -> ET approx 3.4 mm/day -> 3 days = 10.2 mm
        current = {'temperature': 40, 'humidity': 20, 'wind_speed': 20, 'rain_amount': 0}
        
        # Supply target: ~6.2 mm
        # History: 2, 2, 2.2
        history = [{'precipitation': 2}, {'precipitation': 2}, {'precipitation': 2.2}] 
        forecast = {'total_rain_next_24h': 0}
        
        # Verify Loam first (control)
        # Deficit = 10.2 - 6.2 = 4.0 (< 5) -> False
        self.mock_config.data["soil_type"] = "Vályog"
        engine_loam = CalculationEngine()
        req_l, amt_l, _ = engine_loam.calculate_needs(current, forecast, history)
        
        # Verify Sand
        # Deficit = 10.2 - (6.2 * 0.8) = 10.2 - 4.96 = 5.24 (> 5) -> True
        self.mock_config.data["soil_type"] = "Homokos"
        engine_sand = CalculationEngine()
        req_s, amt_s, _ = engine_sand.calculate_needs(current, forecast, history)
        
        print(f"Soil Test (Sandy): Loam Amt={amt_l}, Sand Amt={amt_s}")
        self.assertGreater(amt_s, amt_l, "Sandy soil should require more water")

    def test_clay_soil(self):
        # Clay soil (Agyagos) -> Factor 1.2 -> Effective supply increased -> Lower deficit
        
        # Scenario: Deficit exists for Loam, but Clay retains enough water to skip.
        # Need ~ 20 mm (High heat/wind over 3 days). 
        # Supply ~ 14 mm.
        # Loam Deficit = 6. (> 5) -> Water.
        # Clay Deficit = 20 - (14 * 1.2) = 3.2. (< 5) -> No Water.
        
        # To get ET ~ 6.6/day -> Need extreme weather or mock.
        # Let's just use the same weather as above (ET=10.2) but lower supply.
        # Need = 10.2.
        # Target Loam Deficit = 6 => Supply = 4.2.
        # Clay Deficit = 10.2 - (4.2 * 1.2) = 10.2 - 5.04 = 5.16. (Still > 5).
        
        # We need Clay factor to push it below 5.
        # Let's try Supply = 5.
        # Loam Deficit = 10.2 - 5 = 5.2. (> 5) -> Water.
        # Clay Deficit = 10.2 - (5 * 1.2) = 10.2 - 6 = 4.2. (< 5) -> No Water.
        
        current = {'temperature': 40, 'humidity': 20, 'wind_speed': 20, 'rain_amount': 0}
        history = [{'precipitation': 1}, {'precipitation': 2}, {'precipitation': 2}] # Total 5
        forecast = {'total_rain_next_24h': 0}
        
        # Verify Loam (control)
        self.mock_config.data["soil_type"] = "Vályog"
        engine_loam = CalculationEngine()
        req_l, amt_l, _ = engine_loam.calculate_needs(current, forecast, history)
        
        # Verify Clay
        self.mock_config.data["soil_type"] = "Agyagos"
        engine_clay = CalculationEngine()
        req_c, amt_c, _ = engine_clay.calculate_needs(current, forecast, history)
        
        print(f"Soil Test (Clay): Loam Amt={amt_l}, Clay Amt={amt_c}")
        self.assertLess(amt_c, amt_l, "Clay soil should require less water")

if __name__ == '__main__':
    unittest.main()
