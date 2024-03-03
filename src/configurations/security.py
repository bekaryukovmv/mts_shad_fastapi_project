import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from .settings import settings
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

oauth_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")


def hashing_password(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password=password.encode('utf-8'), salt=salt).decode('utf-8')


def validate_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password=password.encode('utf-8'), hashed_password=hashed_password.encode('utf-8'))


def encode_jwt(payload: dict,
               private_key: str = settings.private_key,
               algorithm: str = settings.algorithm,
               expire_minutes: int = settings.access_token_expire_minutes):
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
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def validate_token(token: str = Depends(oauth_scheme)):
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token:{e}")

    user = payload.get("email")

    if user:
        return payload
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token")

