from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


def generate_ecc_key_pair():
    """
    Generate an ECC private key and corresponding public key.
    """
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    return private_key, public_key


def generate_shared_secret(private_key, peer_public_key):
    """
    Generate a shared secret using ECDH.
    """
    shared_secret = private_key.exchange(
        ec.ECDH(),
        peer_public_key
    )

    return shared_secret


def derive_session_key(shared_secret):
    """
    Derive a 256-bit AES session key from the ECC shared secret.
    """
    session_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"SecureIoT AES Session Key"
    ).derive(shared_secret)

    return session_key


if __name__ == "__main__":

    print("======================================")
    print("   Secure IoT - ECC Key Exchange")
    print("======================================")

    # Device A generates ECC key pair
    device_a_private, device_a_public = generate_ecc_key_pair()

    # Device B generates ECC key pair
    device_b_private, device_b_public = generate_ecc_key_pair()

    print("\n[1] ECC key pairs generated successfully.")

    # Exchange public keys and generate shared secrets
    device_a_shared_secret = generate_shared_secret(
        device_a_private,
        device_b_public
    )

    device_b_shared_secret = generate_shared_secret(
        device_b_private,
        device_a_public
    )

    print("[2] Shared secrets generated.")

    # Check whether both devices generated the same secret
    if device_a_shared_secret == device_b_shared_secret:
        print("[3] SUCCESS: Both devices generated the same shared secret.")
    else:
        print("[3] ERROR: Shared secrets do not match.")

    # Convert shared secret into AES session key
    device_a_session_key = derive_session_key(
        device_a_shared_secret
    )

    device_b_session_key = derive_session_key(
        device_b_shared_secret
    )

    print("[4] AES session keys derived using HKDF.")

    # Verify AES session keys
    if device_a_session_key == device_b_session_key:
        print("[5] SUCCESS: AES session keys match.")
    else:
        print("[5] ERROR: AES session keys do not match.")

    print("\nECC key exchange test completed successfully.")