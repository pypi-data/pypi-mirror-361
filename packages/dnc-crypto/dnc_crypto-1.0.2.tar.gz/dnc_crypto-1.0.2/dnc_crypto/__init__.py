from .core import ChainedEncryptor
from .key_manager import generate_key_file, load_key_from_file
from .exceptions import DNCCryptoError, DecryptionError, KeyManagementError

__version__ = "1.1.0" # افزایش نسخه به دلیل افزودن ویژگی جدید
__author__ = "Your Name"

class DNCCrypto:
    def __init__(self, key_path: str):
        self._key = load_key_from_file(key_path)
        self._engine = ChainedEncryptor(self._key)

    @staticmethod
    def generate_key(key_path: str, key_size_bits: int = 256):
        generate_key_file(key_path, key_size_bits)

    def encrypt(self, plaintext: bytes) -> bytes:
        if not isinstance(plaintext, bytes):
            raise TypeError("Plaintext must be of type bytes.")
        return self._engine.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        if not isinstance(ciphertext, bytes):
            raise TypeError("Ciphertext must be of type bytes.")
        try:
            return self._engine.decrypt(ciphertext)
        except (ValueError, IndexError) as e:
            raise DecryptionError(
                "Decryption failed. The data may be corrupt or the key is incorrect."
            ) from e