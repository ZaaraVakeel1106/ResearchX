"""Public API error response contract."""

from pydantic import BaseModel, Field


class APIErrorDetail(BaseModel):
    field: str
    message: str


class APIError(BaseModel):
    code: str
    message: str
    details: list[APIErrorDetail] = Field(default_factory=list)


class APIErrorResponse(BaseModel):
    error: APIError
