from cryptography.exceptions import InvalidTag

from crypto.ecc import (
    generate_ecc_key_pair,
    generate_shared_secret,
    derive_session_key
)

from crypto.aes import encrypt_data, decrypt_data


print("==============================================")
print("       AES-256-GCM Tampering Test")
print("==============================================")


# ------------------------------------------
# STEP 1: Generate ECC key pairs
# ------------------------------------------

device_a_private, device_a_public = generate_ecc_key_pair()
device_b_private, device_b_public = generate_ecc_key_pair()

print("\n[1] ECC key pairs generated.")


# ------------------------------------------
# STEP 2: Generate shared secrets
# ------------------------------------------

shared_a = generate_shared_secret(
    device_a_private,
    device_b_public
)

shared_b = generate_shared_secret(
    device_b_private,
    device_a_public
)


# ------------------------------------------
# STEP 3: Derive AES session keys
# ------------------------------------------

key_a = derive_session_key(shared_a)
key_b = derive_session_key(shared_b)

print("[2] AES session keys established.")


# ------------------------------------------
# STEP 4: Encrypt IoT data
# ------------------------------------------

message = "Temperature: 28.5 C | Humidity: 65%"

nonce, ciphertext = encrypt_data(
    key_a,
    message
)

print("[3] IoT data encrypted successfully.")


# ------------------------------------------
# STEP 5: Modify encrypted data
# ------------------------------------------

tampered_ciphertext = bytearray(ciphertext)

tampered_ciphertext[0] ^= 1

tampered_ciphertext = bytes(tampered_ciphertext)

print("[4] Encrypted data has been modified.")


# ------------------------------------------
# STEP 6: Attempt decryption
# ------------------------------------------

try:

    decrypt_data(
        key_b,
        nonce,
        tampered_ciphertext
    )

    print("\nERROR: Tampered data was accepted.")

except InvalidTag:

    print("\nSUCCESS: Tampering detected!")
    print("AES-256-GCM rejected the modified ciphertext.")

print("\n==============================================")
print("       Security Test Completed")
print("==============================================")