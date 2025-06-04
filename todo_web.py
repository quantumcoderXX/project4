from flask import Flask, render_template_string, request, redirect, url_for, flash
import json
import os
from datetime import datetime

# --- Constants and Setup ---
TASKS_FILE = "tasks.json"  # ✅ File for storing tasks
DATE_FORMAT = "%Y-%m-%d"    # ✅ Date format used in the app

# --- Data Logic (reused from CLI version) ---
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []  # ✅ Return empty if no file exists
    with open(TASKS_FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def generate_task_id(tasks):
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1  # ✅ Auto-increment task ID

def add_task(title, due, priority, category, note):
    tasks = load_tasks()
    task = {
        "id": generate_task_id(tasks),
        "title": title,
        "due": due,
        "priority": priority,
        "category": category or "General",
        "note": note or "",
        "done": False,
        "created": datetime.now().strftime(DATE_FORMAT),
        "archived": False
    }
    tasks.append(task)
    save_tasks(tasks)

def update_task(task_id, title, due, priority, category, note):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["title"] = title
            task["due"] = due
            task["priority"] = priority
            task["category"] = category
            task["note"] = note
            break  # ✅ Stop loop after match
    save_tasks(tasks)

def mark_done(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            break
    save_tasks(tasks)

def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]  # ✅ Filter out task
    save_tasks(tasks)

def archive_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["archived"] = True
            break
    save_tasks(tasks)

def unarchive_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["archived"] = False
            break
    save_tasks(tasks)

def sort_tasks(tasks):
    def sort_key(task):
        try:
            due = datetime.strptime(task["due"], DATE_FORMAT)
        except Exception:
            due = datetime.max
        priority_map = {"high": 0, "medium": 1, "low": 2}
        return (task["archived"], task["done"], due, priority_map.get(task["priority"], 1))
    return sorted(tasks, key=sort_key)

# --- Flask Web App Setup ---
app = Flask(__name__)
app.secret_key = "change_this_secret"  # Needed for flash messages

# --- HTML Template ---
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>To-Do List Web</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #f0f0f0; }
        tr.done { text-decoration: line-through; color: #888; }
        .archived { background: #f9e6e6; }
        .overdue { background: #ffe0e0; }
        .actions form { display: inline; }
        .add-form { margin-bottom: 20px; }
        .edit-form { margin-bottom: 20px; background: #f5f5f5; padding: 10px; }
    </style>
</head>
<body>
    <h1>To-Do List (Web)</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>
        {% for message in messages %}
          <li style="color: red;">{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <!-- Edit Task Form -->
    {% if edit_task %}
    <form class="edit-form" method="post" action="{{ url_for('edit', task_id=edit_task.id) }}">
        <strong>Edit Task:</strong>
        <input name="title" value="{{ edit_task.title }}" required>
        <input name="due" value="{{ edit_task.due }}">
        <select name="priority">
            <option value="low" {% if edit_task.priority == 'low' %}selected{% endif %}>Low</option>
            <option value="medium" {% if edit_task.priority == 'medium' %}selected{% endif %}>Medium</option>
            <option value="high" {% if edit_task.priority == 'high' %}selected{% endif %}>High</option>
        </select>
        <input name="category" value="{{ edit_task.category }}">
        <input name="note" value="{{ edit_task.note }}">
        <button type="submit">Save</button>
        <a href="{{ url_for('index') }}">Cancel</a>
    </form>
    {% endif %}

    <!-- Task Creation Form -->
    <form class="add-form" method="post" action="{{ url_for('add') }}">
        <input name="title" placeholder="Title" required>
        <input name="due" placeholder="Due (YYYY-MM-DD)">
        <select name="priority">
            <option value="low">Low</option>
            <option value="medium" selected>Medium</option>
            <option value="high">High</option>
        </select>
        <input name="category" placeholder="Category">
        <input name="note" placeholder="Note">
        <button type="submit">Add Task</button>
    </form>

    <!-- Task Display Table -->
    <table>
        <tr>
            <th>Title</th><th>Due</th><th>Priority</th><th>Category</th><th>Note</th>
            <th>Done</th><th>Archived</th><th>Actions</th>
        </tr>
        {% for task in tasks %}
        <tr class="{% if task.done %}done{% endif %} {% if task.archived %}archived{% endif %} {% if not task.done and not task.archived and task.due and task.due != 'No due date' and task.due < now %}overdue{% endif %}">
            <td>{{ task.title }}</td>
            <td>{{ task.due }}</td>
            <td>{{ task.priority }}</td>
            <td>{{ task.category }}</td>
            <td>{{ task.note }}</td>
            <td>{{ "Yes" if task.done else "No" }}</td>
            <td>{{ "Yes" if task.archived else "No" }}</td>
            <td class="actions">
                {% if not task.done %}
                <form method="post" action="{{ url_for('mark_done_route', task_id=task.id) }}"><button>Done</button></form>
                {% endif %}
                <form method="post" action="{{ url_for('delete', task_id=task.id) }}"><button>Delete</button></form>
                {% if not task.archived %}
                <form method="post" action="{{ url_for('archive', task_id=task.id) }}"><button>Archive</button></form>
                {% else %}
                <form method="post" action="{{ url_for('unarchive', task_id=task.id) }}"><button>Unarchive</button></form>
                {% endif %}
                <form method="get" action="{{ url_for('edit', task_id=task.id) }}"><button>Edit</button></form>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# --- Flask Routes ---
@app.route("/", methods=["GET"])
def index():
    tasks = sort_tasks(load_tasks())
    now = datetime.now().strftime(DATE_FORMAT)
    return render_template_string(HTML, tasks=tasks, now=now, edit_task=None)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    due = request.form.get("due", "").strip() or "No due date"
    priority = request.form.get("priority", "medium")
    category = request.form.get("category", "General")
    note = request.form.get("note", "")
    if title:
        add_task(title, due, priority, category, note)
    else:
        flash("Title is required.")
    return redirect(url_for("index"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        flash("Task not found.")
        return redirect(url_for("index"))
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        due = request.form.get("due", "").strip() or "No due date"
        priority = request.form.get("priority", "medium")
        category = request.form.get("category", "General")
        note = request.form.get("note", "")
        if title:
            update_task(task_id, title, due, priority, category, note)
            return redirect(url_for("index"))
        else:
            flash("Title is required.")
    now = datetime.now().strftime(DATE_FORMAT)
    return render_template_string(HTML, tasks=sort_tasks(tasks), now=now, edit_task=task)

@app.route("/mark_done/<int:task_id>", methods=["POST"])
def mark_done_route(task_id):
    mark_done(task_id)
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    delete_task(task_id)
    return redirect(url_for("index"))

@app.route("/archive/<int:task_id>", methods=["POST"])
def archive(task_id):
    archive_task(task_id)
    return redirect(url_for("index"))

@app.route("/unarchive/<int:task_id>", methods=["POST"])
def unarchive(task_id):
    unarchive_task(task_id)
    return redirect(url_for("index"))

# --- Run App ---
if __name__ == "__main__":
    app.run(debug=True)  # ✅ Run in debug mode for development

