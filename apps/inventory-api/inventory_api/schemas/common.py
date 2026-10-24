"""
TITAN Common API Schemas
Standardized error structures and pagination envelopes.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    loc: list[str] | None = None
    msg: str
    type: str


class ErrorResponse(BaseModel):
    error: str = Field(..., description="High-level error code or name")
    message: str = Field(..., description="Human-readable explanation of error")
    status_code: int = Field(..., description="HTTP status code")
    correlation_id: str | None = Field(None, description="Request correlation identifier for tracing")
    details: list[ErrorDetail] | None = Field(None, description="Granular field validation errors")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
