import mysql.connector
import logging
import time
from config import config

logger = logging.getLogger("GreenPulse.DB")

class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        retries = 5
        while retries > 0:
            try:
                # First connect without DB to create it if needed
                self.conn = mysql.connector.connect(
                    host=config.db_host,
                    port=config.db_port,
                    user=config.db_user,
                    password=config.db_password
                )
                self._init_db()
                return
            except mysql.connector.Error as err:
                logger.error(f"Database connection failed: {err}. Retrying in 5s...")
                time.sleep(5)
                retries -= 1
        logger.critical("Could not connect to database after retries.")

    def _init_db(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.db_name}")
            self.conn.database = config.db_name
            
            # Table: irrigation_logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS irrigation_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type ENUM('suggestion', 'watering_start', 'watering_end', 'manual'),
                    water_amount FLOAT,
                    reason TEXT,
                    notes TEXT,
                    raw_data JSON
                )
            """)
            
            # Table: weather_history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    temp_max FLOAT,
                    temp_min FLOAT,
                    precipitation FLOAT,
                    humidity FLOAT,
                    wind_speed FLOAT,
                    et_value FLOAT
                )
            """)
            
            self.conn.commit()
            logger.info("Database initialized successfully.")
        except mysql.connector.Error as err:
            logger.error(f"Failed to initialize database: {err}")
        finally:
            cursor.close()

    def get_connection(self):
        if not self.conn or not self.conn.is_connected():
            self.connect()
        return self.conn

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()

db = Database()
