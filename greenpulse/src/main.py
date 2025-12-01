import time
import logging
import schedule
from datetime import datetime, timedelta
from config import config
from database import db
from mqtt_client import mqtt_client
from weather import weather_service
from calculation import calculator

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.get("log_level", "INFO").upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GreenPulse.Main")

def job_heartbeat():
    logger.debug("Sending heartbeat...")
    mqtt_client.publish_heartbeat()

def job_check_weather_and_calculate():
    logger.info("Starting scheduled check...")
    
    # 1. Get Weather Data
    current = weather_service.get_current_weather()
    forecast = weather_service.get_forecast()
    
    # Get history (simplified: just use what we have or fetch yesterday)
    # Ideally we store history in DB. For now, let's fetch yesterday's history from OWM if needed
    # or rely on DB history if we had it running.
    # Let's fetch last 3 days history from OWM for accuracy
    history_data = []
    for i in range(1, 4):
        date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        day_data = weather_service.get_history(date_str)
        if day_data:
            history_data.append(day_data)
            
            # Save to DB for cache/record
            try:
                conn = db.get_connection()
                cursor = conn.cursor()
                # Check if exists
                cursor.execute("SELECT id FROM weather_history WHERE timestamp LIKE %s", (f"{date_str}%",))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO weather_history (timestamp, temp_max, temp_min, precipitation, humidity, wind_speed)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (f"{date_str} 12:00:00", day_data['temp_max'], day_data['temp_min'], 
                          day_data['precipitation'], day_data['humidity'], day_data['wind_speed']))
                    conn.commit()
                cursor.close()
            except Exception as e:
                logger.error(f"DB Error saving history: {e}")

    # 2. Calculate Needs
    required, amount, reason = calculator.calculate_needs(current, forecast, history_data)
    
    # 3. Publish Result
    mqtt_client.publish_command(required, amount, reason)
    
    # 4. Log Suggestion to DB
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO irrigation_logs (event_type, water_amount, reason, raw_data)
            VALUES ('suggestion', %s, %s, %s)
        """, (amount if required else 0, reason, "{}")) # raw_data could be weather snapshot
        conn.commit()
        cursor.close()
    except Exception as e:
        logger.error(f"DB Error saving suggestion: {e}")

import threading
import uvicorn
from web.app import app

def run_scheduler():
    logger.info("Scheduler thread started.")
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    logger.info("GreenPulse starting up...")
    
    # Initialize DB
    db.connect()
    
    # Initialize MQTT
    mqtt_client.connect()
    
    # Schedule jobs
    interval = config.get("weather_update_interval_min", 60)
    schedule.every(interval).minutes.do(job_check_weather_and_calculate)
    schedule.every(5).minutes.do(job_heartbeat)
    
    # Run once immediately
    job_heartbeat()
    # job_check_weather_and_calculate() # Optional: run on startup
    
    logger.info(f"Scheduler configured. Interval: {interval} min.")
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start Web Server
    logger.info("Starting Web Server on port 8099...")
    uvicorn.run(app, host="0.0.0.0", port=8099, log_level="info")

if __name__ == "__main__":
    main()
