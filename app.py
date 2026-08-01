from __future__ import annotations

import random
import sqlite3
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "tiny_museum.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-only"

PROMPTS = [
    "Use it once today.",
    "Notice one detail you usually miss.",
    "Write why you kept it.",
    "Move it to a better place.",
    "Tell someone its story.",
    "Imagine giving it away. What would you miss?",
    "Describe it without naming it.",
    "Take a photo from an unusual angle.",
]


def get_db() -> sqlite3.Connection:
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db() -> None:
    with get_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS objects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                emoji TEXT NOT NULL DEFAULT '✨',
                color TEXT NOT NULL DEFAULT '#F2C879',
                memory TEXT,
                location TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                object_id INTEGER NOT NULL,
                prompt TEXT NOT NULL,
                observation TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (object_id) REFERENCES objects(id) ON DELETE CASCADE
            );
            """
        )


def object_or_404(object_id: int) -> sqlite3.Row:
    with get_db() as db:
        item = db.execute("SELECT * FROM objects WHERE id = ?", (object_id,)).fetchone()
    if item is None:
        abort(404)
    return item


@app.route("/")
def gallery():
    with get_db() as db:
        objects = db.execute("SELECT * FROM objects ORDER BY created_at DESC").fetchall()
        experiment_count = db.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
    return render_template("gallery.html", objects=objects, experiment_count=experiment_count)


@app.route("/objects/new", methods=["GET", "POST"])
def add_object():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Give the object a name.")
            return render_template("add.html", form=request.form)
        with get_db() as db:
            cursor = db.execute(
                """INSERT INTO objects (name, emoji, color, memory, location)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    name,
                    request.form.get("emoji", "✨").strip() or "✨",
                    request.form.get("color", "#F2C879"),
                    request.form.get("memory", "").strip(),
                    request.form.get("location", "").strip(),
                ),
            )
        return redirect(url_for("object_detail", object_id=cursor.lastrowid))
    return render_template("add.html", form={})


@app.route("/objects/<int:object_id>")
def object_detail(object_id: int):
    item = object_or_404(object_id)
    with get_db() as db:
        experiments = db.execute(
            "SELECT * FROM experiments WHERE object_id = ? ORDER BY created_at DESC",
            (object_id,),
        ).fetchall()
    return render_template("detail.html", item=item, experiments=experiments)


@app.route("/surprise")
def surprise():
    with get_db() as db:
        objects = db.execute("SELECT * FROM objects").fetchall()
    if not objects:
        flash("Add an object first.")
        return redirect(url_for("add_object"))
    return render_template("experiment.html", item=random.choice(objects), prompt=random.choice(PROMPTS))


@app.route("/experiments", methods=["POST"])
def save_experiment():
    object_id = int(request.form["object_id"])
    object_or_404(object_id)
    with get_db() as db:
        db.execute(
            "INSERT INTO experiments (object_id, prompt, observation) VALUES (?, ?, ?)",
            (object_id, request.form["prompt"], request.form.get("observation", "").strip()),
        )
    flash("Experiment saved.")
    return redirect(url_for("object_detail", object_id=object_id))


init_db()

if __name__ == "__main__":
    app.run(debug=True)

