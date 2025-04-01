import configparser
import mysql.connector
import logging
import os

if not os.path.exists('logs'):
    os.mkdir('logs')

app = logging.getLogger('app')
thanos = logging.getLogger('thanos')

def read_cfg():
    config = configparser.ConfigParser()
    config.read('utils/configs/config.ini')  # Make sure the file exists here

    if 'DATABASE' not in config:
        raise KeyError("The 'DATABASE' section is missing in config.ini")

    try:
        db_connection = mysql.connector.connect(
            user=config.get('DATABASE', 'user'),
            password=config.get('DATABASE', 'password'),
            host=config.get('DATABASE', 'host'),
            database=config.get('DATABASE', 'database'),
            port=config.getint('DATABASE', 'port')
        )
        app.info("✅ Successfully connected to the database!")
    except Exception as e:
        app.error(f"❌ Database connection error: {e}")
        db_connection = None

    return config, db_connection
