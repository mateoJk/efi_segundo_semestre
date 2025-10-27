# app.py
import os
from datetime import timedelta

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Instanciamos db aquí para que models.py pueda hacer `from app import db`
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_object: dict | None = None) -> Flask:
    """
    Factory para crear la aplicación Flask.
    - Permite crear instancias para testing, development y producción.
    - Inicializa extensiones (db, migrate, jwt).
    - Registra blueprints / vistas.
    """
    app = Flask(__name__, instance_relative_config=False)

    # ---------------------------
    # Configuración por defecto
    # ---------------------------
    app.config.setdefault('SQLALCHEMY_DATABASE_URI',
                          os.getenv('DATABASE_URL', 'mysql+pymysql://root:@172.26.112.1/miniblog'))
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # JWT: secret + expiración (24 horas)
    app.config.setdefault('JWT_SECRET_KEY', os.getenv('JWT_SECRET_KEY', 'cualquiercosa'))
    app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))

    # Permite pasar un diccionario de configuración al factory para tests u overrides
    if config_object:
        if isinstance(config_object, dict):
            app.config.update(config_object)
        else:
            # si pasan un objeto, asumimos que es importable
            app.config.from_object(config_object)

    # ---------------------------
    # Inicializar extensiones
    # ---------------------------
    db.init_app(app)
    from models import Usuario, UserCredentials, Post, Comentario, Categoria, post_categoria
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Importar modelos/vistas **después** de inicializar db para evitar ciclos
    # (models.py usa `from app import db` — por eso db debe existir primero)
    with app.app_context():
        # Importar vistas y modelos aquí (lazy import)
        # views debe exportar las clases MethodView o blueprints que queremos registrar
        try:
            # Importar views; si dividís las vistas en un paquete, ajustá las importaciones
            from views import (
                AuthRegisterView, AuthLoginView,
                PostsAPI, PostDetailAPI,
                PostCommentsAPI, CommentDeleteAPI,
                CategoriesAPI, CategoryDetailAPI,
                UsersAPI, UserDetailAPI, UserRolePatchAPI,
                StatsAPI
            )
        except Exception as exc:
            # Si views no está listo aún, evitamos que la app rompa en la importación
            # pero lanzamos un mensaje claro (útil en desarrollo)
            app.logger.debug("Import de views falló: %s", exc)

        # Registrar rutas bajo el prefijo /api
        # Si más adelante querés usar Blueprints, reemplazá estas add_url_rule por blueprint.register
        try:
            app.add_url_rule('/api/register', view_func=AuthRegisterView.as_view('register'), methods=['POST'])
            app.add_url_rule('/api/login', view_func=AuthLoginView.as_view('login'), methods=['POST'])

            app.add_url_rule('/api/posts', view_func=PostsAPI.as_view('posts'), methods=['GET', 'POST'])
            app.add_url_rule('/api/posts/<int:post_id>', view_func=PostDetailAPI.as_view('post_detail'),
                             methods=['GET', 'PUT', 'DELETE'])

            app.add_url_rule('/api/posts/<int:post_id>/comments', view_func=PostCommentsAPI.as_view('post_comments'),
                             methods=['GET', 'POST'])
            app.add_url_rule('/api/comments/<int:comment_id>', view_func=CommentDeleteAPI.as_view('comment_delete'),
                             methods=['DELETE'])

            app.add_url_rule('/api/categories', view_func=CategoriesAPI.as_view('categories'), methods=['GET', 'POST'])
            app.add_url_rule('/api/categories/<int:cat_id>', view_func=CategoryDetailAPI.as_view('category_detail'),
                             methods=['PUT', 'DELETE'])

            app.add_url_rule('/api/users', view_func=UsersAPI.as_view('users'), methods=['GET'])
            app.add_url_rule('/api/users/<int:user_id>', view_func=UserDetailAPI.as_view('user_detail'),
                             methods=['GET', 'DELETE'])
            app.add_url_rule('/api/users/<int:user_id>/role', view_func=UserRolePatchAPI.as_view('user_role'),
                             methods=['PATCH'])

            app.add_url_rule('/api/stats', view_func=StatsAPI.as_view('stats'), methods=['GET'])
        except NameError:
            # Si views no exportó las clases (aún no implementadas), no registramos las rutas.
            # Esto permite que la app arranque sin todas las vistas implementadas.
            app.logger.debug("No se registraron algunas rutas: las vistas aún no están implementadas.")

    # ---------------------------
    # Errores JSON-friendly
    # ---------------------------
    @app.errorhandler(400)
    def bad_request(err):
        return jsonify({"error": "Bad Request", "message": getattr(err, "description", "")}), 400

    @app.errorhandler(401)
    def unauthorized(err):
        return jsonify({"error": "Unauthorized", "message": getattr(err, "description", "")}), 401

    @app.errorhandler(403)
    def forbidden(err):
        return jsonify({"error": "Forbidden", "message": getattr(err, "description", "")}), 403

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({"error": "Not Found", "message": getattr(err, "description", "")}), 404

    @app.errorhandler(500)
    def internal_error(err):
        return jsonify({"error": "Internal Server Error", "message": "Ocurrió un error en el servidor."}), 500

    return app


# Shortcut para desarrollo rápido
if __name__ == '__main__':
    # si ejecutás `python app.py` arranca la app dev en puerto 5000
    app = create_app()
    app.run(debug=True)