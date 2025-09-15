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
    Note CRUD operations service
    """
    
    @staticmethod
    async def create_note(db: AsyncSession, note_data: NoteCreate, user_id: UUID) -> Note:
        """
        Create a new note
        """
        db_note = Note(
            title=note_data.title,
            content=note_data.content,
            is_favorite=note_data.is_favorite,
            user_id=user_id,
            summary=note_data.summary,
            keywords=note_data.keywords
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
        search_in: str = "both",
        filter_by: str = "all",
        sort_by: str = "newest",
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Note], int]:
        """
        Get notes with search, filtering and sorting
        """
        # Base query
        query = select(Note).where(Note.user_id == user_id)
        
        # Apply filters
        if filter_by == "favorites":
            query = query.where(Note.is_favorite == True)
        
        # Apply search
        if search:
            if search_in == "title":
                search_filter = Note.title.ilike(f"%{search}%")
            elif search_in == "content":
                search_filter = Note.content.ilike(f"%{search}%")
            else:  # both
                search_filter = or_(
                    Note.title.ilike(f"%{search}%"),
                    Note.content.ilike(f"%{search}%")
                )
            query = query.where(search_filter)
        
        # Apply sorting
        if sort_by == "newest":
            query = query.order_by(Note.updated_at.desc())
        elif sort_by == "oldest":
            query = query.order_by(Note.updated_at.asc())
        else:
            query = query.order_by(Note.updated_at.desc())
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        notes = result.scalars().all()
        
        return list(notes), total
    
    @staticmethod
    async def get_note_by_id(db: AsyncSession, note_id: UUID, user_id: UUID) -> Optional[Note]:
        """
        Get note by ID (user-specific)
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
        Update note (user-specific)
        """
        note = await NoteService.get_note_by_id(db, note_id, user_id)
        if not note:
            return None
        
        # Update provided fields
        update_data = note_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(note, field, value)
        
        await db.commit()
        await db.refresh(note)
        return note
    
    @staticmethod
    async def delete_note(db: AsyncSession, note_id: UUID, user_id: UUID) -> bool:
        """
        Delete note (user-specific)
        """
        note = await NoteService.get_note_by_id(db, note_id, user_id)
        if not note:
            return False
        
        await db.delete(note)
        await db.commit()
        return True
