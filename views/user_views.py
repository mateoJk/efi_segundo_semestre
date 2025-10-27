from flask import jsonify, request
from flask.views import MethodView
from decorators.auth_decorators import roles_required, active_user_required
from services.user_service import UserService
from marshmallow import Schema, fields, validate

user_service = UserService()

# ==================== Schemas ====================
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Str()
    is_active = fields.Bool()
    role = fields.Method("get_role")

    def get_role(self, obj):
        return obj.credenciales.role if obj.credenciales else None


class UserRoleUpdateSchema(Schema):
    role = fields.Str(required=True, validate=validate.OneOf(["user", "moderator", "admin"]))


# ==================== Views ====================
class UsersAPI(MethodView):
    """Listar todos los usuarios"""
    @roles_required("admin")
    @active_user_required
    def get(self):
        users = user_service.get_all_users()
        return jsonify(UserSchema(many=True).dump(users)), 200


class UserDetailAPI(MethodView):
    """Obtener y desactivar un usuario"""
    @roles_required("admin")
    @active_user_required
    def get(self, user_id):
        user = user_service.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(UserSchema().dump(user)), 200

    @roles_required("admin")
    @active_user_required
    def delete(self, user_id):
        try:
            user = user_service.deactivate_user(user_id)
            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 404
            return jsonify({"message": f"Usuario {user.username} desactivado correctamente"}), 200
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403


class UserRolePatchAPI(MethodView):
    """Actualizar rol de un usuario"""
    @roles_required("admin")
    @active_user_required
    def patch(self, user_id):
        data = request.get_json()
        schema = UserRoleUpdateSchema()
        try:
            valid_data = schema.load(data)
        except Exception as err:
            return jsonify({"error": "Datos inválidos", "details": str(err)}), 400

        try:
            user = user_service.update_user_role(user_id, valid_data["role"])
            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 404
            return jsonify(UserSchema().dump(user)), 200
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403