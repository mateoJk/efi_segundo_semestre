from typing import List, Optional
from repositories.post_repository import PostRepository
from models import Post
from decorators.auth_decorators import check_ownership_or_role


class PostService:
    """Servicio para la lógica de negocio de Posts."""

    def __init__(self):
        self.repo = PostRepository()

    def get_public_posts(self) -> List[Post]:
        """Devuelve todos los posts públicos."""
        return self.repo.get_all(published_only=True)

    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """Devuelve un post por id, sin importar estado de publicación."""
        return self.repo.get_by_id(post_id)

    def get_user_posts(self, user_id: int, published_only: bool = False) -> List[Post]:
        """Devuelve posts de un usuario."""
        return self.repo.get_by_user(user_id=user_id, published_only=published_only)

    def create_post(self, data: dict) -> Post:
        """Crea un post nuevo usando el repository."""
        return self.repo.create(data)

    def update_post(self, post: Post, data: dict) -> Optional[Post]:
        """Actualiza un post si el usuario es dueño o admin."""
        if not check_ownership_or_role(post.usuario_id):
            raise PermissionError("No tienes permiso para actualizar este post.")
        return self.repo.update(post, data)

    def delete_post(self, post: Post) -> None:
        """Elimina un post si el usuario es dueño o admin."""
        if not check_ownership_or_role(post.usuario_id):
            raise PermissionError("No tienes permiso para eliminar este post.")
        self.repo.delete(post)

    # ================= Estadísticas =================
    def count_posts(self, published_only: bool = True) -> int:
        return self.repo.count_all(published_only=published_only)

    def posts_last_week(self) -> List[Post]:
        return self.repo.get_posts_last_week()