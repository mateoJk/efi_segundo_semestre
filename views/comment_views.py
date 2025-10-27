from flask import request, jsonify
from flask.views import MethodView
from decorators.auth_decorators import roles_required, active_user_required, check_ownership_or_role
from services.comment_service import CommentService
from schemas.comment_schemas import CommentCreateSchema

comment_service = CommentService()


class PostCommentsAPI(MethodView):
    """Endpoints para /api/posts/<id>/comments"""

    def get(self, post_id):
        """Listar comentarios de un post (público)"""
        comments = comment_service.get_comments_by_post(post_id)
        return jsonify([comment.to_dict() for comment in comments]), 200

    @roles_required("user", "moderator", "admin")
    @active_user_required
    def post(self, post_id):
        """Crear un comentario en un post"""
        data = request.get_json()
        schema = CommentCreateSchema()
        try:
            valid_data = schema.load(data)
        except Exception as err:
            return jsonify({"error": "Datos inválidos", "details": str(err)}), 400

        nuevo_comment = comment_service.create_comment(post_id, valid_data)
        return jsonify(nuevo_comment.to_dict()), 201


class CommentDeleteAPI(MethodView):
    """Eliminar comentario por id"""

    @roles_required("user", "moderator", "admin")
    @active_user_required
    def delete(self, comment_id):
        comment = comment_service.get_comment_by_id(comment_id)
        if not comment:
            return jsonify({"error": "Comentario no encontrado"}), 404

        # Solo autor, moderator o admin
        if not (check_ownership_or_role(comment.usuario_id) or
                self._is_moderator_or_admin()):
            return jsonify({"error": "No tienes permiso"}), 403

        comment_service.delete_comment(comment)
        return jsonify({"message": "Comentario eliminado correctamente"}), 200

    def _is_moderator_or_admin(self):
        from flask_jwt_extended import get_jwt
        role = get_jwt().get("role")
        return role in ("moderator", "admin")