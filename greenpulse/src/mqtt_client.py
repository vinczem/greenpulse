import paho.mqtt.client as mqtt
import json
import logging
from config import config

logger = logging.getLogger("GreenPulse.MQTT")

class MQTTClient:
    def __init__(self):
        self.host = config.get("mqtt_host")
        self.port = config.get("mqtt_port")
        self.user = config.get("mqtt_user")
        self.password = config.get("mqtt_password")
        
        self.topic_command = config.get("mqtt_topic_command")
        self.topic_heartbeat = config.get("mqtt_topic_heartbeat")
        self.topic_feedback = config.get("mqtt_topic_feedback")
        
        self.client = mqtt.Client()
        if self.user and self.password:
            self.client.username_pw_set(self.user, self.password)
            
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            logger.info(f"Connected to MQTT broker at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT: {e}")

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"MQTT Connected with result code {rc}")
        client.subscribe(self.topic_feedback)

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"Received message on {msg.topic}: {payload}")
            
            # Log to database
            from database import db
            conn = db.get_connection()
            if conn:
                cursor = conn.cursor()
                event_type = 'manual' if payload.get('type') == 'Manual watering' else 'watering_end'
                amount = payload.get('amount', 0)
                notes = payload.get('notes', '')
                
                cursor.execute("""
                    INSERT INTO irrigation_logs (event_type, water_amount, notes, raw_data)
                    VALUES (%s, %s, %s, %s)
                """, (event_type, amount, notes, json.dumps(payload)))
                conn.commit()
                cursor.close()
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def publish_command(self, required, amount, reason):
        payload = {
            "watering_required": required,
            "water_amount_lpm2": amount,
            "reason": reason
        }
        self.client.publish(self.topic_command, json.dumps(payload), retain=True)
        logger.info(f"Published command: {payload}")

    def publish_heartbeat(self):
        payload = {
            "status": "online",
            "timestamp": logging.Formatter('%(asctime)s').format(logging.LogRecord(None, None, None, None, None, None, None))
        }
        self.client.publish(self.topic_heartbeat, json.dumps(payload))

mqtt_client = MQTTClient()
