"""Намеренно уязвимое приложение — ТОЛЬКО для локальной учебной среды."""
import sqlite3
from flask import Flask, request

app = Flask(__name__)

def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users(id INTEGER, name TEXT, pass TEXT)")
    conn.execute("INSERT INTO users VALUES (1,'admin','s3cret')")
    conn.execute("INSERT INTO users VALUES (2,'bob','hunter2')")
    return conn

@app.route("/login")
def login():
    # УЯЗВИМО: SQL-инъекция (учебная). Fix: параметризованный запрос.
    user = request.args.get("user", "")
    conn = db()
    q = f"SELECT * FROM users WHERE name = '{user}'"
    rows = conn.execute(q).fetchall()
    return {"result": rows}

@app.route("/search")
def search():
    # УЯЗВИМО: reflected XSS (учебная). Fix: экранирование вывода.
    q = request.args.get("q", "")
    return f"<h1>Результаты для: {q}</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
