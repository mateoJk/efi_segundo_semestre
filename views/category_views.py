from flask import request, jsonify
from flask.views import MethodView
from services.category_service import CategoryService
from schemas.category_schemas import CategorySchema, CategoryCreateSchema
from decorators.auth_decorators import roles_required, active_user_required

category_service = CategoryService()


class CategoriesAPI(MethodView):
    """Endpoints para /api/categories"""

    def get(self):
        """Listar categorías (público)"""
        categorias = category_service.get_all_categories()
        schema = CategorySchema(many=True)
        return jsonify(schema.dump(categorias)), 200

    @roles_required("moderator", "admin")
    @active_user_required
    def post(self):
        """Crear categoría (solo moderator o admin)"""
        data = request.get_json()
        schema = CategoryCreateSchema()
        try:
            valid_data = schema.load(data)
        except Exception as err:
            return jsonify({"error": "Datos inválidos", "details": str(err)}), 400

        nueva = category_service.create_category(valid_data["nombre"])
        return jsonify(CategorySchema().dump(nueva)), 201


class CategoryDetailAPI(MethodView):
    """Endpoints para /api/categories/<id>"""

    @roles_required("moderator", "admin")
    @active_user_required
    def put(self, category_id):
        """Actualizar categoría (solo moderator o admin)"""
        category = category_service.get_category_by_id(category_id)
        if not category:
            return jsonify({"error": "Categoría no encontrada"}), 404

        data = request.get_json()
        schema = CategoryCreateSchema()
        try:
            valid_data = schema.load(data)
        except Exception as err:
            return jsonify({"error": "Datos inválidos", "details": str(err)}), 400

        actualizada = category_service.update_category(category, valid_data["nombre"])
        return jsonify(CategorySchema().dump(actualizada)), 200

    @roles_required("admin")
    @active_user_required
    def delete(self, category_id):
        """Eliminar categoría (solo admin)"""
        category = category_service.get_category_by_id(category_id)
        if not category:
            return jsonify({"error": "Categoría no encontrada"}), 404

        category_service.delete_category(category)
        return jsonify({"message": "Categoría eliminada correctamente"}), 200