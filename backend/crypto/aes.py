import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_data(session_key, plaintext):
    """
    Encrypt data using AES-256-GCM.
    """

    # Generate a unique 96-bit nonce
    nonce = os.urandom(12)

    aes = AESGCM(session_key)

    ciphertext = aes.encrypt(
        nonce,
        plaintext.encode("utf-8"),
        None
    )

    return nonce, ciphertext


def decrypt_data(session_key, nonce, ciphertext):
    """
    Decrypt AES-256-GCM encrypted data.
    """

    aes = AESGCM(session_key)

    plaintext = aes.decrypt(
        nonce,
        ciphertext,
        None
    )

    return plaintext.decode("utf-8")


if __name__ == "__main__":

    print("======================================")
    print("     Secure IoT - AES Encryption")
    print("======================================")

    # Generate a temporary AES-256 key for this standalone test
    session_key = AESGCM.generate_key(bit_length=256)

    # Simulated IoT sensor data
    sensor_data = (
        "Device ID: IOT-001 | "
        "Temperature: 28.4 C | "
        "Humidity: 63%"
    )

    print("\nOriginal IoT Data:")
    print(sensor_data)

    # Encrypt
    nonce, ciphertext = encrypt_data(
        session_key,
        sensor_data
    )

    print("\nEncrypted Data:")
    print(ciphertext.hex())

    # Decrypt
    decrypted_data = decrypt_data(
        session_key,
        nonce,
        ciphertext
    )

    print("\nDecrypted IoT Data:")
    print(decrypted_data)

    # Verify
    if decrypted_data == sensor_data:
        print("\nSUCCESS: AES encryption and decryption verified.")
    else:
        print("\nERROR: Decrypted data does not match.")