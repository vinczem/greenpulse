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
        self.et_correction_factor = config.get("et_correction_factor", 1.0)
        self.force_daily = config.get("force_daily_watering", False)
        self.force_amount = config.get("force_watering_amount", 5.0)

    def get_soil_retention_factor(self):
        """
        Returns a factor based on soil type.
        < 1.0: Poor retention (Sandy) -> Needs more water / frequent watering
        > 1.0: Good retention (Clay) -> Needs less water / less frequent watering
        """
        st = self.soil_type.lower()
        if "homokos" in st: return 0.8
        if "agyagos" in st: return 1.2
        if "humuszos" in st: return 1.1
        return 1.0

    def calculate_needs(self, current_deficit, current_weather, forecast, interval_hours, irrigation_amount=0, has_watered_today=False):
        """
        Calculate irrigation needs based on cumulative water balance.
        Returns: (required: bool, amount: float, reason: str, new_deficit: float, details: dict)
        """
        if not current_weather or not forecast:
            return False, 0, "Hiányzó időjárási adatok", current_deficit, {}

        # 1. Calculate ET0 (Reference Evapotranspiration) using current instantaneous weather
        temp = current_weather.get('temperature', 20)
        humidity = current_weather.get('humidity', 50)
        wind = current_weather.get('wind_speed', 0)
        
        # Base ET rate for the day (mm/day)
        et0 = 0.0
        if temp > 10:
            et0 = (0.04 * temp) - (0.01 * humidity) + (0.1 * wind)
            if et0 < 0: et0 = 0
            
        # Interval ET (proportion of the day)
        interval_et0 = et0 * (interval_hours / 24.0)
        
        # 2. Crop Coefficient (Kc)
        kc = 1.0
        if self.grass_type == "Sportfű": kc = 1.1
        elif self.grass_type == "Szárazságtűrő": kc = 0.7
        
        # 3. ET Correction Factor
        et_adjusted = interval_et0 * kc * (1 - (self.shade_pct / 200)) * self.et_correction_factor
        
        # 4. Water Supply
        # Current rain from API (usually 1h volume). Scale by interval roughly if interval != 1.
        current_rain = current_weather.get('rain_amount', 0)
        if interval_hours != 1.0 and interval_hours > 0:
            current_rain = current_rain * interval_hours
            
        retention_factor = self.get_soil_retention_factor()
        effective_rain = current_rain * retention_factor
        
        # 5. Cumulative Balance
        # Deficit increases with ET, decreases with rain and irrigation
        new_deficit = current_deficit + et_adjusted - effective_rain - irrigation_amount
        new_deficit = max(0.0, new_deficit) # Clamp at 0 (field capacity), excess water runs off
        
        deficit = new_deficit
        forecast_rain = forecast.get('total_rain_next_24h', 0)
        
        logger.info(f"Calc: ET={et_adjusted:.2f}, Rain={effective_rain:.2f}, Irr={irrigation_amount:.2f}, Deficit: {current_deficit:.2f} -> {deficit:.2f}")
        
        details = {
            "et0_rate": round(et0, 2),
            "interval_et0": round(interval_et0, 2),
            "et_adjusted": round(et_adjusted, 2),
            "current_rain": round(current_rain, 2),
            "effective_rain": round(effective_rain, 2),
            "irrigation_amount": round(irrigation_amount, 2),
            "previous_deficit": round(current_deficit, 2),
            "new_deficit": round(deficit, 2),
            "forecast_rain": round(forecast_rain, 2),
            "et_correction_factor": self.et_correction_factor,
            "soil_retention_factor": retention_factor,
            "shade_factor": self.shade_pct,
            "wind_speed": wind,
            "temperature": temp,
            "humidity": humidity,
            "kc": kc,
            "interval_hours": interval_hours,
            "min_watering_amount": self.min_amount
        }

        # Forced Watering Logic
        if self.force_daily and not has_watered_today:
            weather_amount = 0
            if deficit > self.min_amount:
                weather_amount = min(deficit, self.max_amount)
            
            if weather_amount > self.force_amount:
                return True, round(weather_amount, 1), f"Időjárás alapú öntözés (több mint a kényszerített {self.force_amount} mm).", deficit, details
            else:
                return True, round(self.force_amount, 1), "Kényszerített napi öntözés.", deficit, details

        # Standard Logic
        if deficit > self.min_amount:
            amount = min(deficit, self.max_amount)
            reason = f"Vízhiány: {deficit:.1f} mm. (Küszöb: {self.min_amount} mm)"
            if deficit > self.max_amount:
                reason += f" (Maximumra korlátozva: {self.max_amount} mm)"
                
            # Wait if rain is forecasted
            if forecast_rain > 5:
                return False, 0, f"Eső várható a következő 24 órában ({forecast_rain} mm). Vízhiány: {deficit:.2f} mm.", deficit, details
                
            return True, round(amount, 1), reason, deficit, details
        else:
            if deficit > 0:
                return False, 0, f"A vízhiány ({deficit:.1f} mm) nem éri el a minimumot ({self.min_amount} mm).", deficit, details
            else:
                return False, 0, f"Nincs szükség öntözésre (egyensúlyban).", deficit, details

calculator = CalculationEngine()
