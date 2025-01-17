from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status

load_dotenv()

class AuthHandler:
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY')
        self.algorithm = os.getenv('ALGORITHM')
        self.access_token_expire = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
        self.refresh_token_expire = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')) * 24 * 7

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.refresh_token_expire)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )