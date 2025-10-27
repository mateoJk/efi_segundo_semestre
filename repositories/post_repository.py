from datetime import datetime, timedelta
from typing import List, Optional

from app import db
from models import Post, Categoria


class PostRepository:
    """Repository para operaciones CRUD sobre Post."""

    @staticmethod
    def get_all(published_only: bool = True, order_desc: bool = True) -> List[Post]:
        """
        Devuelve todos los posts.
        - published_only: si True devuelve solo posts con is_published=True.
        - order_desc: si True ordena por fecha_creacion desc.
        """
        query = Post.query
        if published_only:
            query = query.filter_by(is_published=True)
        if order_desc:
            query = query.order_by(Post.fecha_creacion.desc())
        else:
            query = query.order_by(Post.fecha_creacion.asc())
        return query.all()

    @staticmethod
    def get_by_id(post_id: int) -> Optional[Post]:
        """Devuelve un Post por su id o None si no existe."""
        return Post.query.get(post_id)

    @staticmethod
    def get_by_user(user_id: int, published_only: bool = False) -> List[Post]:
        """Devuelve posts escritos por un usuario."""
        query = Post.query.filter_by(usuario_id=user_id)
        if published_only:
            query = query.filter_by(is_published=True)
        return query.order_by(Post.fecha_creacion.desc()).all()

    @staticmethod
    def create(data: dict) -> Post:
        """
        Crea y guarda un Post.
        data expected keys:
          - titulo (str)
          - contenido (str)
          - usuario_id (int)
          - is_published (bool) optional
          - categoria_ids (list[int]) optional
        Retorna la instancia Post creada (no serializada).
        """
        categoria_objs = []
        cat_ids = data.get("categoria_ids") or []
        if cat_ids:
            categoria_objs = Categoria.query.filter(Categoria.id.in_(cat_ids)).all()

        nuevo_post = Post(
            titulo=data["titulo"],
            contenido=data["contenido"],
            usuario_id=data["usuario_id"],
            is_published=data.get("is_published", True)
        )

        # Asociar categorías si existen
        if categoria_objs:
            for c in categoria_objs:
                nuevo_post.categorias.append(c)

        db.session.add(nuevo_post)
        db.session.commit()
        # refrescar por si hay defaults/autogenerados
        db.session.refresh(nuevo_post)
        return nuevo_post

    @staticmethod
    def update(post: Post, data: dict) -> Post:
        """
        Actualiza un Post existente.
        - post: instancia de Post ya cargada.
        - data: dict con campos a actualizar (titulo, contenido, is_published, categoria_ids)
        Devuelve la instancia actualizada.
        """
        if "titulo" in data and data["titulo"] is not None:
            post.titulo = data["titulo"]
        if "contenido" in data and data["contenido"] is not None:
            post.contenido = data["contenido"]
        if "is_published" in data:
            post.is_published = data["is_published"]

        # Manejo de categorías: si viene categoria_ids, reemplazamos las relaciones
        if "categoria_ids" in data:
            cat_ids = data.get("categoria_ids") or []
            if cat_ids:
                categorias = Categoria.query.filter(Categoria.id.in_(cat_ids)).all()
                post.categorias = categorias
            else:
                # si lista vacía => limpiar categorías
                post.categorias = []

        db.session.commit()
        db.session.refresh(post)
        return post

    @staticmethod
    def delete(post: Post) -> None:
        """Elimina un post (borrado físico)."""
        db.session.delete(post)
        db.session.commit()

    @staticmethod
    def count_all(published_only: bool = True) -> int:
        """Cuenta posts (útil para estadísticas)."""
        query = Post.query
        if published_only:
            query = query.filter_by(is_published=True)
        return query.count()

    @staticmethod
    def get_posts_last_week() -> List[Post]:
        """Devuelve posts creados en la última semana."""
        since = datetime.utcnow() - timedelta(days=7)
        return Post.query.filter(Post.fecha_creacion >= since).order_by(Post.fecha_creacion.desc()).all()