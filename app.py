from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)
DB = "workouts.db"


def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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


def add_workout(date_val, exercise, sets, reps, weight, note):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO workouts (date, exercise, sets, reps, weight, note) VALUES (?, ?, ?, ?, ?, ?)",
        (date_val, exercise, sets, reps, weight, note)
    )
    conn.commit()
    conn.close()

def get_workouts():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workouts ORDER BY date DESC, id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_workout(workout_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
    conn.commit()
    conn.close()


@app.route("/")
def index():
    workouts = get_workouts()
    return render_template("index.html", today=date.today().isoformat(), workouts=workouts)


@app.route("/add", methods=["POST"])
def add():
    date_val = request.form.get("date")
    exercise = request.form.get("exercise")
    sets = int(request.form.get("sets"))
    reps = int(request.form.get("reps"))

    weight_str = request.form.get("weight", "").strip()
    weight = float(weight_str) if weight_str else None

    note = request.form.get("note", "")

    if date_val and exercise and sets and reps:
        add_workout(date_val, exercise, sets, reps, weight, note)

    return redirect("/")

@app.route("/delete/<int:workout_id>")
def delete(workout_id):
    delete_workout(workout_id)
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)