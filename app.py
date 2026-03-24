from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="studenttaskmanager"
)

cursor = db.cursor()

@app.route('/')
def home():
    return render_template('login.html')

# Register
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    db.commit()

    return "User Registered Successfully!"

# Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        return redirect(f'/dashboard/{user[0]}')
    else:
        return "Invalid Username or Password"

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    cursor.execute("SELECT * FROM tasks WHERE user_id=%s", (user_id,))
    tasks = cursor.fetchall()
    return render_template('dashboard.html', tasks=tasks, user_id=user_id)

@app.route('/add/<int:user_id>', methods=['POST'])
def add_task(user_id):
    task = request.form['task']
    cursor.execute("INSERT INTO tasks (user_id, task, status) VALUES (%s, %s, %s)", (user_id, task, "pending"))
    db.commit()
    return redirect(f'/dashboard/{user_id}')

@app.route('/complete/<int:task_id>/<int:user_id>')
def complete_task(task_id, user_id):
    cursor.execute("UPDATE tasks SET status='done' WHERE id=%s", (task_id,))
    db.commit()
    return redirect(f'/dashboard/{user_id}')

@app.route('/delete/<int:task_id>/<int:user_id>')
def delete_task(task_id, user_id):
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    db.commit()
    return redirect(f'/dashboard/{user_id}')
@app.route('/logout')
def logout():
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
