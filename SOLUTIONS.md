# Разбор и исправления

## SQLi в /login
Проблема: конкатенация строки в SQL.
Fix:
```python
rows = conn.execute("SELECT * FROM users WHERE name = ?", (user,)).fetchall()
```

## XSS в /search
Проблема: вывод пользовательского ввода без экранирования.
Fix: использовать шаблонизатор с автоэкранированием (Jinja2) или `markupsafe.escape(q)`.
