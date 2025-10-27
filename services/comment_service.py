from typing import List, Optional
from app import db
from models import Comentario
from repositories.comment_repository import CommentRepository

comment_repo = CommentRepository()


class CommentService:
    """Lógica de negocio para comentarios"""

    def get_comments_by_post(self, post_id: int) -> List[Comentario]:
        return comment_repo.get_by_post(post_id)

    def get_comment_by_id(self, comment_id: int) -> Optional[Comentario]:
        return comment_repo.get_by_id(comment_id)

    def create_comment(self, post_id: int, data: dict) -> Comentario:
        return comment_repo.create(post_id, data)

    def delete_comment(self, comment: Comentario) -> None:
        comment_repo.delete(comment)