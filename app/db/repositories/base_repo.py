"""
Base Repository Pattern
"""
from typing import Generic, TypeVar, Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Repository de base pour CRUD operations"""
    
    def __init__(self, db: Session, model_class):
        self.db = db
        self.model_class = model_class
    
    def create(self, db_obj: ModelType) -> ModelType:
        """Crée un nouvel objet"""
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Récupère par ID"""
        return self.db.query(self.model_class).filter(self.model_class.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Récupère tous les enregistrements"""
        return self.db.query(self.model_class).offset(skip).limit(limit).all()
    
    def update(self, id: UUID, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Met à jour un objet"""
        db_obj = self.get_by_id(id)
        if db_obj:
            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: UUID) -> bool:
        """Supprime un objet"""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
