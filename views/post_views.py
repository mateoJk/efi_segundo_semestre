from flask import request, jsonify
from flask.views import MethodView

from services.post_service import PostService
from schemas.post_schemas import PostCreateSchema, PostUpdateSchema, PostSchema
from decorators.auth_decorators import roles_required, active_user_required

post_service = PostService()


class PostsAPI(MethodView):
    """Endpoints para /api/posts"""

    def get(self):
        """Listar todos los posts públicos"""
        posts = post_service.get_public_posts()
        schema = PostSchema(many=True)
        return jsonify(schema.dump(posts)), 200

    @roles_required("user", "moderator", "admin")
    @active_user_required
    def post(self):
        """Crear un nuevo post"""
        data = request.get_json()
        schema = PostCreateSchema()
        try:
            valid_data = schema.load(data)
        except Exception as err:
            return jsonify({"error": "Datos inválidos", "details": str(err)}), 400

        nuevo_post = post_service.create_post(valid_data)
        return jsonify(PostSchema().dump(nuevo_post)), 201


class PostDetailAPI(MethodView):
    """Endpoints para /api/posts/<id>"""

    def get(self, post_id):
        """Obtener un post específico"""
        post = post_service.get_post_by_id(post_id)
        if not post:
            return jsonify({"error": "Post no encontrado"}), 404
        return jsonify(PostSchema().dump(post)), 200

    @roles_required("user", "moderator", "admin")
    @active_user_required
    def put(self, post_id):
        """Actualizar un post (solo autor o admin)"""
        post = post_service.get_post_by_id(post_id)
        if not post:
            return jsonify({"error": "Post no encontrado"}), 404

        data = request.get_json()
        schema = PostUpdateSchema()
        try:
            valid_data = schema.load(data)
        except Exception as err:
            return jsonify({"error": "Datos inválidos", "details": str(err)}), 400

        try:
            actualizado = post_service.update_post(post, valid_data)
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403

        return jsonify(PostSchema().dump(actualizado)), 200

    @roles_required("user", "moderator", "admin")
    @active_user_required
    def delete(self, post_id):
        """Eliminar un post (solo autor o admin)"""
        post = post_service.get_post_by_id(post_id)
        if not post:
            return jsonify({"error": "Post no encontrado"}), 404

        try:
            post_service.delete_post(post)
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403

        return jsonify({"message": "Post eliminado correctamente"}), 200