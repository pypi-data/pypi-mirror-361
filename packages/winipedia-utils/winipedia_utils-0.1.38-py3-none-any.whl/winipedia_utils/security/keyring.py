"""Keyring utilities for secure storage and retrieval of secrets.

This module provides utility functions for working with keyring,
including getting and creating secrets and fernets.
These utilities help with secure storage and retrieval of secrets.
"""

from collections.abc import Callable

import keyring
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def get_or_create_fernet(service_name: str, username: str) -> Fernet:
    """Get the app secret using keyring.

    If it does not exist, create it with a Fernet.
    """
    return get_or_create_key(
        service_name, username, Fernet, lambda: Fernet.generate_key()
    )


def get_or_create_aes_gcm(service_name: str, username: str) -> AESGCM:
    """Get the app secret using keyring.

    If it does not exist, create it with a AESGCM.
    """
    return get_or_create_key(
        service_name, username, AESGCM, lambda: AESGCM.generate_key(bit_length=256)
    )


def get_or_create_key[T](
    service_name: str,
    username: str,
    key_class: Callable[[bytes], T],
    generate_key_func: Callable[..., bytes],
) -> T:
    """Get the app secret using keyring.

    If it does not exist, create it with the generate_func.
    """
    service_name = f"{service_name}_{key_class.__name__}"
    secret = keyring.get_password(service_name, username)
    if secret is None:
        secret = generate_key_func().decode()
        keyring.set_password(service_name, username, secret)

    return key_class(secret.encode())
