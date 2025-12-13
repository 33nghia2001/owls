"""
Generate RSA Key Pair for JWT RS256
===================================
Run this script to generate private/public keys for JWT authentication.
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import os


def generate_rsa_keys(key_size: int = 2048):
    """Generate RSA key pair."""
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    
    # Get private key in PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Get public key in PEM format
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem


def main():
    # Create keys directory
    keys_dir = Path(__file__).parent / 'keys'
    keys_dir.mkdir(exist_ok=True)
    
    # Generate keys
    print("Generating RSA key pair (2048 bits)...")
    private_pem, public_pem = generate_rsa_keys()
    
    # Save private key
    private_key_path = keys_dir / 'private.pem'
    with open(private_key_path, 'wb') as f:
        f.write(private_pem)
    print(f"✓ Private key saved to: {private_key_path}")
    
    # Save public key
    public_key_path = keys_dir / 'public.pem'
    with open(public_key_path, 'wb') as f:
        f.write(public_pem)
    print(f"✓ Public key saved to: {public_key_path}")
    
    # Print instructions
    print("\n" + "="*60)
    print("IMPORTANT: Add 'keys/' to your .gitignore!")
    print("="*60)
    print("\nFor .env file, add:")
    print(f"JWT_PRIVATE_KEY_PATH={private_key_path}")
    print(f"JWT_PUBLIC_KEY_PATH={public_key_path}")
    print("\nOr copy the keys directly to .env:")
    print("\nJWT_PRIVATE_KEY=\"\"\"")
    print(private_pem.decode())
    print("\"\"\"")
    print("\nJWT_PUBLIC_KEY=\"\"\"")
    print(public_pem.decode())
    print("\"\"\"")


if __name__ == '__main__':
    main()
