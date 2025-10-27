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
            print(current_key)
            if not current_key:
                raise_and_log_error(
                    logger,
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    "Public key not loaded yet"
                )

            payload = jwt.decode(
                credentials.credentials,
                current_key,
                algorithms=[algorithm]
            )
            return payload

        except jwt.InvalidTokenError:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, "Invalid token")

        except Exception as e:
            raise_and_log_error(logger, status.HTTP_500_INTERNAL_SERVER_ERROR, f"Internal error: {e}")

    return verify_token