from flask import Flask, render_template, request, redirect, session, url_for, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"
DB_NAME = "mascotas.db"

# CONEXIÓN A LA BASE DE DATOS
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# INICIALIZAR BASE DE DATOS
def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE mascotas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    especie TEXT NOT NULL,
                    raza TEXT,
                    edad INTEGER,
                    propietario TEXT
                )
            """)
            # Usuario de ejemplo
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
        print("Base de datos creada con éxito")

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template('login.html', error=error)

# REGISTRO DE NUEVOS USUARIOS
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "El nombre de usuario ya existe"
    return render_template('register.html', error=error)

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session["user"])

# CRUD DE MASCOTAS
@app.route('/mascotas')
def mascotas():
    if "user" not in session:
        return redirect(url_for('login'))
    db = get_db()
    data = db.execute("SELECT * FROM mascotas").fetchall()
    return render_template('mascotas.html', mascotas=data)

@app.route('/mascotas/add', methods=['POST'])
def add_mascota():
    if "user" not in session:
        return redirect(url_for('login'))
    nombre = request.form['nombre']
    especie = request.form['especie']
    raza = request.form['raza']
    edad = request.form['edad']
    propietario = request.form['propietario']
    db = get_db()
    db.execute("INSERT INTO mascotas (nombre, especie, raza, edad, propietario) VALUES (?, ?, ?, ?, ?)",
               (nombre, especie, raza, edad, propietario))
    db.commit()
    return redirect(url_for('mascotas'))

@app.route('/mascotas/delete/<int:id>')
def delete_mascota(id):
    if "user" not in session:
        return redirect(url_for('login'))
    db = get_db()
    db.execute("DELETE FROM mascotas WHERE id=?", (id,))
    db.commit()
    return redirect(url_for('mascotas'))

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
