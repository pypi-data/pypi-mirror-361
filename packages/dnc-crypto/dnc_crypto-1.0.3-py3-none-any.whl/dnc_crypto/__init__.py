import os
import json
import struct
import hmac
from .core import ChainedEncryptor
from .key_manager import generate_key_file, load_key_from_file
from .exceptions import DNCCryptoError, DecryptionError, KeyManagementError

__version__ = "2.0.0" # افزایش نسخه به دلیل تغییرات بزرگ در فرمت
__author__ = "Your Name"

class DNCCrypto:
    # --- ثابت‌های پروتکل صنعتی ---
    MAGIC_BYTES = b'DNCE'
    CURRENT_VERSION_TUPLE = (2, 0, 0)
    HEADER_FORMAT = "!4sH H" # Magic (4s), Version (H), HeaderLen (H)
    HMAC_KEY_SALT = b"dnc-hmac-integrity-key-salt"

    def __init__(self, key_path: str, num_chains: int = 8):
        self._key = load_key_from_file(key_path)
        self.num_chains = num_chains
        self._engine = ChainedEncryptor(self._key, num_chains=self.num_chains)
        
        # یک کلید مجزا برای HMAC از کلید اصلی مشتق می‌کنیم
        self._hmac_key = self._engine._derive_key(self.HMAC_KEY_SALT)

    @staticmethod
    def generate_key(key_path: str, key_size_bits: int = 256):
        generate_key_file(key_path, key_size_bits)

    def _create_header(self) -> bytes:
        """هدر JSON را ایجاد و به بایت تبدیل می‌کند."""
        header_data = {
            "key_size_bits": len(self._key) * 8,
            "num_chains": self.num_chains,
            "cipher_engine": "DNC-v1"
        }
        return json.dumps(header_data, separators=(',', ':')).encode('utf-8')

    def encrypt(self, plaintext: bytes) -> bytes:
        if not isinstance(plaintext, bytes):
            raise TypeError("Plaintext must be of type bytes.")
            
        ciphertext = self._engine.encrypt(plaintext)
        
        # 1. ساخت هدر
        header_json_bytes = self._create_header()
        
        # 2. ساخت بخش اولیه پاکت
        version_packed = (self.CURRENT_VERSION_TUPLE[0] << 8) | self.CURRENT_VERSION_TUPLE[1]
        packet_prefix = struct.pack(self.HEADER_FORMAT, self.MAGIC_BYTES, version_packed, len(header_json_bytes))
        
        # 3. محاسبه HMAC روی هدر
        header_hmac = hmac.new(self._hmac_key, packet_prefix + header_json_bytes, 'sha256').digest()
        
        # 4. الحاق تمام قطعات
        return packet_prefix + header_json_bytes + header_hmac + ciphertext

    def decrypt(self, data: bytes) -> bytes:
        if not isinstance(data, bytes):
            raise TypeError("Data to decrypt must be of type bytes.")
            
        try:
            # 1. استخراج بخش اولیه پاکت
            prefix_len = struct.calcsize(self.HEADER_FORMAT)
            if len(data) < prefix_len:
                raise DecryptionError("Data is too short to be a valid DNCCrypto payload.")
            
            magic, version_packed, header_len = struct.unpack(self.HEADER_FORMAT, data[:prefix_len])
            
            # 2. اعتبارسنجی Magic Bytes
            if magic != self.MAGIC_BYTES:
                raise DecryptionError("Invalid data format or not a DNCCrypto file (magic bytes mismatch).")
            
            # 3. استخراج و اعتبارسنجی هدر
            header_end = prefix_len + header_len
            hmac_end = header_end + 32
            if len(data) < hmac_end:
                raise DecryptionError("Data is truncated or corrupt (header/HMAC section).")
            
            header_json_bytes = data[prefix_len:header_end]
            received_hmac = data[header_end:hmac_end]
            
            # 4. اعتبارسنجی HMAC
            expected_hmac = hmac.new(self._hmac_key, data[:header_end], 'sha256').digest()
            if not hmac.compare_digest(received_hmac, expected_hmac):
                raise DecryptionError("Header integrity check failed! The file metadata may have been tampered with.")
            
            # 5. پارس کردن هدر و بررسی پارامترها
            header_data = json.loads(header_json_bytes)
            if header_data.get("key_size_bits") != len(self._key) * 8:
                raise DecryptionError(
                    f"Key size mismatch. File was encrypted with a {header_data.get('key_size_bits')}-bit key, "
                    f"but trying to decrypt with a {len(self._key) * 8}-bit key."
                )

            # 6. استخراج و رمزگشایی ciphertext
            ciphertext = data[hmac_end:]
            return self._engine.decrypt(ciphertext)
            
        except (struct.error, json.JSONDecodeError, ValueError, IndexError) as e:
            raise DecryptionError("Decryption failed due to corrupted data or incorrect format.") from e