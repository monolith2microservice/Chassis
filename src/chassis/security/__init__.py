from ..routers import raise_and_log_error
from fastapi import (
    Depends, 
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials, 
    HTTPBearer
)
from typing import (
    Callable, 
    Optional,
)
import jwt
import logging

Bearer = HTTPBearer()

def create_jwt_verifier(
        public_key: Callable[[], Optional[str]],
        logger: logging.Logger,
        algorithm: str = "RS256"
):

    def verify_token(credentials: HTTPAuthorizationCredentials = Depends(Bearer)):
        try:
            current_key = public_key()  # get latest value dynamically
            if not current_key:
                raise_and_log_error(
                    logger,
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    "Public key not loaded yet"
                )
            normalized_key = normalize_public_key(current_key)
            payload = jwt.decode(
                credentials.credentials,
                normalized_key,
                algorithms=[algorithm]
            )
            return payload

        except jwt.InvalidTokenError as e:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"Invalid token: {e}")

        except Exception as e:
            raise_and_log_error(logger, status.HTTP_500_INTERNAL_SERVER_ERROR, f"Internal error: {e}")

    return verify_token

def normalize_public_key(key: str) -> str:
    if '\n' in key:
        return key
    
    # Remover los headers si existen en la cadena
    key = key.replace('-----BEGIN PUBLIC KEY-----', '')
    key = key.replace('-----END PUBLIC KEY-----', '')
    key = key.strip()
    
    # Reconstruir con el formato correcto
    return f"-----BEGIN PUBLIC KEY-----\n{key}\n-----END PUBLIC KEY-----"