from ..routers import raise_and_log_error
from fastapi import (
    Depends, 
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials, 
    HTTPBearer
)
from typing import Optional
import jwt
import logging

Bearer = HTTPBearer()

def create_jwt_verifier(
        public_key: Optional[str],
        logger: logging.Logger,
        algorithm: str = "RS256"
):
    """
    Factory function to create a JWT verifier with a specific public key.
    """
    assert public_key is not None, "Public key should be set"
    def verify_token(credentials: HTTPAuthorizationCredentials = Depends(Bearer)):
        try:
            payload = jwt.decode(
                credentials.credentials,
                public_key,
                algorithms=[algorithm]
            )
            return payload
        except jwt.InvalidTokenError:
            raise_and_log_error(logger, status.HTTP_401_UNAUTHORIZED, "Invalid token")
        except Exception as e:
            raise_and_log_error(logger, status.HTTP_500_INTERNAL_SERVER_ERROR, f"Internal error: {e}")
    
    return verify_token