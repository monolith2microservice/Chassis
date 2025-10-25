# microservice_chassis/security/jwt_utils.py
import jwt
import logging

logger = logging.getLogger(__name__)

PUBLIC_KEY_PATH = "/tmp/keys/public.pem"
ALGORITHM = "RS256"


def verify_jwt(token: str, require_admin: bool = False):
    """
    Verify JWT using RS256 algorithm and stored public key.
    Returns the decoded payload if valid, or raises Exception otherwise.
    """
    try:
        with open(PUBLIC_KEY_PATH, "r") as f:
            public_key = f.read()

        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        logger.debug(f"JWT verified successfully for user_id={payload.get('sub')}")

        user_role = payload.get("role")
        if require_admin and user_role != "admin":
            logger.warning(f"Access denied: user_role={user_role} (admin required)")
            raise Exception("User does not have admin privileges")

        return payload

    except FileNotFoundError:
        logger.error(f"Public key not found at {PUBLIC_KEY_PATH}")
        raise Exception("Public key not found")
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise Exception("Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise Exception("Invalid token")
