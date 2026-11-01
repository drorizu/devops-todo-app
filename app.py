
import os
import sqlite3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "tasks.db")
# Testing GitHub Actions CI/CD pipeline
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>DevOps To-Do App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 40px 15px;
        }
        .container {
            max-width: 600px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px #0001;
        }
        h1 { color: #1e293b; }
        form.add {
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 12px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
        }
        button {
            padding: 10px 14px;
            border: 0;
            border-radius: 6px;
            cursor: pointer;
            background: #2563eb;
            color: white;
        }
        .task {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            padding: 15px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        .completed {
            text-decoration: line-through;
            color: #94a3b8;
        }
        .delete { background: #dc2626; }
        .small { font-size: 12px; color: #64748b; }
    </style>
</head>
<body>
<div class="container">
    <h1>My DevOps To-Do List</h1>
    <p>Learn DevOps one task at a time.</p>

    <form class="add" method="POST" action="/add">
        <input name="title" placeholder="Enter a new task..." required>
        <button type="submit">Add</button>
    </form>

    <h3>My Tasks</h3>

    {% for task in tasks %}
    <div class="task">
        <div>
            <span class="{{ 'completed' if task[2] else '' }}">
                {{ task[1] }}
            </span>
        </div>
        <div style="display:flex; gap:6px">
            <form method="POST" action="/toggle/{{ task[0] }}">
                <button type="submit">
                    {{ 'Undo' if task[2] else 'Done' }}
                </button>
            </form>
            <form method="POST" action="/delete/{{ task[0] }}">
                <button class="delete" type="submit">Delete</button>
            </form>
        </div>
    </div>
    {% else %}
        <p>No tasks yet. Add your first task!</p>
    {% endfor %}

    <p class="small">DevOps learning project | Flask + SQLite</p>
</div>
</body>
</html>
"""


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)
    return connection


@app.route("/")
def home():
    connection = get_db()
    tasks = connection.execute(
        "SELECT id, title, completed FROM tasks ORDER BY id DESC"
    ).fetchall()
    connection.close()
    return render_template_string(HTML, tasks=tasks)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()

    if title:
        connection = get_db()
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)", (title,)
        )
        connection.commit()
        connection.close()

    return redirect("/")


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle(task_id):
    connection = get_db()
    connection.execute(
        "UPDATE tasks SET completed = 1 - completed WHERE id = ?",
        (task_id,)
    )
    connection.commit()
    connection.close()
    return redirect("/")


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    connection = get_db()
    connection.execute(
        "DELETE FROM tasks WHERE id = ?", (task_id,)
    )
    connection.commit()
    connection.close()
    return redirect("/")


@app.route("/health")
def health():
    try:
        connection = get_db()
        connection.execute("SELECT 1")
        connection.close()
        return {"status": "healthy"}, 200
    except sqlite3.Error:
        return {"status": "unhealthy"}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
