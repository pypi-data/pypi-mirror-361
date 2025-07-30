# jwt_auth_validator/validators/jwt_validator.py

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from .jwks_fetcher import JWKSFetcher
from ..utils.cache import Cache
from ..exceptions import JWTValidationError, PermissionDeniedError, InvalidTokenStructureError

class JWTValidator:
    def __init__(self, jwks_url: str, cache_ttl: int = 300, required_permissions: list[str]=None):
        self.jwks_fetcher = JWKSFetcher(jwks_url)
        self.cache = Cache(cache_ttl)
        self.required_permissions = required_permissions or []

    def _get_public_key(self) -> str:
        """ Get public key from cache or fetch from service """
        public_key = self.cache.get("public_key")
        if not public_key:
            public_key = self.jwks_fetcher.fetch_public_key()
            self.cache.set("public_key", public_key)
        return public_key

    def validate_token(self, token: str) -> dict:
        """ Validates the JWT token and returns the relevant information. """
        try:
            public_key = self._get_public_key()
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                options={"verify_aud": False}  
            )

            # Check permissions in payload (if roles or permissions are in payload)
            self._validate_permissions(payload)

            return payload

        except ExpiredSignatureError:
            raise JWTValidationError("JWT has expired.")
        except InvalidTokenError:
            raise JWTValidationError("Invalid JWT.")
        except Exception as e:
            raise InvalidTokenStructureError(f"Invalid token structure: {str(e)}")

    def _validate_permissions(self, payload: dict):
        """Checking whether the user has the necessary permissions or not"""
        permissions = payload.get("permissions", [])
        required_permissions = self._get_required_permissions()  

        if not required_permissions:
            return  # No permissions required for this view; allow access

        if not any(p in permissions for p in required_permissions):
            raise PermissionDeniedError(
                f"User lacks required permissions. Needs at least one of: {required_permissions}"
            )
    def _get_required_permissions(self) -> list:
        return self.required_permissions

        
# Helper function for decorators
def validate_jwt_token(token: str, required_permission: list[str]=None) -> dict:
    from ..settings import settings  # avoid circular imports

    validator = JWTValidator(settings.jwks_url, settings.cache_ttl, required_permission)
    payload = validator.validate_token(token)

    # if required_permission and required_permission not in payload.get("permissions", []):
    #     raise PermissionDeniedError(f"User lacks required permission: {required_permission}")

    return payload