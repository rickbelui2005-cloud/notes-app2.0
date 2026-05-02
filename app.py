from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# create DB
def init_db():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT)')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def home():
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        note = request.form['note']
        if note.strip():
            cursor.execute('INSERT INTO notes (text) VALUES (?)', (note,))
            conn.commit()
        conn.close()
        return redirect('/')

    cursor.execute('SELECT * FROM notes')
    notes = cursor.fetchall()
    conn.close()

    return render_template('index.html', notes=notes)

# IMPORTANT for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)