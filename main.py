from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

# Usuarios simulados 
users = {
    "admin": "1234",
    "dilan": "abcd"
}

@app.route('/')
def home():
    # Redirigir al login
    if "user" not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session["user"])

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
