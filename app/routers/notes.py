from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from enum import Enum

from app.database import get_db
from app.middleware.auth import get_current_user
from app.services.note import NoteService
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse


class SearchIn(str, Enum):
    """Search scope options"""
    BOTH = "both"
    TITLE = "title"
    CONTENT = "content"


class NoteFilter(str, Enum):
    """Note filtering options"""
    ALL = "all"
    FAVORITES = "favorites"


class NoteSort(str, Enum):
    """Note sorting options"""
    NEWEST = "newest"
    OLDEST = "oldest"

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=NoteListResponse)
async def get_notes(
    search: Optional[str] = Query(None, description="Search term"),
    search_in: SearchIn = Query(SearchIn.BOTH, description="Search scope"),
    filter_by: NoteFilter = Query(NoteFilter.ALL, description="Filter type"),
    sort_by: NoteSort = Query(NoteSort.NEWEST, description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Get notes with search, filtering and pagination
    """
    skip = (page - 1) * per_page
    
    notes, total = await NoteService.get_notes(
        db=db,
        user_id=current_user,
        search=search,
        search_in=search_in.value,
        filter_by=filter_by.value,
        sort_by=sort_by.value,
        skip=skip,
        limit=per_page
    )
    
    return NoteListResponse(
        notes=notes,
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Create a new note
    """
    note = await NoteService.create_note(
        db=db,
        note_data=note_data,
        user_id=current_user
    )
    
    return note


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Get note by ID
    """
    note = await NoteService.get_note_by_id(
        db=db,
        note_id=note_id,
        user_id=current_user
    )
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or you don't have permission to access it"
        )
    
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Update note by ID
    """
    note = await NoteService.update_note(
        db=db,
        note_id=note_id,
        note_data=note_data,
        user_id=current_user
    )
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or you don't have permission to update it"
        )
    
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Delete note by ID
    """
    deleted = await NoteService.delete_note(
        db=db,
        note_id=note_id,
        user_id=current_user
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or you don't have permission to delete it"
        )
    
    return None
