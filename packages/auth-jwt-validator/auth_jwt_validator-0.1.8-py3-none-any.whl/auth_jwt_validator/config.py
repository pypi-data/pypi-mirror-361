from .settings import settings

def configure(domain: str, cache_ttl: int = 300):
    """
    Configure the JWT Auth Validator package.

    Args:
        domain (str): Base domain for your user_service, e.g., "https://auth.myapp.com"
        cache_ttl (int): Optional - cache lifetime in seconds (default: 300)
    """
    settings.set_domain(domain)
    settings.set_cache_ttl(cache_ttl)