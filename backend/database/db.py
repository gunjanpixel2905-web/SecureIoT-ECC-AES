import sqlite3
from datetime import datetime


DATABASE = "database/secure_iot.db"


def get_connection():
    connection = sqlite3.connect(
        DATABASE,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            temperature REAL,
            humidity REAL,
            timestamp TEXT,
            status TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            status TEXT,
            details TEXT,
            timestamp TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS processed_messages (
            message_id TEXT PRIMARY KEY,
            timestamp TEXT
        )
    """)

    connection.commit()
    connection.close()
def log_security_event(event, status, details):

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO security_logs
            (event, status, details, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                event,
                status,
                details,
                datetime.now().isoformat()
            )
        )

        connection.commit()

    finally:
        connection.close()


def is_message_replayed(message_id, timestamp):
    connection = get_connection()

    try:
        existing_message = connection.execute(
            """
            SELECT message_id
            FROM processed_messages
            WHERE message_id = ?
            """,
            (message_id,)
        ).fetchone()

        if existing_message:
            return True

        connection.execute(
            """
            INSERT INTO processed_messages
            (message_id, timestamp)
            VALUES (?, ?)
            """,
            (message_id, timestamp)
        )

        connection.commit()

        return False

    finally:
        connection.close()
    