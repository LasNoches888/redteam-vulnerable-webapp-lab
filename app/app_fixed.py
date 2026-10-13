"""Исправленная версия учебного приложения: те же маршруты, но без уязвимостей из app.py.

Запуск локально:  python app_fixed.py   (слушает только 127.0.0.1:5000)
Сравните с app.py построчно — каждое отличие описано в SOLUTIONS.md и docs/owasp_mapping.md.
"""
import os
import sqlite3

from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users(id INTEGER, name TEXT, pass TEXT)")
    conn.execute("INSERT INTO users VALUES (1,'admin','s3cret')")
    conn.execute("INSERT INTO users VALUES (2,'bob','hunter2')")
    return conn


@app.after_request
def add_security_headers(response):
    # Вторая линия защиты от XSS и подмены типа содержимого
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/login")
def login():
    # ИСПРАВЛЕНО (SQL-инъекция): параметризованный запрос — ввод пользователя никогда не становится частью SQL.
    # ИСПРАВЛЕНО (утечка данных): возвращаем только id и имя, а не всю строку вместе с паролем.
    user = request.args.get("user", "")
    conn = db()
    rows = conn.execute("SELECT id, name FROM users WHERE name = ?", (user,)).fetchall()
    return {"result": rows}


@app.route("/search")
def search():
    # ИСПРАВЛЕНО (reflected XSS): вывод экранируется, <script> превращается в безвредный текст.
    q = request.args.get("q", "")
    return f"<h1>Результаты для: {escape(q)}</h1>"


if __name__ == "__main__":
    # Локальный интерфейс по умолчанию; для контейнера задайте LAB_HOST=0.0.0.0
    app.run(host=os.environ.get("LAB_HOST", "127.0.0.1"), port=5000)
