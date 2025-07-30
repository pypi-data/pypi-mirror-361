# jwt_auth_validator/decorators/graphql.py

from functools import wraps
from auth_jwt_validator.validators.jwt_validator import validate_jwt_token
from auth_jwt_validator.exceptions import PermissionDeniedError
from graphql import GraphQLError


def graphql_jwt_required(required_permission: list[str] = None):
    def decorator(resolve_func):
        @wraps(resolve_func)
        def wrapper(parent, info, *args, **kwargs):
            request = info.context
            auth_header = request.META.get("HTTP_AUTHORIZATION")

            if not auth_header or not auth_header.startswith("Bearer "):
                raise GraphQLError("Authorization header missing or malformed.")

            token = auth_header.split("Bearer ")[1]

            try:
                payload = validate_jwt_token(token, required_permission)
                request.user_id = payload.get("user_id")
                request.user_permissions = payload.get("permissions", [])
            except PermissionDeniedError as e:
                raise GraphQLError(str(e))
            except Exception as e:
                raise GraphQLError("Invalid token.")

            return resolve_func(parent, info, *args, **kwargs)

        return wrapper
    return decorator