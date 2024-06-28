import pyotp


class MFAMixin:
    """MFA mixin."""

    def create_mfa_secret(self) -> str:
        """Generate a random MFA key."""
        return pyotp.random_base32()

    def get_totp(self, mfa_secret: str) -> str:
        """Return string TOTP key for currenct moment and defined mfa_secret."""
        totp = pyotp.TOTP(mfa_secret)
        return totp.now()
