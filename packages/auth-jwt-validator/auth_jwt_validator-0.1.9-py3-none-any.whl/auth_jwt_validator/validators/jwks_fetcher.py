# jwt_auth_validator/validators/jwks_fetcher.py

import requests
import jwt
from jwt.algorithms import RSAAlgorithm
from ..settings import settings
from ..exceptions import JWKSNotAvailableError, PublicKeyFetchError


class JWKSFetcher:
    def __init__(self, jwks_url: str = None):
        self.jwks_url = jwks_url or settings.jwks_url

    def fetch_jwks(self) -> dict:
        try:
            response = requests.get(self.jwks_url, timeout=5)
            response.raise_for_status()
            jwks = response.json()
        except Exception as e:
            raise PublicKeyFetchError(f"Failed to fetch JWKS: {str(e)}")

        if "keys" not in jwks or not jwks["keys"]:
            raise JWKSNotAvailableError("JWKS endpoint returned empty or malformed keys.")

        return jwks

    def fetch_public_key(self) -> str:
        """ Takes JWKS and extracts public key for PyJWT """
        jwks = self.fetch_jwks()

        key_data = jwks["keys"][0]  # It is assumed that there is currently only one key in JWKS.
        try:
            public_key = RSAAlgorithm.from_jwk(key_data)
        except Exception as e:
            raise PublicKeyFetchError(f"Failed to parse public key from JWK: {str(e)}")

        return public_key