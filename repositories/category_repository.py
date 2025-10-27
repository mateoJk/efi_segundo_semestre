from app import db
from models import Categoria

class CategoryRepository:
    """Acceso a datos para categorías"""

    @staticmethod
    def get_all():
        """Devuelve todas las categorías"""
        return Categoria.query.order_by(Categoria.nombre.asc()).all()

    @staticmethod
    def get_by_id(category_id: int):
        """Obtiene una categoría por id"""
        return Categoria.query.get(category_id)

    @staticmethod
    def create(nombre: str):
        """Crea una nueva categoría"""
        nueva = Categoria(nombre=nombre)
        db.session.add(nueva)
        db.session.commit()
        db.session.refresh(nueva)
        return nueva

    @staticmethod
    def update(category: Categoria, nombre: str):
        """Actualiza una categoría existente"""
        category.nombre = nombre
        db.session.commit()
        db.session.refresh(category)
        return category

    @staticmethod
    def delete(category: Categoria):
        """Elimina una categoría"""
        db.session.delete(category)
        db.session.commit()