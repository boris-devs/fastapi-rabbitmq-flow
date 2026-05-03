import argon2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

ph = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using a secure hashing algorithm.

    This function provides a mechanism to securely hash passwords, which
    can be used for user authentication systems. The resulting hash is
    non-reversible and designed specifically for secure storage of
    passwords.

    :param password: The plain text password to hash.
    :return: A hashed version of the provided password.
    """
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plain text password matches its hashed counterpart. This function compares a given
    plain text password with a pre-hashed password and confirms whether they correspond. If the
    hashed password does not match the plain text password or if an error occurs during the
    verification, the function will return False. Otherwise, it will return True.

    :param plain_password: The plain text password to be verified.
    :type plain_password: str
    :param hashed_password: The hashed password to compare against.
    :type hashed_password: str
    :return: True if the plain text password matches the hashed password, False otherwise.
    :rtype: bool
    """
    try:
        return ph.verify(hashed_password, plain_password)

    except VerifyMismatchError:
        return False
    except(VerificationError, InvalidHashError):
        return False
