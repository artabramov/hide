"""
Provides encryption and decryption utilities using the Fernet symmetric
encryption scheme from the cryptography library. Includes a mixin class
with methods for generating Fernet keys, and for encrypting and
decrypting strings, using a pre-configured Fernet key from the
application configuration.
"""

from cryptography.fernet import Fernet
from app.config import get_config

config = get_config()
cipher_suite = Fernet(config.FERNET_KEY)


class FernetMixin:
    """
    Provides methods for encryption and decryption using the Fernet
    symmetric encryption scheme. Includes functionality to generate a
    new Fernet key, encrypt a string, and decrypt an encrypted string.
    Utilizes a pre-configured Fernet key for encryption and decryption
    operations.
    """

    @staticmethod
    def generate_ferntet_key() -> bytes:
        """
        Generates a new Fernet encryption key suitable for use with the
        Fernet encryption scheme. Returns the key as a byte string.
        """
        return Fernet.generate_key()

    def encrypt(self, value: str) -> str:
        """
        Encrypts the given string using the Fernet encryption scheme.
        Returns the encrypted text as a string.
        """
        encoded_text = cipher_suite.encrypt(str.encode(value))
        return encoded_text.decode()

    def decrypt(self, value: str) -> str:
        """
        Decrypts the given encrypted string using the Fernet encryption
        scheme. Returns the decrypted text as a string.
        """
        decoded_text = cipher_suite.decrypt(str.encode(value))
        return decoded_text.decode()
