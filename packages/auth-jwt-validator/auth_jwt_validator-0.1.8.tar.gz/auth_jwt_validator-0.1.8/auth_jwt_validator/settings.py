# jwt_auth_validator/settings.py

class Settings:
    def __init__(self):
        self._domain = None
        self._jwks_path = "/.well-known/jwks.json"
        self._cache_ttl_seconds = 300  # default: 5 minutes

    @property
    def domain(self) -> str:
        if not self._domain:
            raise ValueError("DOMAIN is not set. Use `configure(domain)` to set it.")
        return self._domain

    @property
    def jwks_url(self) -> str:
        return f"{self.domain}{self._jwks_path}"

    @property
    def cache_ttl(self) -> int:
        return self._cache_ttl_seconds

    def set_domain(self, domain: str):
        domain = domain.rstrip("/")
        self._domain = domain

    def set_cache_ttl(self, ttl_seconds: int):
        if ttl_seconds <= 0:
            raise ValueError("Cache TTL must be a positive integer.")
        self._cache_ttl_seconds = ttl_seconds


# Singleton instance
settings = Settings()