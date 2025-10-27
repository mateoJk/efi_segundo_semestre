from typing import List, Optional
from models import Usuario, UserCredentials
from app import db
from flask_jwt_extended import get_jwt_identity, get_jwt

class UserService:
    """Lógica de negocio para usuarios"""

    def get_all_users(self) -> List[Usuario]:
        return Usuario.query.order_by(Usuario.username.asc()).all()

    def get_user_by_id(self, user_id: int) -> Optional[Usuario]:
        return Usuario.query.get(user_id)

    def update_user_role(self, user_id: int, new_role: str) -> Optional[Usuario]:
        user = self.get_user_by_id(user_id)
        if not user or not user.credenciales:
            return None

        # Evitar que un admin cambie su propio rol
        current_user_id = get_jwt_identity()
        if current_user_id == user.id:
            raise PermissionError("No puedes cambiar tu propio rol")

        user.credenciales.role = new_role
        db.session.commit()
        db.session.refresh(user)
        return user

    def deactivate_user(self, user_id: int) -> Optional[Usuario]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        current_user_id = get_jwt_identity()
        # Evitar que un admin se desactive a sí mismo
        if current_user_id == user.id:
            raise PermissionError("No puedes desactivar tu propia cuenta")

        user.is_active = False
        db.session.commit()
        db.session.refresh(user)
        return user