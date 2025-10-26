# EFI Segunda Etapa - Programación Python 1
## Sistema de Roles y Permisos en API REST

---

## Contexto

En la primera etapa desarrollaron un miniblog con Flask, modelos relacionales y templates. Ahora van a evolucionar ese proyecto hacia una **API REST con autenticación JWT y control de acceso basado en roles (RBAC)**.

---

## Enunciado

Deberás extender tu proyecto de miniblog para convertirlo en una **API REST segura** que implemente:
- Autenticación con JWT (JSON Web Tokens)
- Sistema de roles de usuario (admin, moderador, usuario)
- Control de permisos por endpoint según el rol
- Vistas basadas en clases (MethodView)
- Arquitectura service-repository (opcional pero recomendado)

---

## Requisitos Funcionales

### 1. Sistema de Roles

Implementa **tres roles** con los siguientes permisos:

#### **Usuario (user)**
- Ver todos los posts y comentarios (público)
- Crear sus propios posts
- Editar y eliminar **solo sus propios** posts
- Comentar en cualquier post
- Editar y eliminar **solo sus propios** comentarios

#### **Moderador (moderator)**
- Todo lo que puede hacer un usuario
- Eliminar **cualquier** comentario (moderación)
- Editar categorías
- Ver estadísticas básicas (cantidad de posts, comentarios, usuarios)

#### **Administrador (admin)**
- Todo lo que puede hacer un moderador
- Eliminar **cualquier** post
- Crear, editar y eliminar categorías
- Gestionar usuarios (ver lista, cambiar roles, desactivar usuarios)
- Ver estadísticas completas del sistema

---

### 2. Modelos a Modificar/Crear

#### **Usuario** (modificar el existente)
Agregar:
- `role`: String (valores: "user", "moderator", "admin") - default: "user"
- `is_active`: Boolean - default: True
- `created_at`: DateTime

#### **UserCredentials** (nuevo modelo recomendado)
Separar las credenciales del modelo User:
- `user_id`: ForeignKey a User
- `password_hash`: String (nunca guardar contraseñas en texto plano)
- `role`: String

#### **Post** (modificar el modelo Entrada)
Agregar:
- `is_published`: Boolean - default: True
- `updated_at`: DateTime

#### **Comentario** (modificar el existente)
Agregar:
- `is_visible`: Boolean - default: True (para moderación)

---

### 3. Endpoints a Implementar

Todos los endpoints deben estar implementados como **vistas basadas en clases** usando `MethodView`.

#### **Autenticación**
```
POST /api/register
  Body: { "username", "email", "password" }
  Response: { "message": "Usuario creado", "user_id": 1 }

POST /api/login
  Body: { "email", "password" }
  Response: { "access_token": "eyJ0eXAiOiJKV1QiLCJh..." }
```

#### **Posts**
```
GET    /api/posts              # Público - listar todos los posts
GET    /api/posts/<id>         # Público - ver un post específico
POST   /api/posts              # Requiere autenticación (user+)
PUT    /api/posts/<id>         # Solo el autor o admin
DELETE /api/posts/<id>         # Solo el autor o admin
```

#### **Comentarios**
```
GET    /api/posts/<id>/comments      # Público
POST   /api/posts/<id>/comments      # Requiere autenticación (user+)
DELETE /api/comments/<id>            # Autor, moderator o admin
```

#### **Categorías**
```
GET    /api/categories         # Público
POST   /api/categories         # Solo moderator y admin
PUT    /api/categories/<id>    # Solo moderator y admin
DELETE /api/categories/<id>    # Solo admin
```

#### **Usuarios (Admin)**
```
GET    /api/users              # Solo admin
GET    /api/users/<id>         # Usuario mismo o admin
PATCH  /api/users/<id>/role    # Solo admin (cambiar rol)
DELETE /api/users/<id>         # Solo admin (desactivar)
```

#### **Estadísticas**
```
GET /api/stats                 # Moderator y admin
  Response: {
    "total_posts": 45,
    "total_comments": 120,
    "total_users": 30,
    "posts_last_week": 8  // solo admin
  }
```

---

### 4. Implementación Técnica

#### **Autenticación JWT**
- Usar `flask-jwt-extended`
- El token debe incluir: `user_id`, `email`, `role`
- Tiempo de expiración: 24 horas

#### **Decoradores de Permisos**
Crear decoradores personalizados:

```python
@jwt_required()
@roles_required("admin", "moderator")
def delete_comment(id):
    # lógica
```

#### **Validación con Marshmallow**
- Todos los endpoints deben validar datos de entrada con schemas
- Manejar errores de validación apropiadamente

#### **Verificación de Propiedad**
Para operaciones como editar/eliminar posts propios:
```python
def check_ownership(user_id, resource_owner_id):
    """Verifica si el usuario es dueño del recurso"""
    claims = get_jwt()
    if claims['role'] == 'admin':
        return True
    return user_id == resource_owner_id
```

---

### 5. Arquitectura (Recomendado)

Organiza tu código siguiendo el patrón **service-repository**:

```
/project
  /models       # Modelos SQLAlchemy
  /schemas      # Schemas Marshmallow
  /repositories # Acceso a datos (queries)
  /services     # Lógica de negocio
  /views        # Controladores (MethodView)
  /decorators   # Decoradores personalizados
  app.py        # Configuración y rutas
```

**Ejemplo:**
```python
# repositories/post_repository.py
class PostRepository:
    @staticmethod
    def get_all_published():
        return Post.query.filter_by(is_published=True).all()

# services/post_service.py
class PostService:
    def __init__(self):
        self.repo = PostRepository()
    
    def get_public_posts(self):
        return self.repo.get_all_published()

# views/post_views.py
class PostAPI(MethodView):
    def __init__(self):
        self.service = PostService()
    
    def get(self):
        posts = self.service.get_public_posts()
        return PostSchema(many=True).dump(posts)
```

---

## Criterios de Evaluación

### Funcionalidad (40%)
- [ ] Sistema de autenticación JWT funcional
- [ ] Los tres roles implementados correctamente
- [ ] Todos los endpoints requeridos funcionan
- [ ] Validación de permisos correcta en cada endpoint

### Código (30%)
- [ ] Uso de vistas basadas en clases (MethodView)
- [ ] Schemas de Marshmallow para validación
- [ ] Código organizado y legible
- [ ] Manejo apropiado de errores

### Seguridad (20%)
- [ ] Contraseñas hasheadas (bcrypt o similar)
- [ ] Tokens JWT implementados correctamente
- [ ] Verificación de propiedad de recursos
- [ ] No hay endpoints sin protección que deberían tenerla

### Arquitectura (10%)
- [ ] Separación de responsabilidades
- [ ] Uso de decoradores personalizados
- [ ] Código reutilizable

---

## Entregables

1. **Repositorio de GitHub** con:
   - Código fuente completo
   - `requirements.txt` actualizado
   - `README.md` con:
     - Instrucciones de instalación
     - Cómo ejecutar el proyecto
     - Documentación de endpoints (puede ser informal)
     - Credenciales de prueba para cada rol

2. **Archivo de prueba** (Postman Collection o archivo `.http`):
   - Ejemplos de requests para cada endpoint
   - Casos de éxito y error

3. **Base de datos**:
   - Migraciones o script SQL para crear las tablas
   - Datos de prueba (al menos 1 usuario de cada rol)

---

## Consideraciones

- **Máximo por grupo:** 3 personas
- **Entrega individual:** Cada integrante debe subir el repositorio en Classroom
- **Base de datos:** MySQL (puede ser local o remota)
- **Fecha de entrega:** [DEFINIR FECHA]
- **Consultas:** Pueden hacerse durante las clases o por el canal de Discord/Slack

---

## Plus Opcionales (Puntos Extra)

- [ ] Implementar refresh tokens
- [ ] Paginación en listados de posts
- [ ] Filtros y búsqueda de posts por categoría/autor
- [ ] Rate limiting (límite de requests por usuario)
- [ ] Tests con cobertura >70%
- [ ] Documentación con Swagger/OpenAPI
- [ ] Implementar soft delete en lugar de borrado físico
- [ ] Sistema de notificaciones (cuando alguien comenta tu post)

---

## Recursos Útiles

- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)
- [Flask MethodView](https://flask.palletsprojects.com/en/2.3.x/views/)
- [Passlib (hashing)](https://passlib.readthedocs.io/)

---

## Ejemplo de Flujo de Trabajo

1. Usuario se registra → recibe confirmación
2. Usuario hace login → recibe JWT token
3. Usuario crea un post → incluye token en header `Authorization: Bearer <token>`
4. Otro usuario comenta el post → también autenticado
5. Moderador elimina un comentario inapropiado → verificación de rol
6. Admin cambia el rol de un usuario a moderador → solo admin puede hacerlo

---

**¡Éxitos con la segunda etapa!** 🚀

Recuerden que el objetivo es que apliquen los conceptos de:
- Autenticación y autorización
- Arquitectura de software
- Seguridad en APIs
- Buenas prácticas de desarrollo