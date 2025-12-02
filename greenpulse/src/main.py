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
log_level = config.get("log_level", "INFO").upper()
valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
if log_level not in valid_levels:
    # Fallback if config is messed up (e.g. contains the whole list string)
    log_level = "INFO"

logging.basicConfig(
    level=getattr(logging, log_level),
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
    # Fetch irrigation history (last 3 days to match weather history)
    irrigation_history_amount = 0
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        # Calculate start date (3 days ago)
        start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            SELECT SUM(water_amount) as total 
            FROM irrigation_logs 
            WHERE event_type IN ('manual', 'watering_end') 
            AND timestamp >= %s
        """, (start_date,))
        result = cursor.fetchone()
        if result and result[0]:
            irrigation_history_amount = float(result[0])
        cursor.close()
    except Exception as e:
        logger.error(f"DB Error fetching irrigation history: {e}")

    # Check if watered today (for forced watering logic)
    has_watered_today = False
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        today_start = datetime.now().strftime("%Y-%m-%d 00:00:00")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM irrigation_logs 
            WHERE event_type IN ('manual', 'watering_end') 
            AND timestamp >= %s
        """, (today_start,))
        result = cursor.fetchone()
        if result and result[0] > 0:
            has_watered_today = True
        cursor.close()
    except Exception as e:
        logger.error(f"DB Error checking today's watering: {e}")

    required, amount, reason, details = calculator.calculate_needs(current, forecast, history_data, irrigation_history_amount, has_watered_today)
    
    # 3. Publish Result
    mqtt_client.publish_command(required, amount, reason)
    
    # 4. Log Suggestion to DB
    try:
        import json
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO irrigation_logs (event_type, water_amount, reason, raw_data)
            VALUES ('suggestion', %s, %s, %s)
        """, (amount if required else 0, reason, json.dumps(details)))
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
    schedule.every(1).minutes.do(job_heartbeat)
    
    # Run once immediately
    job_heartbeat()
    job_check_weather_and_calculate()
    
    logger.info(f"Scheduler configured. Interval: {interval} min.")
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start Web Server
    logger.info(f"Starting Web Server on port {config.web_port}...")
    uvicorn.run(app, host="0.0.0.0", port=config.web_port, log_level="info")

if __name__ == "__main__":
    main()
