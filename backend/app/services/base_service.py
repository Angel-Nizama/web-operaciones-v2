from typing import Any, Dict, List, Optional, Type, TypeVar
from app import db
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar('T')

class BaseService:
    """Servicio base con operaciones CRUD comunes"""
    
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        """Obtiene una entidad por su ID"""
        return self.model.query.get(id)

    def get_all(self) -> List[T]:
        """Obtiene todas las entidades"""
        return self.model.query.all()

    def create(self, data: Dict[str, Any]) -> T:
        """Crea una nueva entidad"""
        try:
            instance = self.model(**data)
            db.session.add(instance)
            db.session.commit()
            return instance
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """Actualiza una entidad existente"""
        try:
            instance = self.get_by_id(id)
            if instance:
                for key, value in data.items():
                    setattr(instance, key, value)
                db.session.commit()
            return instance
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def delete(self, id: int) -> bool:
        """Elimina una entidad"""
        try:
            instance = self.get_by_id(id)
            if instance:
                db.session.delete(instance)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e