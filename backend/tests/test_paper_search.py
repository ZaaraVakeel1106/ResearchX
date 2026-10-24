import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

import app.integrations.openalex as openalex_module
from app.core.config import Settings
from app.integrations.metadata import (
    MetadataProviderRateLimited,
    MetadataProviderUnavailable,
)
from app.integrations.openalex import OpenAlexPaperSearchProvider
from app.main import app
from app.schemas.papers import PaperSearchResponse, SearchPagination
from app.api.v1.papers import get_paper_search_provider


def settings(**overrides) -> Settings:
    return Settings(
        _env_file=None,
        openalex_base_url="https://api.openalex.org",
        **overrides,
    )


def openalex_payload(work: dict | None = None) -> dict:
    return {
        "meta": {"count": 1, "page": 1, "per_page": 20},
        "results": [
            work
            or {
                "id": "https://openalex.org/W123",
                "title": "A connected research example",
                "authorships": [
                    {
                        "author": {
                            "id": "https://openalex.org/A123",
                            "display_name": "Ada Researcher",
                        }
                    }
                ],
                "publication_year": 2024,
                "publication_date": "2024-04-10",
                "doi": "https://doi.org/10.1234/example",
                "abstract_inverted_index": {
                    "ideas": [3],
                    "Research": [0],
                    "connect": [1],
                    "and": [2],
                },
                "primary_location": {
                    "landing_page_url": "https://journal.example/paper",
                    "source": {"display_name": "Research Journal"},
                },
                "best_oa_location": {
                    "landing_page_url": "https://repository.example/paper",
                    "pdf_url": "https://repository.example/paper.pdf",
                },
                "open_access": {"is_oa": True},
                "cited_by_count": 18,
            }
        ],
    }


def test_openalex_response_maps_to_provider_neutral_schema() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["authorization"] = request.headers.get("Authorization")
        return httpx.Response(200, json=openalex_payload())

    provider = OpenAlexPaperSearchProvider(
        settings(openalex_api_key="test-only-key"),
        transport=httpx.MockTransport(handler),
    )
    response = asyncio.run(provider.search("graph theory", 1, 20))
    paper = response.items[0]

    assert paper.provider_id == "https://openalex.org/W123"
    assert paper.provider_url == "https://openalex.org/W123"
    assert paper.title == "A connected research example"
    assert [author.model_dump() for author in paper.authors] == [
        {"provider_id": "https://openalex.org/A123", "display_name": "Ada Researcher"}
    ]
    assert paper.publication_year == 2024
    assert paper.publication_date.isoformat() == "2024-04-10"
    assert paper.venue == "Research Journal"
    assert paper.doi == "10.1234/example"
    assert paper.abstract == "Research connect and ideas"
    assert paper.landing_page_url == "https://journal.example/paper"
    assert paper.open_access_status == "open_access"
    assert paper.open_access_url == "https://repository.example/paper"
    assert paper.citation_count == 18
    assert paper.metadata_provenance.provider == "openalex"
    assert response.pagination.total == 1
    assert response.pagination.has_more is False
    assert seen["authorization"] == "Bearer test-only-key"
    assert "test-only-key" not in seen["url"]


def test_openalex_missing_optional_fields_stay_null() -> None:
    provider = OpenAlexPaperSearchProvider(
        settings(),
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(
                200, json=openalex_payload({"id": "https://openalex.org/W456"})
            )
        ),
    )

    paper = asyncio.run(provider.search("sparse metadata", 1, 20)).items[0]

    assert paper.provider_id == "https://openalex.org/W456"
    assert paper.title is None
    assert paper.authors is None
    assert paper.publication_year is None
    assert paper.venue is None
    assert paper.doi is None
    assert paper.abstract is None
    assert paper.landing_page_url is None
    assert paper.open_access_status is None
    assert paper.citation_count is None


@pytest.mark.parametrize(
    "abstract_index",
    [
        {"first": [0], "wrong": [0]},
        {"first": [0], "third": [2]},
        {"first": [-1]},
    ],
)
def test_openalex_does_not_reconstruct_invalid_abstract_index(abstract_index: dict) -> None:
    provider = OpenAlexPaperSearchProvider(
        settings(),
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(
                200,
                json=openalex_payload(
                    {
                        "id": "https://openalex.org/W456",
                        "abstract_inverted_index": abstract_index,
                    }
                ),
            )
        ),
    )

    paper = asyncio.run(provider.search("topic", 1, 20)).items[0]

    assert paper.abstract is None


def test_openalex_rejects_malformed_response() -> None:
    provider = OpenAlexPaperSearchProvider(
        settings(),
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, json={"results": "bad"})),
    )

    with pytest.raises(MetadataProviderUnavailable):
        asyncio.run(provider.search("topic", 1, 20))


@pytest.mark.parametrize(
    ("response", "expected_error"),
    [
        (httpx.Response(429), MetadataProviderRateLimited),
        (httpx.Response(401), MetadataProviderUnavailable),
        (httpx.Response(503), MetadataProviderUnavailable),
    ],
)
def test_openalex_maps_upstream_http_failures(response, expected_error) -> None:
    provider = OpenAlexPaperSearchProvider(
        settings(),
        transport=httpx.MockTransport(lambda _request: response),
    )

    with pytest.raises(expected_error):
        asyncio.run(provider.search("topic", 1, 20))


def test_openalex_maps_timeout_without_leaking_exception() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("private upstream detail")

    provider = OpenAlexPaperSearchProvider(
        settings(), transport=httpx.MockTransport(handler)
    )

    with pytest.raises(MetadataProviderUnavailable) as error:
        asyncio.run(provider.search("topic", 1, 20))

    assert "private upstream detail" not in str(error.value)


def test_openalex_enforces_total_request_deadline(monkeypatch) -> None:
    class SlowTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, _request: httpx.Request) -> httpx.Response:
            await asyncio.sleep(0.05)
            return httpx.Response(200, json=openalex_payload())

    monkeypatch.setattr(openalex_module, "REQUEST_TOTAL_TIMEOUT_SECONDS", 0.001)
    provider = OpenAlexPaperSearchProvider(settings(), transport=SlowTransport())

    with pytest.raises(MetadataProviderUnavailable):
        asyncio.run(provider.search("topic", 1, 20))


def test_openalex_maps_network_error_without_leaking_exception() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("private connection detail")

    provider = OpenAlexPaperSearchProvider(
        settings(), transport=httpx.MockTransport(handler)
    )

    with pytest.raises(MetadataProviderUnavailable) as error:
        asyncio.run(provider.search("topic", 1, 20))

    assert "private connection detail" not in str(error.value)


def test_openalex_discards_non_web_landing_urls() -> None:
    provider = OpenAlexPaperSearchProvider(
        settings(),
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(
                200,
                json=openalex_payload(
                    {
                        "id": "https://openalex.org/W789",
                        "primary_location": {
                            "landing_page_url": "javascript:alert(1)",
                            "source": {"display_name": "Example Source"},
                        },
                    }
                ),
            )
        ),
    )

    paper = asyncio.run(provider.search("topic", 1, 20)).items[0]

    assert paper.provider_url == "https://openalex.org/W789"
    assert paper.landing_page_url is None


def test_openalex_pagination_discloses_basic_result_limit() -> None:
    works = [
        {"id": f"https://openalex.org/W{index}"}
        for index in range(50)
    ]
    provider = OpenAlexPaperSearchProvider(
        settings(),
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(
                200, json={"meta": {"count": 12_000}, "results": works}
            )
        ),
    )

    response = asyncio.run(provider.search("topic", 200, 50))

    assert response.pagination.total == 12_000
    assert response.pagination.has_more is False
    assert response.pagination.provider_limit_reached is True


class StubSearchProvider:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.query: str | None = None

    async def search(self, query: str, page: int, page_size: int) -> PaperSearchResponse:
        if self.error:
            raise self.error
        self.query = query
        return PaperSearchResponse(
            items=[],
            pagination=SearchPagination(
                page=page,
                page_size=page_size,
                total=0,
                has_more=False,
                provider_limit_reached=False,
            ),
        )


def test_search_endpoint_trims_query_and_returns_paginated_response() -> None:
    provider = StubSearchProvider()
    app.dependency_overrides[get_paper_search_provider] = lambda: provider
    try:
        response = TestClient(app).get(
            "/api/v1/papers/search?q=%20graph%20neural%20networks%20&page=2&page_size=10"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert provider.query == "graph neural networks"
    assert response.json() == {
        "items": [],
        "pagination": {
            "page": 2,
            "page_size": 10,
            "total": 0,
            "has_more": False,
            "provider_limit_reached": False,
        },
    }


def test_search_endpoint_rejects_pages_beyond_provider_offset_limit() -> None:
    provider = StubSearchProvider()
    app.dependency_overrides[get_paper_search_provider] = lambda: provider
    try:
        response = TestClient(app).get(
            "/api/v1/papers/search?q=topic&page=201&page_size=50"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["error"]["details"][0]["field"] == "page"
    assert provider.query is None


@pytest.mark.parametrize(
    "query",
    [
        "q=+++",
        f"q={'x' * 301}",
        "q=valid&page=0",
        "q=valid&page_size=51",
    ],
)
def test_search_endpoint_rejects_invalid_query_or_pagination(query: str) -> None:
    response = TestClient(app).get(f"/api/v1/papers/search?{query}")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize(
    ("provider_error", "status_code", "code"),
    [
        (MetadataProviderUnavailable("secret detail"), 502, "PROVIDER_UNAVAILABLE"),
        (MetadataProviderRateLimited("secret detail"), 503, "PROVIDER_RATE_LIMITED"),
    ],
)
def test_search_endpoint_returns_safe_provider_errors(
    provider_error: Exception, status_code: int, code: str
) -> None:
    app.dependency_overrides[get_paper_search_provider] = lambda: StubSearchProvider(
        provider_error
    )
    try:
        response = TestClient(app).get("/api/v1/papers/search?q=topic")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == status_code
    assert response.json()["error"]["code"] == code
    assert "secret detail" not in response.text
