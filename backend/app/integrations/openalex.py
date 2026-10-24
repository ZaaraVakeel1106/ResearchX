"""OpenAlex Works search adapter."""

import asyncio
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

from app.core.config import Settings, settings
from app.integrations.metadata import (
    MetadataProviderRateLimited,
    MetadataProviderUnavailable,
)
from app.schemas.papers import (
    MetadataProvenance,
    PaperSearchAuthor,
    PaperSearchResponse,
    PaperSearchResult,
    SearchPagination,
)

REQUEST_TIMEOUT = httpx.Timeout(timeout=10.0, connect=3.0, read=7.0, write=3.0, pool=3.0)
REQUEST_TOTAL_TIMEOUT_SECONDS = 10.0
OPENALEX_BASIC_PAGING_LIMIT = 10_000


class _OpenAlexModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class _OpenAlexAuthor(_OpenAlexModel):
    id: str | None = None
    display_name: str | None = None


class _OpenAlexAuthorship(_OpenAlexModel):
    author: _OpenAlexAuthor | None = None


class _OpenAlexSource(_OpenAlexModel):
    display_name: str | None = None


class _OpenAlexLocation(_OpenAlexModel):
    landing_page_url: str | None = None
    pdf_url: str | None = None
    source: _OpenAlexSource | None = None


class _OpenAlexOpenAccess(_OpenAlexModel):
    is_oa: bool | None = None


class _OpenAlexWork(_OpenAlexModel):
    id: str
    title: str | None = None
    authorships: list[_OpenAlexAuthorship] | None = None
    publication_year: int | None = None
    publication_date: str | None = None
    doi: str | None = None
    abstract_inverted_index: dict[str, list[int]] | None = None
    primary_location: _OpenAlexLocation | None = None
    best_oa_location: _OpenAlexLocation | None = None
    open_access: _OpenAlexOpenAccess | None = None
    cited_by_count: int | None = None


class _OpenAlexMeta(_OpenAlexModel):
    count: int


class _OpenAlexSearchResponse(_OpenAlexModel):
    meta: _OpenAlexMeta
    results: list[_OpenAlexWork]


def _safe_web_url(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = urlsplit(value)
        if (
            parsed.scheme.lower() not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
        ):
            return None
    except ValueError:
        return None
    return value


def _openalex_record_url(value: str) -> str | None:
    safe_url = _safe_web_url(value)
    if safe_url is None:
        return None
    try:
        parsed = urlsplit(safe_url)
        if parsed.scheme == "https" and parsed.hostname == "openalex.org":
            return safe_url
    except ValueError:
        return None
    return None


def _decode_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    if not inverted_index:
        return None
    words_by_position: dict[int, str] = {}
    for word, positions in inverted_index.items():
        for position in positions:
            # Do not silently join a corrupt or incomplete index into text that
            # looks like a complete abstract.
            if position < 0 or position in words_by_position:
                return None
            words_by_position[position] = word
    if not words_by_position or set(words_by_position) != set(range(len(words_by_position))):
        return None
    return " ".join(words_by_position[position] for position in sorted(words_by_position)) or None


def _normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "http://dx.doi.org/"):
        if normalized.lower().startswith(prefix):
            return normalized[len(prefix) :] or None
    return normalized or None


def _map_work(work: _OpenAlexWork, retrieved_at: datetime) -> PaperSearchResult:
    provider_id = work.id.strip()
    if not provider_id:
        raise ValueError("OpenAlex work is missing its identifier")

    primary_location = work.primary_location
    best_oa_location = work.best_oa_location
    source = primary_location.source if primary_location else None
    open_access_value = work.open_access.is_oa if work.open_access else None
    open_access_url = None
    if open_access_value is True and best_oa_location:
        open_access_url = _safe_web_url(
            best_oa_location.landing_page_url or best_oa_location.pdf_url
        )

    authors = None
    if work.authorships is not None:
        authors = [
            PaperSearchAuthor(
                provider_id=authorship.author.id if authorship.author else None,
                display_name=(
                    authorship.author.display_name if authorship.author else None
                ),
            )
            for authorship in work.authorships
        ]

    return PaperSearchResult(
        provider_id=provider_id,
        provider_url=_openalex_record_url(provider_id),
        title=work.title,
        authors=authors,
        publication_year=work.publication_year,
        publication_date=work.publication_date,
        venue=source.display_name if source else None,
        doi=_normalize_doi(work.doi),
        abstract=_decode_abstract(work.abstract_inverted_index),
        landing_page_url=(
            _safe_web_url(primary_location.landing_page_url)
            if primary_location
            else None
        ),
        open_access_status=(
            "open_access"
            if open_access_value is True
            else "not_marked_open_access"
            if open_access_value is False
            else None
        ),
        open_access_url=open_access_url,
        citation_count=work.cited_by_count,
        metadata_provenance=MetadataProvenance(
            provider="openalex", retrieved_at=retrieved_at
        ),
    )


class OpenAlexPaperSearchProvider:
    """Search OpenAlex and normalize records into the Research X API contract."""

    def __init__(
        self,
        config: Settings = settings,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._config = config
        self._transport = transport

    async def search(
        self, query: str, page: int, page_size: int
    ) -> PaperSearchResponse:
        headers = {"Accept": "application/json"}
        if self._config.openalex_api_key:
            headers["Authorization"] = (
                f"Bearer {self._config.openalex_api_key.get_secret_value()}"
            )
        base_url = str(self._config.openalex_base_url).rstrip("/")

        try:
            async with asyncio.timeout(REQUEST_TOTAL_TIMEOUT_SECONDS):
                async with httpx.AsyncClient(
                    timeout=REQUEST_TIMEOUT,
                    transport=self._transport,
                    headers=headers,
                    follow_redirects=False,
                ) as client:
                    response = await client.get(
                        f"{base_url}/works",
                        params={"search": query, "page": page, "per_page": page_size},
                    )
        except TimeoutError as error:
            raise MetadataProviderUnavailable from error
        except httpx.TimeoutException as error:
            raise MetadataProviderUnavailable from error
        except httpx.RequestError as error:
            raise MetadataProviderUnavailable from error

        if response.status_code == 429:
            raise MetadataProviderRateLimited
        if not response.is_success:
            raise MetadataProviderUnavailable

        try:
            payload: Any = response.json()
            upstream = _OpenAlexSearchResponse.model_validate(payload)
            retrieved_at = datetime.now(timezone.utc)
            items = [_map_work(work, retrieved_at) for work in upstream.results]
        except (ValueError, ValidationError) as error:
            raise MetadataProviderUnavailable from error

        return PaperSearchResponse(
            items=items,
            pagination=SearchPagination(
                page=page,
                page_size=page_size,
                total=upstream.meta.count,
                has_more=(
                    (page - 1) * page_size + len(items) < upstream.meta.count
                    and (page - 1) * page_size + len(items)
                    < OPENALEX_BASIC_PAGING_LIMIT
                ),
                provider_limit_reached=(
                    upstream.meta.count > OPENALEX_BASIC_PAGING_LIMIT
                    and (page - 1) * page_size + len(items)
                    >= OPENALEX_BASIC_PAGING_LIMIT
                ),
            ),
        )
