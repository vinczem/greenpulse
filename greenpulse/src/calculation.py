import logging
from config import config

logger = logging.getLogger("GreenPulse.Calc")

class CalculationEngine:
    def __init__(self):
        self.grass_type = config.get("grass_type", "Univerzális keverék")
        self.soil_type = config.get("soil_type", "Vályog")
        self.shade_pct = config.get("shade_percentage", 0)
        self.min_amount = config.get("min_watering_amount", 5)
        self.max_amount = config.get("max_watering_amount", 25)

    def calculate_needs(self, current_weather, forecast, history_data):
        """
        Calculate irrigation needs based on weather data.
        Returns: (required: bool, amount: float, reason: str)
        """
        if not current_weather or not forecast:
            return False, 0, "Hiányzó időjárási adatok"

        # 1. Calculate ET0 (Reference Evapotranspiration) - Simplified Penman-Monteith approximation
        # We use a very simplified formula here for demonstration.
        # ET0 approx = 0.0023 * (Tmean + 17.8) * (Tmax - Tmin)^0.5 * Ra (Radiation)
        # Without radiation, we use a base value adjusted by temp and humidity.
        
        temp = current_weather['temperature']
        humidity = current_weather['humidity']
        wind = current_weather['wind_speed']
        
        # Base ET for the day (mm/day)
        et0 = 0.0
        if temp > 10:
            et0 = (0.04 * temp) - (0.01 * humidity) + (0.1 * wind)
            if et0 < 0: et0 = 0
        
        # 2. Crop Coefficient (Kc)
        kc = 1.0
        if self.grass_type == "Sportfű": kc = 1.1
        elif self.grass_type == "Szárazságtűrő": kc = 0.7
        
        # 3. Shade adjustment
        # Shade reduces ET
        et_adjusted = et0 * kc * (1 - (self.shade_pct / 200)) # 50% shade reduces ET by 25% approx
        
        # 4. Water Balance
        # Deficit = ET_adjusted - Effective Rainfall
        
        # Check recent history (last 3 days)
        recent_rain = 0
        for day in history_data:
            recent_rain += day.get('precipitation', 0)
            
        # Check forecast rain
        forecast_rain = forecast.get('total_rain_next_24h', 0)
        
        # Current rain
        current_rain = current_weather.get('rain_amount', 0)
        
        total_water_supply = recent_rain + current_rain + (forecast_rain * 0.8) # 80% confidence in forecast
        
        # Daily need approx
        daily_need = et_adjusted
        
        # If we look at a 3-day window
        three_day_need = daily_need * 3
        
        deficit = three_day_need - total_water_supply
        
        logger.info(f"Calc: ET={et_adjusted:.2f}, Supply={total_water_supply:.2f}, Deficit={deficit:.2f}")
        
        if deficit > self.min_amount:
            amount = min(deficit, self.max_amount)
            return True, round(amount, 1), f"Vízhiány: {deficit:.1f}mm. ET: {et_adjusted:.1f}mm/nap."
        else:
            if forecast_rain > 5:
                return False, 0, "Eső várható a következő 24 órában."
            elif recent_rain > 10:
                return False, 0, "Az elmúlt napok csapadéka elegendő."
            else:
                return False, 0, "Nincs szükség öntözésre (egyensúlyban)."

calculator = CalculationEngine()
