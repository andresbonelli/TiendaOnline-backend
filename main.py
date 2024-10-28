import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from .api.config import allowed_origins, APP_TITLE
from .api.routes import api_router, auth_router

app = FastAPI(title=APP_TITLE)

# Include our API routes
app.include_router(api_router)
# Include our auth routes aside from the API routes
app.include_router(auth_router)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        name="index.html", request=request, context=dict(title=APP_TITLE)
    )


# logging.basicConfig(level=logging.DEBUG)
@app.middleware("http")
async def log_request_data(request: Request, call_next):
    # Log incoming request details
    logging.info(f"Incoming request: {request.method} {request.url}")

    # Log headers (including cookies)
    for key, value in request.headers.items():
        logging.debug(f"Header {key}: {value}")

    response = await call_next(request)

    # Log outgoing response details
    logging.info(f"Response status: {response.status_code}")
    return response
