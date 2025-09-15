from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class NoteBase(BaseModel):
    """
    Base note schema with common fields
    """
    title: str = Field(..., min_length=1, max_length=255, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    is_favorite: bool = Field(default=False, description="Whether the note is marked as favorite")
    summary: Optional[str] = Field(None, description="Note summary")
    keywords: Optional[str] = Field(None, description="Note keywords")


class NoteCreate(NoteBase):
    """
    Schema for creating a new note
    """
    pass


class NoteUpdate(BaseModel):
    """
    Schema for updating an existing note
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Note title")
    content: Optional[str] = Field(None, min_length=1, description="Note content")
    is_favorite: Optional[bool] = Field(None, description="Whether the note is marked as favorite")
    summary: Optional[str] = Field(None, description="Note summary")
    keywords: Optional[str] = Field(None, description="Note keywords")


class NoteResponse(NoteBase):
    """
    Schema for note response
    """
    id: UUID
    user_id: UUID  # User ID foreign key
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NoteListResponse(BaseModel):
    """
    Schema for note list response
    """
    notes: list[NoteResponse]
    total: int
    page: int = 1
    per_page: int = 10
