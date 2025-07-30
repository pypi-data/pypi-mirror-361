# auth_jwt_validator/drf/permissions.py

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from auth_jwt_validator.validators.jwt_validator import validate_jwt_token
from auth_jwt_validator.exceptions import JWTValidationError, PermissionDeniedError


class HasJWTAndPermissions(BasePermission):
    """
    DRF permission class to check JWT validity and required permissions.
    Add `required_permissions` list to your view class to specify required permissions.
    
    Example:
        class MyView(APIView):
            permission_classes = [HasJWTAndPermissions]
            required_permissions = ["read_user"]
    """

    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Authorization header missing or invalid.")

        token = auth_header.split(" ")[1]
        required_permissions = getattr(view, "required_permissions", None)

        try:
            payload = validate_jwt_token(token, required_permissions)
        except JWTValidationError as e:
            raise AuthenticationFailed(str(e))
        except PermissionDeniedError as e:
            raise PermissionDenied(str(e))

        # Attach useful info to request
        request.jwt_payload = payload
        request.user_id = payload.get("user_id")
        request.user_permissions = payload.get("permissions", [])

        return True