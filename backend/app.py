from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import uuid
import os

from devices.simulator import IoTDevice

from crypto.ecc import (
    generate_ecc_key_pair,
    generate_shared_secret,
    derive_session_key
)

from crypto.aes import encrypt_data, decrypt_data

from database.db import (
    get_connection,
    initialize_database,
    log_security_event,
    is_message_replayed
)


# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)
CORS(app)

initialize_database()


# --------------------------------------------------
# HOME / HEALTH CHECK
# --------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "Secure IoT Backend is running!"
    })


# --------------------------------------------------
# SECURE IoT DATA COMMUNICATION
# ECC + ECDH + AES-256-GCM + REPLAY PROTECTION
# --------------------------------------------------

@app.route("/api/device/data")
def secure_device_data():

    try:
        # Generate IoT sensor data
        device = IoTDevice("IOT-001")
        sensor_data = device.generate_sensor_data()

        # Use provided message ID or generate a new one
        message_id = request.args.get("message_id")

        if not message_id:
            message_id = str(uuid.uuid4())

        # --------------------------------------------------
        # ECC KEY GENERATION
        # --------------------------------------------------

        device_a_private, device_a_public = generate_ecc_key_pair()
        device_b_private, device_b_public = generate_ecc_key_pair()

        # --------------------------------------------------
        # ECDH SHARED SECRET
        # --------------------------------------------------

        device_a_shared = generate_shared_secret(
            device_a_private,
            device_b_public
        )

        device_b_shared = generate_shared_secret(
            device_b_private,
            device_a_public
        )

        log_security_event(
            "ECC_KEY_EXCHANGE",
            "SUCCESS",
            "ECDH shared secret established successfully"
        )

        # --------------------------------------------------
        # DERIVE AES SESSION KEY
        # --------------------------------------------------

        device_a_key = derive_session_key(device_a_shared)
        device_b_key = derive_session_key(device_b_shared)

        # --------------------------------------------------
        # AES-256-GCM ENCRYPTION
        # --------------------------------------------------

        sensor_json = json.dumps(sensor_data)

        nonce, ciphertext = encrypt_data(
            device_a_key,
            sensor_json
        )

        log_security_event(
            "AES_ENCRYPTION",
            "SUCCESS",
            "Sensor data encrypted using AES-256-GCM"
        )

        # Simulate transmission
        transmitted_nonce = nonce
        transmitted_ciphertext = ciphertext

        # --------------------------------------------------
        # AES-256-GCM DECRYPTION
        # --------------------------------------------------

        decrypted_data = decrypt_data(
            device_b_key,
            transmitted_nonce,
            transmitted_ciphertext
        )

        received_data = json.loads(decrypted_data)

        log_security_event(
            "AES_DECRYPTION",
            "SUCCESS",
            "Encrypted sensor data successfully decrypted"
        )

        # --------------------------------------------------
        # REPLAY PROTECTION
        # --------------------------------------------------

        if is_message_replayed(
            message_id,
            received_data["timestamp"]
        ):

            log_security_event(
                "REPLAY_ATTACK",
                "BLOCKED",
                f"Duplicate message detected: {message_id}"
            )

            return jsonify({
                "success": False,
                "message": "Replay attack detected",
                "message_id": message_id,
                "security": {
                    "replay_protection": "BLOCKED"
                }
            }), 409

        log_security_event(
            "REPLAY_PROTECTION",
            "SUCCESS",
            f"New message accepted: {message_id}"
        )

        # --------------------------------------------------
        # STORE SENSOR DATA
        # --------------------------------------------------

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO sensor_data
            (device_id, temperature, humidity, timestamp, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                received_data["device_id"],
                received_data["temperature"],
                received_data["humidity"],
                received_data["timestamp"],
                received_data["status"]
            )
        )

        connection.commit()
        connection.close()

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return jsonify({
            "success": True,
            "message": "Secure IoT communication successful",
            "message_id": message_id,

            "device": sensor_data,

            "security": {
                "ecc_key_exchange": "SUCCESS",
                "aes_encryption": "SUCCESS",
                "data_decryption": "SUCCESS",
                "replay_protection": "ACTIVE"
            },

            "encrypted_data": ciphertext.hex(),

            "received_data": received_data,

            "database": "Sensor data stored successfully"
        })

    except Exception as e:

        log_security_event(
            "SECURE_COMMUNICATION",
            "FAILED",
            str(e)
        )

        return jsonify({
            "success": False,
            "message": "Secure communication failed",
            "error": str(e)
        }), 500


# --------------------------------------------------
# REPLAY ATTACK DEMONSTRATION
# --------------------------------------------------

@app.route("/api/security/replay-test")
def replay_test():

    try:

        # Fixed message represents a captured old message
        message_id = "REPLAY-DEMO-001"
        timestamp = "2026-10-05T18:00:00"

        # First transmission
        first_check = is_message_replayed(
            message_id,
            timestamp
        )

        if first_check:

            return jsonify({
                "success": False,
                "message": "Replay test setup failed"
            }), 500

        # Same message transmitted again
        second_check = is_message_replayed(
            message_id,
            timestamp
        )

        if second_check:

            log_security_event(
                "REPLAY_ATTACK",
                "BLOCKED",
                "Duplicate message detected during replay attack simulation"
            )

            return jsonify({
                "success": True,
                "message": "Replay attack detected and blocked",
                "security": {
                    "attack": "REPLAY ATTACK",
                    "replay_protection": "BLOCKED",
                    "message_id": message_id
                }
            })

        return jsonify({
            "success": False,
            "message": "Replay attack was not detected"
        }), 500

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Replay test failed",
            "error": str(e)
        }), 500


# --------------------------------------------------
# SENSOR HISTORY
# --------------------------------------------------

@app.route("/api/sensor/history")
def sensor_history():

    try:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT *
            FROM sensor_data
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        history = []

        for row in rows:

            history.append({
                "id": row["id"],
                "device_id": row["device_id"],
                "temperature": row["temperature"],
                "humidity": row["humidity"],
                "timestamp": row["timestamp"],
                "status": row["status"]
            })

        return jsonify({
            "success": True,
            "count": len(history),
            "data": history
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Unable to fetch sensor history",
            "error": str(e)
        }), 500


# --------------------------------------------------
# DEVICE STATUS
# --------------------------------------------------

@app.route("/api/device/status")
def device_status():

    try:

        connection = get_connection()

        row = connection.execute(
            """
            SELECT *
            FROM sensor_data
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        connection.close()

        if row is None:

            return jsonify({
                "success": False,
                "message": "No sensor data available"
            }), 404

        return jsonify({
            "success": True,
            "device_id": row["device_id"],
            "status": row["status"],
            "temperature": row["temperature"],
            "humidity": row["humidity"],
            "last_updated": row["timestamp"],

            "security": {
                "ecc": "ACTIVE",
                "aes_256_gcm": "ACTIVE",
                "replay_protection": "ACTIVE"
            }
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Unable to fetch device status",
            "error": str(e)
        }), 500


# --------------------------------------------------
# SECURITY LOGS
# --------------------------------------------------

@app.route("/api/security/logs")
def security_logs():

    try:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT *
            FROM security_logs
            ORDER BY id DESC
            """
        ).fetchall()

        connection.close()

        logs = []

        for row in rows:

            logs.append({
                "id": row["id"],
                "event": row["event"],
                "status": row["status"],
                "details": row["details"],
                "timestamp": row["timestamp"]
            })

        return jsonify({
            "success": True,
            "count": len(logs),
            "logs": logs
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Unable to fetch security logs",
            "error": str(e)
        }), 500


# --------------------------------------------------
# TAMPERING ATTACK DEMONSTRATION
# AES-256-GCM INTEGRITY PROTECTION
# --------------------------------------------------

@app.route("/api/security/tamper-test")
def tamper_test():

    try:

        # Generate ECC keys
        device_a_private, device_a_public = generate_ecc_key_pair()
        device_b_private, device_b_public = generate_ecc_key_pair()

        # Generate shared secret
        shared_secret = generate_shared_secret(
            device_a_private,
            device_b_public
        )

        # Generate AES session key
        session_key = derive_session_key(shared_secret)

        # Original message
        test_data = (
            "IOT-001|Temperature:28.5|Humidity:60"
        )

        # Encrypt message
        nonce, ciphertext = encrypt_data(
            session_key,
            test_data
        )

        # --------------------------------------------------
        # SIMULATE ATTACKER MODIFYING CIPHERTEXT
        # --------------------------------------------------

        tampered_ciphertext = bytearray(ciphertext)

        tampered_ciphertext[0] ^= 1

        # Try to decrypt modified ciphertext
        decrypt_data(
            session_key,
            nonce,
            bytes(tampered_ciphertext)
        )

        # If decryption succeeds, attack was not detected
        return jsonify({
            "success": False,
            "message": "Tampering was not detected"
        }), 500

    except Exception:

        # AES-GCM authentication detects modification
        log_security_event(
            "TAMPERING_ATTACK",
            "BLOCKED",
            "Modified ciphertext rejected by AES-256-GCM authentication"
        )

        return jsonify({
            "success": True,
            "message": "Tampering detected and blocked",

            "security": {
                "attack": "TAMPERING ATTACK",
                "integrity_protection": "BLOCKED",
                "algorithm": "AES-256-GCM"
            }
        })


# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )