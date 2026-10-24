"""
TITAN Common API Schemas
Standardized error structures and pagination envelopes.
"""

from typing import Generic, List, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    loc: Optional[List[str]] = None
    msg: str
    type: str


class ErrorResponse(BaseModel):
    error: str = Field(..., description="High-level error code or name")
    message: str = Field(..., description="Human-readable explanation of error")
    status_code: int = Field(..., description="HTTP status code")
    correlation_id: Optional[str] = Field(None, description="Request correlation identifier for tracing")
    details: Optional[List[ErrorDetail]] = Field(None, description="Granular field validation errors")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
