import base64
from cryptography.hazmat.primitives.asymmetric import ec

def generate_vapid_keys():
    # Generate an Elliptic Curve private key (P-256 is required for Web Push)
    private_key = ec.generate_private_key(ec.SECP256R1())
    
    # Get the private value (d)
    private_numbers = private_key.private_numbers()
    d_bytes = private_numbers.private_value.to_bytes(32, byteorder='big')
    # Encode as URL-safe base64 without padding
    private_key_b64 = base64.urlsafe_b64encode(d_bytes).decode('utf-8').rstrip('=')
    
    # Get the public numbers (x and y)
    public_key = private_key.public_key()
    public_numbers = public_key.public_numbers()
    
    # The public key format for Web Push is an uncompressed point starting with 0x04
    x_bytes = public_numbers.x.to_bytes(32, byteorder='big')
    y_bytes = public_numbers.y.to_bytes(32, byteorder='big')
    public_key_bytes = b'\x04' + x_bytes + y_bytes
    
    # Encode as URL-safe base64 without padding
    public_key_b64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')
    
    print("VAPID Keys geradas com sucesso!")
    print("-" * 50)
    print(f"VAPID_PUBLIC_KEY={public_key_b64}")
    print(f"VAPID_PRIVATE_KEY={private_key_b64}")
    print("-" * 50)
    print("Copie estas duas linhas e cole no seu arquivo .env na VPS (e/ou .env local)!")

if __name__ == "__main__":
    generate_vapid_keys()
