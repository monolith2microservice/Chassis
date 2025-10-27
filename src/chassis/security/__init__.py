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
        public_key_func: Callable[[], Optional[str]],
        logger: logging.Logger,
        algorithm: str = "RS256"
):
    def verify_token(credentials: HTTPAuthorizationCredentials = Depends(Bearer)):
        try:
            current_key = public_key_func()
            assert current_key is not None, "Public key must be set."
            payload = jwt.decode(
                credentials.credentials,
                current_key,
                algorithms=[algorithm]
            )
            return payload

        except jwt.InvalidTokenError as e:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, f"Invalid token: {e}")

        except Exception as e:
            raise_and_log_error(logger, status.HTTP_500_INTERNAL_SERVER_ERROR, f"Internal error: {e}")
    return verify_token