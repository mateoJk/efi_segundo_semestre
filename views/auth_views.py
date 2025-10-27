from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import create_access_token

from app import db
from models import Usuario, UserCredentials
from schemas.auth_schemas import RegisterSchema, LoginSchema


class AuthRegisterView(MethodView):
    def post(self):
        """Registro de nuevo usuario"""
        data = request.get_json()
        schema = RegisterSchema()

        # Validación
        try:
            valid_data = schema.load(data)
        except Exception as err:
            return jsonify({"error": "Datos inválidos", "details": str(err)}), 400

        # Verificar que no exista usuario o email
        if Usuario.query.filter_by(email=valid_data["email"]).first():
            return jsonify({"error": "El email ya está registrado"}), 400
        if Usuario.query.filter_by(username=valid_data["username"]).first():
            return jsonify({"error": "El nombre de usuario ya está en uso"}), 400

        # Crear usuario y credenciales
        nuevo_usuario = Usuario(username=valid_data["username"], email=valid_data["email"])
        db.session.add(nuevo_usuario)
        db.session.flush()  # obtener ID antes de commit

        credenciales = UserCredentials(usuario_id=nuevo_usuario.id)
        credenciales.set_password(valid_data["password"])

        db.session.add(credenciales)
        db.session.commit()

        return jsonify({
            "message": "Usuario creado correctamente",
            "user_id": nuevo_usuario.id
        }), 201


class AuthLoginView(MethodView):
    def post(self):
        """Login y generación de token JWT"""
        data = request.get_json()
        schema = LoginSchema()

        # Validación
        try:
            valid_data = schema.load(data)
        except Exception as err:
            return jsonify({"error": "Datos inválidos", "details": str(err)}), 400

        usuario = Usuario.query.filter_by(email=valid_data["email"]).first()

        if not usuario or not usuario.credenciales:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if not usuario.credenciales.check_password(valid_data["password"]):
            return jsonify({"error": "Contraseña incorrecta"}), 401

        if not usuario.is_active:
            return jsonify({"error": "Usuario inactivo"}), 403

        # Crear token JWT con claims personalizados
        access_token = create_access_token(identity=usuario.id, additional_claims={
            "username": usuario.username,
            "email": usuario.email,
            "role": usuario.credenciales.role,
            "is_active": usuario.is_active
        })

        return jsonify({
            "access_token": access_token,
            "user": {
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "role": usuario.credenciales.role
            }
        }), 200