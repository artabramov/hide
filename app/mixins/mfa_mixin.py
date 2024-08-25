"""
Provides functionality for Multi-Factor Authentication (MFA) through
the MFAMixin class. Includes methods for generating MFA secrets and
creating Time-based One-Time Passwords (TOTP) using those secrets.
"""

import pyotp


class MFAMixin:
    """
    A mixin class for handling Multi-Factor Authentication (MFA)
    functionalities. Provides methods to generate MFA secrets and
    to generate Time-based One-Time Passwords (TOTP) based on those
    secrets.
    """

    def create_mfa_secret(self) -> str:
        """
        Generates a new MFA (Multi-Factor Authentication) secret in
        base32 format suitable for use with TOTP (Time-based One-Time
        Password) systems. Returns the secret as a string.
        """
        return pyotp.random_base32()

    def get_totp(self, mfa_secret: str) -> str:
        """
        Generates a TOTP (Time-based One-Time Password) using the
        provided MFA secret. Returns the generated TOTP as a string.
        """
        totp = pyotp.TOTP(mfa_secret)
        return totp.now()
