"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.health import router as health_router
from app.api.v1.papers import router as papers_router
from app.core.config import settings
from app.integrations.metadata import (
    MetadataProviderRateLimited,
    MetadataProviderUnavailable,
)

app = FastAPI(title="Research X API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(papers_router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    _request: Request, error: RequestValidationError
) -> JSONResponse:
    """Return safe, consistent validation errors without echoing user input."""
    details = []
    for validation_error in error.errors():
        location = validation_error.get("loc", ())
        field = ".".join(str(part) for part in location if part not in {"query", "path"})
        details.append({"field": field or "request", "message": "Invalid value."})
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request contains invalid parameters.",
                "details": details,
            }
        },
    )


@app.exception_handler(MetadataProviderRateLimited)
async def provider_rate_limited_handler(
    _request: Request, _error: MetadataProviderRateLimited
) -> JSONResponse:
    """Report upstream throttling without disclosing provider internals."""
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "PROVIDER_RATE_LIMITED",
                "message": "The research provider is temporarily rate limiting requests.",
                "details": [],
            }
        },
    )


@app.exception_handler(MetadataProviderUnavailable)
async def provider_unavailable_handler(
    _request: Request, _error: MetadataProviderUnavailable
) -> JSONResponse:
    """Return a safe error when the upstream provider cannot be used."""
    return JSONResponse(
        status_code=502,
        content={
            "error": {
                "code": "PROVIDER_UNAVAILABLE",
                "message": "The research provider could not complete the search.",
                "details": [],
            }
        },
    )
