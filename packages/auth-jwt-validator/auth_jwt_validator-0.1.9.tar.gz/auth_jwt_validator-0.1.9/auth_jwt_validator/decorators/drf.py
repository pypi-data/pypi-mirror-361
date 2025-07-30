from functools import wraps
from rest_framework.response import Response
from rest_framework import status

from auth_jwt_validator.validators.jwt_validator import JWTValidator, validate_jwt_token
from auth_jwt_validator.exceptions import JWTValidationError, PermissionDeniedError


def drf_jwt_required(required_permission: list[str] = None):
    """
        Decorator for checking JWT in DRF If required_permission is specified,
        it is checked whether the user has that permission or not.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                return Response({"detail": "Authorization header missing or invalid."},
                                status=status.HTTP_401_UNAUTHORIZED)

            jwt_token = token.split(" ")[1]

            # validator = JWTValidator()
            try:
                payload = validate_jwt_token(jwt_token, required_permission)
            except JWTValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            except PermissionDeniedError as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

            # attach user_id and permissions to request
            request.jwt_payload = payload
            request.user_id = payload.get("user_id")
            request.user_permissions = payload.get("permissions", [])

            return view_func(self, request, *args, **kwargs)

        return _wrapped_view

    return decorator