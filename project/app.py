from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = 'mysecretkey'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT, email TEXT, progress TEXT, attendance INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS workshops (id INTEGER PRIMARY KEY, title TEXT, description TEXT, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS certificates (id INTEGER PRIMARY KEY, student_id INTEGER, code TEXT)''')
    conn.commit()
    admin = c.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
    if not admin:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', 'admin123', 'admin'))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']

        conn = sqlite3.connect('database.db')
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, 'student'))
            conn.execute("INSERT INTO students (name, email, progress, attendance) VALUES (?, ?, ?, ?)", (name, email, 'Not started', 0))
            conn.commit()
            msg = "✅ Registration successful! You can now login."
        except:
            msg = "❌ Username already exists!"
        conn.close()
        return msg

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/student')
def student_dashboard():
    if 'role' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    workshops = conn.execute("SELECT * FROM workshops").fetchall()
    conn.close()
    return render_template('student_dashboard.html', workshops=workshops, user=session['username'])

@app.route('/admin')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    students = conn.execute("SELECT * FROM students").fetchall()
    workshops = conn.execute("SELECT * FROM workshops").fetchall()
    conn.close()
    return render_template('admin_dashboard.html', students=students, workshops=workshops)

@app.route('/add_workshop', methods=['POST'])
def add_workshop():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    title = request.form['title']
    description = request.form['description']
    date = request.form['date']
    conn = sqlite3.connect('database.db')
    conn.execute("INSERT INTO workshops (title, description, date) VALUES (?, ?, ?)", (title, description, date))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    progress = request.form['progress']
    attendance = request.form['attendance']
    conn = sqlite3.connect('database.db')
    conn.execute("UPDATE students SET progress = ?, attendance = ? WHERE id = ?", (progress, attendance, student_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/generate_certificate/<int:student_id>')
def generate_certificate(student_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    conn = sqlite3.connect('database.db')
    conn.execute("INSERT INTO certificates (student_id, code) VALUES (?, ?)", (student_id, code))
    conn.commit()
    conn.close()
    return f"✅ Certificate generated! Code: {code}"

from flask import redirect

@app.route('/verify')
def verify_certificate():
    return redirect("https://bonibytesedutech-cert-verify.vercel.app/")


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
from flask import redirect



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
