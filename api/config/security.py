__all__ = ["access_token_exp", "refresh_token_exp", "allowed_origins"]

from datetime import timedelta

from .__base import HOST_URL, HOST_PORT, FRONTEND_HOST

access_token_exp = timedelta(days=30)
refresh_token_exp = timedelta(days=1)

allowed_origins = [
    f"http://{HOST_URL}",
    f"http://{HOST_URL}:{HOST_PORT}",
    f"http://{FRONTEND_HOST}",
    f"http://{FRONTEND_HOST}:{HOST_PORT}",
    f"https://{HOST_URL}",
    f"https://{HOST_URL}:{HOST_PORT}",
    f"https://{FRONTEND_HOST}",
    f"https://{FRONTEND_HOST}:{HOST_PORT}",
]