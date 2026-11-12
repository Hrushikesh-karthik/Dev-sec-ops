import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)

# INTENTIONALLY INSECURE FOR THE WORKSHOP:
# Gitleaks should flag this fake-looking demo credential.
# Never put real credentials in source code.
DEMO_API_TOKEN = "ghp_123456789012345678901234567890123456"

# INTENTIONALLY WEAK FOR THE WORKSHOP. Replace with an environment variable.
app.secret_key = "devsecops-demo-secret"

DB_PATH = os.environ.get("DB_PATH", "workshop.db")


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL
            )
        """)
        db.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            ("student", "Password123!")
        )
        count = db.execute("SELECT COUNT(*) AS count FROM products").fetchone()["count"]
        if count == 0:
            db.executemany(
                "INSERT INTO products (name, description) VALUES (?, ?)",
                [
                    ("Laptop", "A lightweight demo laptop"),
                    ("Keyboard", "A mechanical demo keyboard"),
                    ("Monitor", "A 24-inch demo monitor"),
                ],
            )


@app.route("/")
def index():
    return render_template("index.html", username=session.get("username"))


@app.route("/login", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # INTENTIONALLY VULNERABLE:
        # User input is concatenated directly into SQL (SQL injection).
        query = (
            "SELECT * FROM users WHERE username = '"
            + username
            + "' AND password = '"
            + password
            + "'"
        )
        with get_db() as db:
            user = db.execute(query).fetchone()

        if user:
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        message = "Invalid username or password"

    return render_template("login.html", message=message)


@app.route("/search")
def search():
    term = request.args.get("q", "")
    # INTENTIONALLY VULNERABLE:
    # The template renders this value as trusted HTML (XSS).
    return render_template("search.html", term=term, unsafe=True)


@app.route("/dashboard")
def dashboard():
    if not session.get("username"):
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])


@app.route("/health")
def health():
    return {"status": "ok"}, 200


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    initialize_database()
    # Debug mode is intentionally enabled for the workshop finding.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
