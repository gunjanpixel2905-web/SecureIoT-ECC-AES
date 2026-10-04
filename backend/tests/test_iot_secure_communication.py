import json

from crypto.ecc import (
    generate_ecc_key_pair,
    generate_shared_secret,
    derive_session_key
)

from crypto.aes import encrypt_data, decrypt_data

from devices.simulator import IoTDevice


print("==============================================")
print("   Secure IoT Communication System")
print("   ECC + AES-256-GCM")
print("==============================================")


# ------------------------------------------
# STEP 1: Create IoT Device
# ------------------------------------------

device = IoTDevice("IOT-001")

sensor_data = device.generate_sensor_data()

print("\n[1] IoT Sensor Data Generated:")
print(json.dumps(sensor_data, indent=4))


# ------------------------------------------
# STEP 2: ECC Key Pair Generation
# ------------------------------------------

device_a_private, device_a_public = generate_ecc_key_pair()
device_b_private, device_b_public = generate_ecc_key_pair()

print("\n[2] ECC key pairs generated successfully.")


# ------------------------------------------
# STEP 3: ECDH Shared Secret
# ------------------------------------------

device_a_shared_secret = generate_shared_secret(
    device_a_private,
    device_b_public
)

device_b_shared_secret = generate_shared_secret(
    device_b_private,
    device_a_public
)

if device_a_shared_secret == device_b_shared_secret:
    print("[3] SUCCESS: Shared secret matches.")
else:
    print("[3] ERROR: Shared secret does not match.")


# ------------------------------------------
# STEP 4: Derive AES Session Key
# ------------------------------------------

device_a_session_key = derive_session_key(
    device_a_shared_secret
)

device_b_session_key = derive_session_key(
    device_b_shared_secret
)

if device_a_session_key == device_b_session_key:
    print("[4] SUCCESS: AES session keys match.")
else:
    print("[4] ERROR: AES session keys do not match.")


# ------------------------------------------
# STEP 5: Convert Sensor Data to JSON
# ------------------------------------------

sensor_json = json.dumps(sensor_data)

print("\n[5] Sensor data prepared for transmission.")


# ------------------------------------------
# STEP 6: Encrypt IoT Data
# ------------------------------------------

nonce, ciphertext = encrypt_data(
    device_a_session_key,
    sensor_json
)

print("[6] SUCCESS: IoT data encrypted using AES-256-GCM.")

print("\nEncrypted Data:")
print(ciphertext.hex())


# ------------------------------------------
# STEP 7: Simulate Network Transmission
# ------------------------------------------

transmitted_ciphertext = ciphertext
transmitted_nonce = nonce

print("\n[7] Encrypted data transmitted securely.")


# ------------------------------------------
# STEP 8: Receiver Decrypts Data
# ------------------------------------------

decrypted_json = decrypt_data(
    device_b_session_key,
    transmitted_nonce,
    transmitted_ciphertext
)

received_data = json.loads(decrypted_json)

print("\n[8] Decrypted IoT Data:")
print(json.dumps(received_data, indent=4))


# ------------------------------------------
# STEP 9: Verify Communication
# ------------------------------------------

if received_data == sensor_data:
    print("\n==============================================")
    print("SUCCESS: Secure IoT communication verified!")
    print("ECC key exchange + AES encryption working.")
    print("==============================================")
else:
    print("\nERROR: Data integrity verification failed.")