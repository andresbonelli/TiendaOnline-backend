__all__ = ["access_token_exp", "refresh_token_exp", "allowed_origins"]

from datetime import timedelta

from .__base import HOST_URL, HOST_PORT, FRONTEND_HOST

access_token_exp = timedelta(minutes=60)
refresh_token_exp = timedelta(days=1)

allowed_origins = [
    "*",
    HOST_URL,
    f"{HOST_URL}:{HOST_PORT}",
    FRONTEND_HOST,
    f"{FRONTEND_HOST}:{HOST_PORT}",
]
