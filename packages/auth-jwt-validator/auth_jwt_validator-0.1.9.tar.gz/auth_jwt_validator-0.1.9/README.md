# auth_jwt_validator

A simple and secure JWT validation and permission checking package for DRF and GraphQL APIs.

---

## ✨ Features

- 🔐 Verifies JWT tokens using RS256 public keys.
- ⚙️ Supports dynamic domain configuration to fetch keys from `/.well-known/jwks.json`.
- ⚡ Internal caching of public keys to reduce HTTP calls.
- 🔎 Verifies `exp`, `iat`, and `kid` fields.
- 🔐 Extracts `permissions` and `user_id` from JWT.
- ✅ Validates required permissions.
- ✅ Works with DRF: APIView, GenericAPIView, ViewSet.
- ✅ Supports function-based DRF views.
- ✅ Supports GraphQL (Graphene).

---

## 📦 Installation

```bash
pip install auth_jwt_validator
```

---

## ⚙️ Configuration

Before using the validator, configure your auth domain in main settings.py:

```python
from auth_jwt_validator.settings import settings

# Set your user service domain dynamically
settings.set_domain("https://auth.myapp.com")
```

> You can also set custom cache TTL (default is 300 seconds):
>
> ```python
> configure("https://auth.myapp.com", cache_ttl=600)
> ```

---

## 🚀 Usage

### ✅ Option 1: DRF Permission Class (Recommended for class-based views)

Add to your `APIView`, `GenericAPIView`, or `ViewSet`:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from auth_jwt_validator.drf.permissions import HasJWTAndPermissions

class MyView(APIView):
    permission_classes = [HasJWTAndPermissions]
    required_permissions = ["read_profile"]

    def get(self, request):
        return Response({"user_id": request.user_id})
```

You can also use this with `GenericAPIView`:

```python
from rest_framework.generics import GenericAPIView

class MyGenericView(GenericAPIView):
    permission_classes = [HasJWTAndPermissions]
    required_permissions = ["read_profile"]

    def get(self, request):
        return Response({"user_id": request.user_id})
```

Or inside a `ViewSet`:

```python
from rest_framework.viewsets import ViewSet

class MyViewSet(ViewSet):
    permission_classes = [HasJWTAndPermissions]
    required_permissions = ["read_profile"]

    def retrieve(self, request, pk=None):
        return Response({"user_id": request.user_id, "profile_id": pk})
```

---

### ✅ Option 2: `drf_jwt_required` Decorator (for function-based views or custom method handling)

Use it for full control over the method:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from auth_jwt_validator.decorators.drf import drf_jwt_required

class MyView(APIView):
    @drf_jwt_required(["read_profile"])
    def get(self, request):
        return Response({"user_id": request.user_id})
```

> 🧠 Tip: This approach bypasses `permission_classes` and does everything inline.

#### ✅ With `GenericAPIView`
```python
from rest_framework.generics import GenericAPIView

class MyGenericView(GenericAPIView):
    @drf_jwt_required(["read_profile"])
    def get(self, request, *args, **kwargs):
        return Response({"user_id": request.user_id})
```

#### ✅ With `ViewSet`
```python
from rest_framework.viewsets import ViewSet

class MyViewSet(ViewSet):
    @drf_jwt_required(["read_profile"])
    def retrieve(self, request, pk=None):
        return Response({"user_id": request.user_id, "profile_id": pk})
```

> ⚠️ Only use `drf_jwt_required` when you need per-method control and don’t want to use `permission_classes`.

---

## 🧪 GraphQL Usage (Graphene)

Add the decorator to your GraphQL resolvers:

```python
import graphene
from auth_jwt_validator.decorators.graphql import graphql_jwt_required

class Query(graphene.ObjectType):
    me = graphene.String()

    @graphql_jwt_required(["read_profile"])
    def resolve_me(self, info):
        user_id = info.context.user_id
        return f"Hello user {user_id}"
```

---

## 🔐 JWT Payload Format

JWTs should contain at minimum:

```json
{
  "user_id": "123",
  "permissions": ["read_profile", "edit_profile"],
  "exp": 1712345678,
  "iat": 1712340000,
  "iss": "auth.myapp.com"
}
```

---

## 🛠 Internals

### `validate_jwt_token(token: str, required_permissions: list[str] | None)`
- Validates signature using public key (with `kid`)
- Checks `exp`, `iat`, and `iss`
- Raises:
  - `JWTValidationError`
  - `PermissionDeniedError`

---

## 💡 Best Practices

- Use `permission_classes = [HasJWTAndPermissions]` for most DRF views.
- Use `drf_jwt_required` only for function-based views or fine-grained control.
- Always call `configure(...)` once at app startup.
- Ensure `/.well-known/jwks.json` is exposed in your user service.

---

## 🤝 Contributing
Pull requests welcome!

---

## 📄 License
MIT

