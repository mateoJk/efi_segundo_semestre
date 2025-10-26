from flask import (
    Flask, 
    flash, 
    redirect,
    render_template, 
    request,
    url_for,
    abort
    )

# generar vistas o endpoints para los crud que ya tiene la app que armaron.

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_login import(
    LoginManager, #gestiona el sistema de login (quién está logueado, etc.)
    login_user, # inicia sesión con un usuario válido.
    login_required, # protege rutas, solo accesibles si estás logueado.
    logout_user, # cerrar sesión
    current_user # variable mágica que te dice quién está conectado.
)
from werkzeug.security import (
    generate_password_hash, #cifran y verifican contraseñas de forma segura.
    check_password_hash
    )


app = Flask(__name__)

app.secret_key = "cualquiercosa"
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://root:@172.26.112.1/miniblog"
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import Usuario, Post, Comentario, Categoria


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

from datetime import datetime

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.context_processor
def inject_categorias():
    categorias = Categoria.query.all()
    return dict(categorias=categorias)

@app.route('/')
def index():
    return render_template(
        'index.html'
   )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # contraseña que llega desde el formulario
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(pwhash= user.password_hash, password = password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('El usuario o la contraseña no existen.', 'danger')
    return render_template(
        'auth/login.html'
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if not username or not email or not password:
            flash('Completa todos los campos.', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('register'))

        user = Usuario.query.filter_by(username=username).first()
        if user:
            flash('El nombre de usuario ya existe', 'danger')
            return redirect(url_for('register'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'danger')
            return redirect(url_for('register'))
        
        # Hasheo de contraseña
        password_hash = generate_password_hash(
            password=password
            #,method = 'pbkdf2' --> usa pbkdf2:sha256 por defecto
        )
        # Creacion de nuevo usuario con contraseña hash
        new_user = Usuario(
            username = username,
            email=email,
            password_hash = password_hash
        )

        db.session.add(new_user)
        db.session.commit()
        flash('Usuario creado correctamente', 'success')
        return redirect(url_for('login'))

    return render_template(
        'auth/register.html'
    )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/posts', methods=['GET', 'POST'])
def posts():
    # Crear nuevo post si está logueado y envió el formulario
    if current_user.is_authenticated and request.method == 'POST':
        titulo = request.form['titulo']
        contenido = request.form['contenido']
        categoria_ids = request.form.getlist('categoria_id')
        nuevas_categorias = []

        nueva_categoria = request.form['nueva_categoria'].strip()
        if nueva_categoria:
            existente = Categoria.query.filter_by(nombre=nueva_categoria).first()
            if not existente:
                nueva_categoria_obj = Categoria(nombre=nueva_categoria)
                db.session.add(nueva_categoria_obj)
                db.session.commit()
                nuevas_categorias.append(nueva_categoria_obj)
            else:
                nuevas_categorias.append(existente)

        categorias_seleccionadas = Categoria.query.filter(Categoria.id.in_(categoria_ids)).all()

        nuevo_post = Post(
            titulo=titulo,
            contenido=contenido,
            usuario_id=current_user.id,
            categorias=categorias_seleccionadas + nuevas_categorias
        )
        db.session.add(nuevo_post)
        db.session.commit()
        flash('Post creado correctamente', 'success')
        return redirect(url_for('posts'))

    # Mostrar todos los posts ordenados por fecha
    posts = Post.query.order_by(Post.fecha_creacion.desc()).all()
    return render_template('posts.html', posts=posts)


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detalle(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST' and current_user.is_authenticated:
        contenido = request.form['comentario_contenido']
        nuevo_comentario = Comentario(
            contenido=contenido,
            usuario_id=current_user.id,
            post_id=post.id
        )
        db.session.add(nuevo_comentario)
        db.session.commit()
        flash('Comentario agregado', 'success')
        return redirect(url_for('post_detalle', post_id=post.id))

    return render_template('post_detalle.html', post=post)


@app.route('/editar_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def editar_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Asegurar que solo el autor pueda editar
    if post.usuario_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        post.titulo = request.form['titulo']
        post.contenido = request.form['contenido']

        categoria_ids = request.form.getlist('categoria_id')
        nuevas_categorias = []

        nueva_categoria = request.form['nueva_categoria'].strip()
        if nueva_categoria:
            existente = Categoria.query.filter_by(nombre=nueva_categoria).first()
            if not existente:
                nueva_categoria_obj = Categoria(nombre=nueva_categoria)
                db.session.add(nueva_categoria_obj)
                db.session.commit()
                nuevas_categorias.append(nueva_categoria_obj)
            else:
                nuevas_categorias.append(existente)

        categorias_seleccionadas = Categoria.query.filter(Categoria.id.in_(categoria_ids)).all()

        # Limpiar y actualizar las categorías del post
        post.categorias = categorias_seleccionadas + nuevas_categorias

        db.session.commit()
        flash('Post actualizado correctamente', 'success')
        return redirect(url_for('post_detalle', post_id=post.id))

    return render_template('editar_post.html', post=post)


@app.route('/post/<int:post_id>/eliminar', methods=['POST'])
@login_required
def eliminar_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.usuario_id != current_user.id:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('El post fue eliminado con éxito.', 'success')
    return redirect(url_for('posts'))


@app.route('/comentario/<int:comentario_id>/editar', methods=['POST'])
@login_required
def editar_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    if comentario.usuario_id != current_user.id:
        abort(403)

    nuevo_contenido = request.form['contenido'].strip()
    if nuevo_contenido:
        comentario.contenido = nuevo_contenido
        db.session.commit()
        flash('Comentario editado correctamente', 'success')
    else:
        flash('El contenido no puede estar vacío', 'danger')

    return redirect(url_for('post_detalle', post_id=comentario.post_id))


@app.route('/comentario/<int:comentario_id>/eliminar', methods=['POST'])
@login_required
def eliminar_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    if comentario.usuario_id != current_user.id:
        abort(403)

    db.session.delete(comentario)
    db.session.commit()
    flash('Comentario eliminado correctamente', 'success')
    return redirect(url_for('post_detalle', post_id=comentario.post_id))


@app.route('/posts/categoria/<int:categoria_id>')
def posts_por_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    posts = categoria.posts.order_by(Post.fecha_creacion.desc()).all()
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template('posts.html', posts=posts, categorias=categorias,categoria_actual=categoria)