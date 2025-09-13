from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from typing import Optional, List
from fastapi import HTTPException, status
from uuid import UUID


class NoteService:
    """
    Service for handling note CRUD operations
    """
    
    @staticmethod
    async def create_note(db: AsyncSession, note_data: NoteCreate, user_id: UUID) -> Note:
        """
        Create a new note for the authenticated user
        
        Args:
            db: Database session
            note_data: Note creation data
            user_id: ID of the authenticated user (UUID)
            
        Returns:
            Note: Created note object
        """
        db_note = Note(
            title=note_data.title,
            content=note_data.content,
            is_favorite=note_data.is_favorite,
            user_id=user_id
        )
        
        db.add(db_note)
        await db.commit()
        await db.refresh(db_note)
        return db_note
    
    @staticmethod
    async def get_notes(
        db: AsyncSession, 
        user_id: UUID, 
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Note], int]:
        """
        Get notes for the authenticated user with optional search
        
        Args:
            db: Database session
            user_id: ID of the authenticated user (UUID)
            search: Optional search term for title/content
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            tuple: (List of notes, Total count)
        """
        # Base query for user's notes
        query = select(Note).where(Note.user_id == user_id)
        
        # Add search filter if provided
        if search:
            search_filter = or_(
                Note.title.ilike(f"%{search}%"),
                Note.content.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Note.updated_at.desc()).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        notes = result.scalars().all()
        
        return list(notes), total
    
    @staticmethod
    async def get_note_by_id(db: AsyncSession, note_id: UUID, user_id: UUID) -> Optional[Note]:
        """
        Get a specific note by ID, ensuring it belongs to the authenticated user
        
        Args:
            db: Database session
            note_id: ID of the note to retrieve
            user_id: ID of the authenticated user (UUID)
            
        Returns:
            Optional[Note]: Note object if found and belongs to user, None otherwise
        """
        query = select(Note).where(
            and_(Note.id == note_id, Note.user_id == user_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_note(
        db: AsyncSession, 
        note_id: UUID, 
        note_data: NoteUpdate, 
        user_id: UUID
    ) -> Optional[Note]:
        """
        Update a note, ensuring it belongs to the authenticated user
        
        Args:
            db: Database session
            note_id: ID of the note to update
            note_data: Note update data
            user_id: ID of the authenticated user (UUID)
            
        Returns:
            Optional[Note]: Updated note object if successful, None if not found
            
        Raises:
            HTTPException: If note doesn't belong to user
        """
        # Get the note and verify ownership
        note = await NoteService.get_note_by_id(db, note_id, user_id)
        if not note:
            return None
        
        # Update fields that were provided
        update_data = note_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(note, field, value)
        
        await db.commit()
        await db.refresh(note)
        return note
    
    @staticmethod
    async def delete_note(db: AsyncSession, note_id: UUID, user_id: UUID) -> bool:
        """
        Delete a note, ensuring it belongs to the authenticated user
        
        Args:
            db: Database session
            note_id: ID of the note to delete
            user_id: ID of the authenticated user (UUID)
            
        Returns:
            bool: True if deleted successfully, False if not found
        """
        # Get the note and verify ownership
        note = await NoteService.get_note_by_id(db, note_id, user_id)
        if not note:
            return False
        
        await db.delete(note)
        await db.commit()
        return True
