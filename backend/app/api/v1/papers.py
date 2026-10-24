"""Paper discovery routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.integrations.metadata import PaperSearchProvider
from app.schemas.papers import PaperSearchResponse

router = APIRouter(prefix="/papers", tags=["papers"])

MAX_QUERY_LENGTH = 300
MAX_PAGE = 10_000
MAX_PAGE_SIZE = 50
MAX_PROVIDER_OFFSET = 10_000


def _validation_error(field: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request contains invalid parameters.",
                "details": [{"field": field, "message": message}],
            }
        },
    )


def get_paper_search_provider() -> PaperSearchProvider:
    """Construct the configured provider without making a network request."""
    from app.integrations.openalex import OpenAlexPaperSearchProvider

    return OpenAlexPaperSearchProvider()


@router.get("/search", response_model=PaperSearchResponse)
async def search_papers(
    q: Annotated[
        str,
        Query(
            min_length=1,
            max_length=MAX_QUERY_LENGTH,
            description="Non-blank research topic or keyword query.",
        ),
    ],
    page: Annotated[int, Query(ge=1, le=MAX_PAGE)] = 1,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = 20,
    provider: PaperSearchProvider = Depends(get_paper_search_provider),
) -> PaperSearchResponse:
    """Return a paginated, provider-attributed search without persisting results."""
    query = q.strip()
    if not query:
        return _validation_error("q", "Query must not be blank.")
    if (page - 1) * page_size >= MAX_PROVIDER_OFFSET:
        return _validation_error(
            "page", "The provider's basic paging limit has been reached. Refine the query."
        )
    return await provider.search(query, page, page_size)
