import json
import os
import logging

OPTIONS_PATH = "/data/options.json"

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.load()
        return cls._instance

    def load(self):
        self.options = {}
        if os.path.exists(OPTIONS_PATH):
            try:
                with open(OPTIONS_PATH, "r") as f:
                    self.options = json.load(f)
            except Exception as e:
                logging.error(f"Failed to load options: {e}")
        else:
            logging.warning(f"Options file not found at {OPTIONS_PATH}. Using defaults or env vars.")

    def get(self, key, default=None):
        return self.options.get(key, default)

    # Database config (hardcoded for local container)
    @property
    def db_host(self):
        return "127.0.0.1"

    @property
    def db_port(self):
        return 3306

    @property
    def db_user(self):
        return "root"

    @property
    def db_password(self):
        return "" # Default for local mysql_install_db

    @property
    def db_name(self):
        return "greenpulse"

config = Config()
