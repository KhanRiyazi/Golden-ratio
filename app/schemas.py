from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

# =========================================================
# Base Schema (Shared Fields)
# =========================================================
class LinkBase(BaseModel):
    title: str
    url: HttpUrl  # Stronger validation for valid URLs
    slug: Optional[str] = None


# =========================================================
# Create / Update Schemas
# =========================================================
class LinkCreate(LinkBase):
    """Schema for creating a new affiliate link."""
    pass


class LinkUpdate(BaseModel):
    """Schema for updating existing links."""
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    slug: Optional[str] = None


# =========================================================
# Click Schema
# =========================================================
class Click(BaseModel):
    id: int
    ip: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =========================================================
# Link Schema (Response)
# =========================================================
class Link(LinkBase):
    id: int
    created_at: datetime
    clicks: List[Click] = []  # Relationship (list of clicks)

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


# =========================================================
# Link Summary Schema (for Dashboard API)
# =========================================================
class LinkSummary(BaseModel):
    id: int
    title: str
    url: str
    slug: str
    click_count: int
    created_at: datetime

    class Config:
        from_attributes = True
