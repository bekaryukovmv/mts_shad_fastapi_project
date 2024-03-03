"""
A set of additional functions for working with passwords and tokens.
"""

import bcrypt
import jwt
from datetime import timedelta, datetime
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from .settings import settings
oauth_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")


def hashing_password(password: str):
    """
    A function for hashing the user's password.
    :param password: the password entered by the user.
    :return: hashed password in string format.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password=password.encode('utf-8'), salt=salt).decode('utf-8')


def validate_password(password: str, hashed_password: str):
    """
    A function for validating the user's password.
    :param password: the password entered by the user.
    :param hashed_password: hashed password from the vault.
    :return: the result of password validation. True or False.
    """
    return bcrypt.checkpw(password=password.encode('utf-8'), hashed_password=hashed_password.encode('utf-8'))


def encode_jwt(payload: dict,
               private_key: str = settings.private_key,
               algorithm: str = settings.algorithm,
               expire_minutes: int = settings.access_token_expire_minutes):
    """
    Function for creating a JWT token.
    :param payload: dictionary of useful user data.
    :param private_key: our private key from the settings.
    :param algorithm: the encryption algorithm.
    :param expire_minutes: token validity period.
    :return: JWT token in string format.
    """
    to_encode = payload.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now
    )
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(token: str | bytes,
               public_key: str = settings.public_key,
               algorithm: str = settings.algorithm):
    """
    A function for decoding an encrypted JWT token.
    :param token: the token passed by the user.
    :param public_key: our public key from the settings.
    :param algorithm: the encryption algorithm.
    :return: decoded dictionary of useful user data.
    """
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def validate_token(token: str = Depends(oauth_scheme)):
    """
    A function for validating the token received from the user.
    :param token: the received token.
    :return: the result of token validation.
    """
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token:{e}")

    user = payload.get("email")

    if user:
        return payload
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token")