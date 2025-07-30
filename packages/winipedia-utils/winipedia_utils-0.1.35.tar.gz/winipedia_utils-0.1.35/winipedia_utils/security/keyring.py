"""Keyring utilities for secure storage and retrieval of secrets.

This module provides utility functions for working with keyring,
including getting and creating secrets and fernets.
These utilities help with secure storage and retrieval of secrets.
"""

import keyring
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def get_or_create_fernet(service_name: str, username: str) -> Fernet:
    """Get the app secret using keyring.

    If it does not exist, create it with a Fernet.
    """
    secret = keyring.get_password(service_name, username)
    if secret is None:
        secret = Fernet.generate_key().decode()
        keyring.set_password(service_name, username, secret)
    return Fernet(secret.encode())


def get_or_create_aes_gcm(service_name: str, username: str) -> AESGCM:
    """Get the app secret using keyring.

    If it does not exist, create it with a AESGCM.
    """
    secret = keyring.get_password(service_name, username)
    if secret is None:
        secret = AESGCM.generate_key(bit_length=256).decode()
        keyring.set_password(service_name, username, secret)
    return AESGCM(secret.encode())
