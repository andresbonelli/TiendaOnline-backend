__all__ = ["access_token_exp", "refresh_token_exp", "allowed_origins"]

from datetime import timedelta

access_token_exp = timedelta(days=1)
refresh_token_exp = timedelta(days=30)

allowed_origins = [
    # "*",
    "http://localhost",
    "http://localhost:8080",
]