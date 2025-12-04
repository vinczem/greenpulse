import requests
import logging
import time
from datetime import datetime, timedelta
from config import config

logger = logging.getLogger("GreenPulse.Weather")

class WeatherService:
    def __init__(self):
        self.api_key = config.get("openweathermap_api_key")
        self.lat = config.get("latitude")
        self.lon = config.get("longitude")
        self.units = "metric"
        self.lang = "hu"

    def get_current_weather(self):
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units={self.units}&lang={self.lang}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'temperature': data.get('main', {}).get('temp', 0),
                'humidity': data.get('main', {}).get('humidity', 50),
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'clouds': data.get('clouds', {}).get('all', 0),
                'is_raining': 'rain' in data and data['rain'].get('1h', 0) > 0,
                'rain_amount': data.get('rain', {}).get('1h', 0),
                'description': data.get('weather', [{}])[0].get('description', ''),
                'visibility': data.get('visibility', 10000) / 1000
            }
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return None

    def get_forecast(self):
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units={self.units}&lang={self.lang}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Process forecast to get next 24h summary
            # This is a simplified summary
            # Process forecast to get next 24h and 3 days summary
            total_rain_24h = 0
            total_rain_3days = 0
            temp_max = -float('inf')
            temp_min = float('inf')
            
            # 24h = 8 items (3h steps)
            # 3 days = 24 items
            for i, item in enumerate(data.get('list', [])):
                if i >= 24: break # Limit to 3 days
                
                rain = item.get('rain', {}).get('3h', 0)
                total_rain_3days += rain
                
                if i < 8: # First 24h
                    total_rain_24h += rain
                    temp = item.get('main', {}).get('temp', 0)
                    if temp > temp_max: temp_max = temp
                    if temp < temp_min: temp_min = temp
            
            return {
                'total_rain_next_24h': round(total_rain_24h, 1),
                'total_rain_next_3days': round(total_rain_3days, 1),
                'temp_max_next_24h': temp_max,
                'temp_min_next_24h': temp_min
            }
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return None

    def get_history(self, date_str):
        # date_str in YYYY-MM-DD format
        url = f"https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units={self.units}&lang={self.lang}&date={date_str}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'date': date_str,
                'temp_max': data.get('temperature', {}).get('max', 0),
                'temp_min': data.get('temperature', {}).get('min', 0),
                'precipitation': data.get('precipitation', {}).get('total', 0),
                'wind_speed': data.get('wind', {}).get('max', {}).get('speed', 0),
                'humidity': data.get('humidity', {}).get('afternoon', 50)
            }
        except Exception as e:
            logger.error(f"Error fetching history for {date_str}: {e}")
            return None

weather_service = WeatherService()
