from repositories.post_repository import PostRepository
from repositories.comment_repository import CommentRepository
from repositories.category_repository import CategoryRepository
from models import Post, Comentario, Categoria

class StatsService:
    """Servicio para obtener estadísticas de la aplicación."""

    def __init__(self):
        self.post_repo = PostRepository()
        self.comment_repo = CommentRepository()
        self.category_repo = CategoryRepository()

    def get_stats(self) -> dict:
        """
        Devuelve estadísticas generales:
        - total_posts
        - total_comments
        - total_categories
        - posts_last_week (cantidad)
        """
        total_posts = self.post_repo.count_all(published_only=True)
        total_comments = len(self.comment_repo.get_all())
        total_categories = len(self.category_repo.get_all())
        posts_last_week = len(self.post_repo.get_posts_last_week())

        return {
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_categories": total_categories,
            "posts_last_week": posts_last_week
        }