from cryptography.fernet import Fernet
from app.config import get_config

config = get_config()
cipher_suite = Fernet(config.APP_FERNET_KEY)


class FernetMixin:

    @staticmethod
    def create_key() -> bytes:
        """Generate fernet key."""
        return Fernet.generate_key()

    def encrypt(self, value: str) -> str:
        """Encrypt string value."""
        encoded_text = cipher_suite.encrypt(str.encode(value))
        return encoded_text.decode()

    def decrypt(self, value: str) -> str:
        """Decrypt string value."""
        decoded_text = cipher_suite.decrypt(str.encode(value))
        return decoded_text.decode()
