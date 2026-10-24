"""Provider-neutral metadata integration contracts and errors."""

from typing import Protocol

from app.schemas.papers import PaperSearchResponse


class PaperSearchProvider(Protocol):
    """An academic metadata provider that can search papers."""

    async def search(
        self, query: str, page: int, page_size: int
    ) -> PaperSearchResponse: ...


class MetadataProviderUnavailable(RuntimeError):
    """Raised when an upstream metadata provider cannot serve a request."""


class MetadataProviderRateLimited(MetadataProviderUnavailable):
    """Raised when the upstream metadata provider rate limits Research X."""
