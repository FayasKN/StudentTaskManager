from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database connection
db = sqlite3.connect('database.db', check_same_thread=False)
cursor = db.cursor()

# Create tables if not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT,
    status TEXT
)
''')

db.commit()


@app.route('/')
def home():
    return render_template('login.html')


# Register
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )
    db.commit()

    return "User Registered Successfully!"


# Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    user = cursor.fetchone()

    if user:
        return redirect(f'/dashboard/{user[0]}')
    else:
        return "Invalid Username or Password"


# Dashboard
@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    cursor.execute(
        "SELECT * FROM tasks WHERE user_id=?",
        (user_id,)
    )
    tasks = cursor.fetchall()
    return render_template('dashboard.html', tasks=tasks, user_id=user_id)


# Add task
@app.route('/add/<int:user_id>', methods=['POST'])
def add_task(user_id):
    task = request.form['task']

    cursor.execute(
        "INSERT INTO tasks (user_id, task, status) VALUES (?, ?, ?)",
        (user_id, task, "pending")
    )
    db.commit()

    return redirect(f'/dashboard/{user_id}')


# Complete task
@app.route('/complete/<int:task_id>/<int:user_id>')
def complete_task(task_id, user_id):
    cursor.execute(
        "UPDATE tasks SET status='done' WHERE id=?",
        (task_id,)
    )
    db.commit()

    return redirect(f'/dashboard/{user_id}')


# Delete task
@app.route('/delete/<int:task_id>/<int:user_id>')
def delete_task(task_id, user_id):
    cursor.execute(
        "DELETE FROM tasks WHERE id=?",
        (task_id,)
    )
    db.commit()

    return redirect(f'/dashboard/{user_id}')


# Logout
@app.route('/logout')
def logout():
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
