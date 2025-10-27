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
    """
    Normaliza una clave pública en cualquier formato al formato PEM correcto.
    Maneja:
    - Claves en una sola línea
    - Claves con \n literales
    - Claves ya correctamente formateadas
    """
    # Reemplazar \n literales por saltos de línea reales
    key = key.replace('\\n', '\n')
    
    # Remover espacios en blanco extras
    key = key.strip()
    
    # Si ya tiene el formato correcto (múltiples líneas con headers), devolverla
    if key.startswith('-----BEGIN') and '\n' in key and key.count('\n') > 2:
        return key
    
    # Extraer solo el contenido de la clave (sin headers)
    key = key.replace('-----BEGIN PUBLIC KEY-----', '')
    key = key.replace('-----END PUBLIC KEY-----', '')
    key = key.replace('\n', '')  # Remover todos los saltos de línea
    key = key.strip()
    
    # Reconstruir con el formato correcto
    # La clave debe tener saltos de línea cada 64 caracteres (estándar PEM)
    lines = [key[i:i+64] for i in range(0, len(key), 64)]
    formatted_key = '\n'.join(lines)
    
    return f"-----BEGIN PUBLIC KEY-----\n{formatted_key}\n-----END PUBLIC KEY-----"