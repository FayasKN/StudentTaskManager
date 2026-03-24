from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

# DB SETUP
db = sqlite3.connect('database.db', check_same_thread=False)
cursor = db.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
task TEXT,
status TEXT)''')

db.commit()


# 🎨 GLOBAL STYLE (LIQUID GLASS)
base_style = """
<style>
body {
    margin:0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background:#1c1f26;
    color:white;
}

/* 🌌 background */
.stars {
    position:fixed;
    width:100%;
    height:100%;
    background: url("https://www.transparenttextures.com/patterns/stardust.png");
    animation: moveStars 80s linear infinite;
    z-index:-1;
}
@keyframes moveStars {
    from {background-position:0 0;}
    to {background-position:2000px 2000px;}
}

/* 💎 LIQUID GLASS */
.glass {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(25px) saturate(200%);
    -webkit-backdrop-filter: blur(25px) saturate(200%);
    
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.2);

    box-shadow:
        0 8px 40px rgba(0,0,0,0.4),
        inset 0 1px 1px rgba(255,255,255,0.2),
        inset 0 -1px 1px rgba(0,0,0,0.2);

    position: relative;
    overflow: hidden;
}

/* ✨ shine */
.glass::before {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 20px;
    background: linear-gradient(
        120deg,
        rgba(255,255,255,0.25),
        rgba(255,255,255,0.05),
        transparent
    );
    opacity: 0.3;
    pointer-events: none;
}

/* inputs */
input {
    width:90%;
    padding:10px;
    margin:10px;
    border-radius:10px;
    border:none;
    background: rgba(255,255,255,0.05);
    color:white;
    backdrop-filter: blur(10px);
    transition:0.3s;
}
input:hover, input:focus {
    outline:none;
    box-shadow:0 0 12px rgba(0,255,200,0.5);
}

/* buttons */
button {
    padding:8px 14px;
    border:none;
    border-radius:10px;
    background: rgba(255,255,255,0.08);
    color:white;
    cursor:pointer;
    backdrop-filter: blur(10px);
    transition:0.3s;
}
button:hover {
    transform:scale(1.08);
    box-shadow:0 0 12px rgba(0,255,200,0.5);
}

/* tasks */
.task {
    padding:12px;
    margin:12px 0;
    display:flex;
    justify-content:space-between;
    align-items:center;
    transition:0.3s;
}
.task:hover {
    transform:translateY(-4px);
    box-shadow:0 0 18px rgba(0,255,200,0.25);
}

/* ✔ SUCCESS (GPay style) */
.success-overlay {
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    display:flex;
    justify-content:center;
    align-items:center;
    background:rgba(0,0,0,0.4);
    animation: fadeOut 1.2s forwards;
}

.circle {
    width:90px;
    height:90px;
    border-radius:50%;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(15px);
    display:flex;
    justify-content:center;
    align-items:center;
}

.checkmark {
    width:50px;
    height:50px;
    stroke:#00ffc3;
    stroke-width:4;
    stroke-linecap:round;
    stroke-linejoin:round;
    fill:none;
    stroke-dasharray:48;
    stroke-dashoffset:48;
    animation: draw 0.6s ease forwards;
}

@keyframes draw {
    to { stroke-dashoffset: 0; }
}

@keyframes fadeOut {
    0% {opacity:1;}
    80% {opacity:1;}
    100% {opacity:0; visibility:hidden;}
}

/* modal */
.modal {
    display:none;
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    background:rgba(0,0,0,0.6);
    justify-content:center;
    align-items:center;
}
.modal.active {
    display:flex;
}
</style>
"""


# 🔐 LOGIN PAGE
login_page = base_style + """
<div class="stars"></div>

<div class="glass" style="width:320px; margin:100px auto; padding:25px; text-align:center;">
<h2>Login</h2>

<form action="/login" method="post">
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button>Login</button>
</form>

<button onclick="openModal()">Register</button>
</div>

<div id="modal" class="modal">
<div class="glass" style="width:320px; padding:20px; text-align:center;">
<h3>Register</h3>
<form action="/register" method="post">
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button>Submit</button>
</form>
<br>
<button onclick="closeModal()">Close</button>
</div>
</div>

<script>
function openModal(){
    document.getElementById("modal").classList.add("active");
}
function closeModal(){
    document.getElementById("modal").classList.remove("active");
}
</script>
"""


# 📋 DASHBOARD
dashboard_page = base_style + """
<div class="stars"></div>

<div class="glass" style="width:450px; margin:50px auto; padding:20px;">
<h2 style="text-align:center;">Your Tasks</h2>

<form action="/add/{{user_id}}" method="post" style="text-align:center;">
<input name="task" placeholder="New Task" required>
<button>Add</button>
</form>

<div style="margin-top:20px;">
{% for task in tasks %}
<div class="glass task">
<span>{{task[2]}} ({{task[3]}})</span>
<div>
<a href="/complete/{{task[0]}}/{{user_id}}"><button>Done</button></a>
<a href="/delete/{{task[0]}}/{{user_id}}"><button>Delete</button></a>
</div>
</div>
{% endfor %}
</div>

<div style="text-align:center; margin-top:20px;">
<a href="/logout"><button>Logout</button></a>
</div>
</div>

<!-- ✔ success animation -->
<div id="success" class="success-overlay">
<div class="circle">
<svg class="checkmark" viewBox="0 0 52 52">
<path d="M14 27 L22 35 L38 18"/>
</svg>
</div>
</div>

<script>
setTimeout(()=>{
    let s = document.getElementById("success");
    if(s) s.style.display="none";
},1000);
</script>
"""


# ROUTES
@app.route('/')
def home():
    return render_template_string(login_page)


@app.route('/register', methods=['POST'])
def register():
    cursor.execute("INSERT INTO users VALUES (NULL, ?, ?)",
                   (request.form['username'], request.form['password']))
    db.commit()
    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (request.form['username'], request.form['password']))
    user = cursor.fetchone()
    return redirect(f'/dashboard/{user[0]}') if user else "Invalid Login"


@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    cursor.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
    return render_template_string(
        dashboard_page,
        tasks=cursor.fetchall(),
        user_id=user_id
    )


@app.route('/add/<int:user_id>', methods=['POST'])
def add_task(user_id):
    cursor.execute("INSERT INTO tasks VALUES (NULL, ?, ?, ?)",
                   (user_id, request.form['task'], "pending"))
    db.commit()
    return redirect(f'/dashboard/{user_id}')


@app.route('/complete/<int:task_id>/<int:user_id>')
def complete_task(task_id, user_id):
    cursor.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    db.commit()
    return redirect(f'/dashboard/{user_id}')


@app.route('/delete/<int:task_id>/<int:user_id>')
def delete_task(task_id, user_id):
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    db.commit()
    return redirect(f'/dashboard/{user_id}')


@app.route('/logout')
def logout():
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
