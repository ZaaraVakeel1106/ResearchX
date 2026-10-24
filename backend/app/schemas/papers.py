"""Provider-neutral paper search API contracts."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class PaperSearchAuthor(BaseModel):
    provider_id: str | None
    display_name: str | None


class MetadataProvenance(BaseModel):
    provider: str
    retrieved_at: datetime


class PaperSearchResult(BaseModel):
    provider_id: str
    provider_url: str | None
    title: str | None
    authors: list[PaperSearchAuthor] | None
    publication_year: int | None
    publication_date: date | None
    venue: str | None
    doi: str | None
    abstract: str | None
    landing_page_url: str | None
    open_access_status: Literal["open_access", "not_marked_open_access"] | None
    open_access_url: str | None
    citation_count: int | None
    metadata_provenance: MetadataProvenance


class SearchPagination(BaseModel):
    page: int
    page_size: int
    total: int
    has_more: bool
    provider_limit_reached: bool


class PaperSearchResponse(BaseModel):
    items: list[PaperSearchResult]
    pagination: SearchPagination
