# jwt_auth_validator/exceptions.py

class JWTValidationError(Exception):
    """Raised when JWT validation fails (e.g. expired, invalid signature, etc.)"""
    pass


class PermissionDeniedError(Exception):
    """Raised when the user does not have the required permission"""
    pass


class PublicKeyFetchError(Exception):
    """Raised when fetching the public key fails (network issues, invalid response, etc.)"""
    pass


class JWKSNotAvailableError(Exception):
    """Raised when JWKS endpoint returns empty or malformed keys"""
    pass


class InvalidTokenStructureError(Exception):
    """Raised when token does not follow the expected JWT structure"""
    pass