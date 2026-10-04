from flask import Flask, jsonify, request
from flask_cors import CORS

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
import json
import uuid


app = Flask(__name__)
CORS(app)


# Initialize database when server starts
initialize_database()


@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "Secure IoT Backend is running!"
    })


@app.route("/api/device/data")
def secure_device_data():

    # ------------------------------------------
    # 1. Generate IoT sensor data
    # ------------------------------------------

    device = IoTDevice("IOT-001")

    sensor_data = device.generate_sensor_data()
        # Generate a unique message ID
    message_id = request.args.get("message_id")

    if not message_id:
        message_id = str(uuid.uuid4())


    # ------------------------------------------
    # 2. ECC Key Exchange
    # ------------------------------------------

    device_a_private, device_a_public = generate_ecc_key_pair()
    device_b_private, device_b_public = generate_ecc_key_pair()

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


    # ------------------------------------------
    # 3. Derive AES Session Key
    # ------------------------------------------

    device_a_key = derive_session_key(
        device_a_shared
    )

    device_b_key = derive_session_key(
        device_b_shared
    )


    # ------------------------------------------
    # 4. Convert sensor data to JSON
    # ------------------------------------------

    sensor_json = json.dumps(sensor_data)


    # ------------------------------------------
    # 5. AES-256-GCM Encryption
    # ------------------------------------------

    nonce, ciphertext = encrypt_data(
        device_a_key,
        sensor_json
    )
    log_security_event(
    "AES_ENCRYPTION",
    "SUCCESS",
    "Sensor data encrypted using AES-256-GCM"
)


    # ------------------------------------------
    # 6. Secure transmission
    # ------------------------------------------

    transmitted_ciphertext = ciphertext
    transmitted_nonce = nonce


    # ------------------------------------------
    # 7. Decryption
    # ------------------------------------------

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
        # ------------------------------------------
    # 7.1 Replay Attack Detection
    # ------------------------------------------

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


    # ------------------------------------------
    # 8. Store sensor data in SQLite
    # ------------------------------------------

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


    # ------------------------------------------
    # 9. Send response
    # ------------------------------------------

    return jsonify({
    "success": True,

    "message_id": message_id,

    "device": sensor_data,
        "security": {
            "ecc_key_exchange": "SUCCESS",
            "aes_encryption": "SUCCESS",
            "data_decryption": "SUCCESS"
        },

        "encrypted_data": ciphertext.hex(),

        "received_data": received_data,

        "database": "Sensor data stored successfully"
    })
@app.route("/api/sensor/history")
def sensor_history():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM sensor_data
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    sensor_history = []

    for row in rows:
        sensor_history.append({
            "id": row["id"],
            "device_id": row["device_id"],
            "temperature": row["temperature"],
            "humidity": row["humidity"],
            "timestamp": row["timestamp"],
            "status": row["status"]
        })

    return jsonify({
        "success": True,
        "count": len(sensor_history),
        "data": sensor_history
    })
@app.route("/api/device/status")
def device_status():

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
            "aes_256_gcm": "ACTIVE"
        }
    })
@app.route("/api/security/logs")
def security_logs():

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

        # Derive AES session key
        session_key = derive_session_key(shared_secret)

        # Original IoT data
        test_data = "IOT-001|Temperature:28.5|Humidity:60"

        # Encrypt
        nonce, ciphertext = encrypt_data(
            session_key,
            test_data
        )

        # Simulate attacker modifying ciphertext
        tampered_ciphertext = bytearray(ciphertext)
        tampered_ciphertext[0] ^= 1

        # Try to decrypt modified data
        decrypt_data(
            session_key,
            nonce,
            bytes(tampered_ciphertext)
        )

        return jsonify({
            "success": False,
            "message": "Tampering was not detected"
        }), 500

    except Exception:

        log_security_event(
            "TAMPERING_ATTACK",
            "BLOCKED",
            "Modified ciphertext rejected by AES-256-GCM authentication"
        )

        return jsonify({
            "success": True,
            "message": "Tampering detected and blocked",
            "security": {
                "integrity_protection": "BLOCKED",
                "algorithm": "AES-256-GCM"
            }
        }), 200

if __name__ == "__main__":
    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )