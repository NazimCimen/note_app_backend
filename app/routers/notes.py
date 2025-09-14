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
    """
    Enum for specifying where to search in notes
    """
    BOTH = "both"         # Search in both title and content (default)
    TITLE = "title"       # Search only in title
    CONTENT = "content"   # Search only in content


class NoteFilter(str, Enum):
    """
    Enum for filtering notes by different criteria
    """
    ALL = "all"           # Tüm notlar (default)
    FAVORITES = "favorites"  # Sadece favoriler
    RECENT = "recent"     # Son eklenenler (7 gün)
    OLDEST = "oldest"     # En eskiler önce


class NoteSortBy(str, Enum):
    """
    Enum for sorting notes
    """
    UPDATED_DESC = "updated_desc"    # En son güncellenen (default)
    UPDATED_ASC = "updated_asc"      # En eski güncellenen
    CREATED_DESC = "created_desc"    # En son oluşturulan
    CREATED_ASC = "created_asc"      # En eski oluşturulan

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=NoteListResponse)
async def get_notes(
    search: Optional[str] = Query(None, description="Search term for notes"),
    search_in: SearchIn = Query(SearchIn.BOTH, description="Where to search: title, content, or both"),
    filter_by: NoteFilter = Query(NoteFilter.ALL, description="Filter notes by category"),
    sort_by: NoteSortBy = Query(NoteSortBy.UPDATED_DESC, description="Sort order for notes"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: UUID = Depends(get_current_user)
):
    """
    Get all notes for the authenticated user with optional search, filtering and pagination
    
    - **search**: Optional search term to filter notes (case-insensitive)
    - **search_in**: Where to search - 'both' (title and content), 'title' only, or 'content' only
    - **filter_by**: Filter notes by category - 'all', 'favorites', 'recent' (7 days), or 'oldest'
    - **sort_by**: Sort order - 'updated_desc', 'updated_asc', 'created_desc', or 'created_asc'
    - **page**: Page number for pagination (starts from 1)
    - **per_page**: Number of items per page (max 100)
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
    Create a new note for the authenticated user
    
    - **title**: Note title (required, max 255 characters)
    - **content**: Note content (required)
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
    Get a specific note by ID
    
    Only returns the note if it belongs to the authenticated user
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
    Update a specific note by ID
    
    Only allows updating if the note belongs to the authenticated user.
    You can update either title, content, or both.
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
    Delete a specific note by ID
    
    Only allows deletion if the note belongs to the authenticated user
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
