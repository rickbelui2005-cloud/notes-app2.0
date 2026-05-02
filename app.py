from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ PostgreSQL connection
def get_db_connection():
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    return conn

# ✅ Create tables
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        text TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# 🟢 REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# 🟢 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect('/')
        else:
            return "Invalid login"

    return render_template('login.html')

# 🟢 HOME (protected)
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        text = request.form['note']
        cur.execute("INSERT INTO notes (user_id, text) VALUES (%s, %s)", (session['user_id'], text))
        conn.commit()

    cur.execute("SELECT * FROM notes WHERE user_id=%s", (session['user_id'],))
    notes = cur.fetchall()

    conn.close()

    return render_template('index.html', notes=notes)

# 🟢 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)
