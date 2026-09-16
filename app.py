from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "поменяй-этот-ключ-на-что-то-случайное"
DB = "workouts.db"


# --- Создание базы и таблиц ---
def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL,
            note TEXT
        )
    """)

    conn.commit()
    conn.close()


# --- Работа с пользователями ---
def get_user_by_name(username):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def create_user(username, password):
    password_hash = generate_password_hash(password)
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    conn.commit()
    conn.close()


# --- Работа с тренировками ---
def add_workout(user_id, date_val, exercise, sets, reps, weight, note):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO workouts (user_id, date, exercise, sets, reps, weight, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, date_val, exercise, sets, reps, weight, note)
    )
    conn.commit()
    conn.close()


def get_workouts(user_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM workouts WHERE user_id = ? ORDER BY date DESC, id DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_workout(workout_id, user_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM workouts WHERE id = ? AND user_id = ?",
        (workout_id, user_id)
    )
    conn.commit()
    conn.close()


# --- Проверка авторизации ---
def is_logged_in():
    return "user_id" in session


# --- Маршруты ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if not username or not password:
            return render_template("register.html", error="Заполни все поля")

        if password != password2:
            return render_template("register.html", error="Пароли не совпадают")

        if len(password) < 6:
            return render_template("register.html", error="Пароль минимум 6 символов")

        if get_user_by_name(username):
            return render_template("register.html", error="Такое имя уже занято")

        create_user(username, password)
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_name(username)

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect("/")
        else:
            return render_template("login.html", error="Неверное имя или пароль")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
def index():
    if not is_logged_in():
        return redirect("/login")

    workouts = get_workouts(session["user_id"])
    return render_template(
        "index.html",
        today=date.today().isoformat(),
        workouts=workouts,
        username=session["username"]
    )


@app.route("/add", methods=["POST"])
def add():
    if not is_logged_in():
        return redirect("/login")

    date_val = request.form.get("date")
    exercise = request.form.get("exercise")
    sets = int(request.form.get("sets"))
    reps = int(request.form.get("reps"))

    weight_str = request.form.get("weight", "").strip()
    weight = float(weight_str) if weight_str else None

    note = request.form.get("note", "")

    if date_val and exercise and sets and reps:
        add_workout(session["user_id"], date_val, exercise, sets, reps, weight, note)

    return redirect("/")


@app.route("/delete/<int:workout_id>")
def delete(workout_id):
    if not is_logged_in():
        return redirect("/login")

    delete_workout(workout_id, session["user_id"])
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)