from crypto.ecc import (
    generate_ecc_key_pair,
    generate_shared_secret,
    derive_session_key
)

from crypto.aes import (
    encrypt_data,
    decrypt_data
)


print("================================================")
print("     SECURE IoT COMMUNICATION TEST")
print("          ECC + AES-256-GCM")
print("================================================")


# ------------------------------------------------
# STEP 1: Generate ECC key pairs
# ------------------------------------------------

print("\n[1] Generating ECC key pairs...")

device_a_private, device_a_public = generate_ecc_key_pair()
device_b_private, device_b_public = generate_ecc_key_pair()

print("    Device A ECC keys generated.")
print("    Device B ECC keys generated.")


# ------------------------------------------------
# STEP 2: Exchange public keys
# ------------------------------------------------

print("\n[2] Exchanging public keys...")

device_a_shared_secret = generate_shared_secret(
    device_a_private,
    device_b_public
)

device_b_shared_secret = generate_shared_secret(
    device_b_private,
    device_a_public
)

print("    Public keys exchanged.")


# ------------------------------------------------
# STEP 3: Verify shared secret
# ------------------------------------------------

print("\n[3] Verifying shared secret...")

if device_a_shared_secret == device_b_shared_secret:
    print("    SUCCESS: Both devices generated the same shared secret.")
else:
    print("    ERROR: Shared secrets do not match.")
    exit()


# ------------------------------------------------
# STEP 4: Derive AES session keys
# ------------------------------------------------

print("\n[4] Deriving AES-256 session keys...")

device_a_session_key = derive_session_key(
    device_a_shared_secret
)

device_b_session_key = derive_session_key(
    device_b_shared_secret
)

if device_a_session_key == device_b_session_key:
    print("    SUCCESS: AES session keys match.")
else:
    print("    ERROR: AES session keys do not match.")
    exit()


# ------------------------------------------------
# STEP 5: Simulated IoT sensor data
# ------------------------------------------------

sensor_data = (
    "Device ID: IOT-001 | "
    "Temperature: 28.4 C | "
    "Humidity: 63%"
)

print("\n[5] Original IoT data:")
print("    " + sensor_data)


# ------------------------------------------------
# STEP 6: Device A encrypts data
# ------------------------------------------------

print("\n[6] Device A encrypting IoT data...")

nonce, ciphertext = encrypt_data(
    device_a_session_key,
    sensor_data
)

print("    Data encrypted successfully.")

print("\n    Encrypted data:")
print("    " + ciphertext.hex())


# ------------------------------------------------
# STEP 7: Simulated network transmission
# ------------------------------------------------

print("\n[7] Transmitting encrypted data...")
print("    Network received ciphertext.")
print("    Original sensor data is not transmitted directly.")


# ------------------------------------------------
# STEP 8: Device B decrypts data
# ------------------------------------------------

print("\n[8] Device B decrypting data...")

decrypted_data = decrypt_data(
    device_b_session_key,
    nonce,
    ciphertext
)

print("    Data decrypted successfully.")

print("\n    Decrypted IoT data:")
print("    " + decrypted_data)


# ------------------------------------------------
# STEP 9: Final verification
# ------------------------------------------------

print("\n[9] Final security verification...")

if decrypted_data == sensor_data:
    print("    SUCCESS: Original data recovered correctly.")
    print("    SUCCESS: Secure ECC + AES communication verified.")
else:
    print("    ERROR: Data verification failed.")


print("\n================================================")
print("       SECURE COMMUNICATION TEST COMPLETE")
print("================================================")