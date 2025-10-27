from typing import List, Optional
from repositories.category_repository import CategoryRepository
from models import Categoria

class CategoryService:
    """Lógica de negocio para categorías"""

    def __init__(self):
        self.repo = CategoryRepository()

    def get_all_categories(self) -> List[Categoria]:
        return self.repo.get_all()

    def get_category_by_id(self, category_id: int) -> Optional[Categoria]:
        return self.repo.get_by_id(category_id)

    def create_category(self, nombre: str) -> Categoria:
        return self.repo.create(nombre)

    def update_category(self, category: Categoria, nombre: str) -> Categoria:
        return self.repo.update(category, nombre)

    def delete_category(self, category: Categoria) -> None:
        self.repo.delete(category)