from app import db
from models import Usuario, UserCredentials


class UserRepository:
    """Acceso a datos de usuarios."""

    @staticmethod
    def get_all():
        """Devuelve todos los usuarios activos e inactivos."""
        return Usuario.query.order_by(Usuario.username.asc()).all()

    @staticmethod
    def get_by_id(user_id: int):
        """Obtiene un usuario por id."""
        return Usuario.query.get(user_id)

    @staticmethod
    def update_role(user: Usuario, new_role: str):
        """Actualiza el rol del usuario (user, moderator, admin)."""
        if not user.credenciales:
            return None
        user.credenciales.role = new_role
        db.session.commit()
        db.session.refresh(user)
        return user

    @staticmethod
    def deactivate_user(user: Usuario):
        """Desactiva un usuario (is_active=False)."""
        user.is_active = False
        db.session.commit()
        db.session.refresh(user)
        return user