from app import db
from models import Comentario
from flask_jwt_extended import get_jwt_identity

class CommentRepository:

    @staticmethod
    def get_by_post(post_id: int):
        return Comentario.query.filter_by(post_id=post_id, is_visible=True).all()

    @staticmethod
    def get_by_id(comment_id: int):
        return Comentario.query.get(comment_id)

    @staticmethod
    def create(post_id: int, data: dict):
        nuevo = Comentario(
            contenido=data["contenido"],
            post_id=post_id,
            usuario_id = get_jwt_identity()
        )
        db.session.add(nuevo)
        db.session.commit()
        db.session.refresh(nuevo)
        return nuevo

    @staticmethod
    def delete(comment):
        db.session.delete(comment)
        db.session.commit()

    @staticmethod
    def get_all():
        """Devuelve todos los comentarios visibles."""
        return Comentario.query.filter_by(is_visible=True).all()