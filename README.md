# Тестовое задание: аутентификация и авторизация

FastAPI-приложение с собственной системой управления доступом. Без готовых auth-библиотек — JWT, хэширование паролей и проверка прав написаны вручную.

## Стек

FastAPI, SQLAlchemy 2.0, Alembic, SQLite, PyJWT, bcrypt, Pydantic v2.

SQLite выбрал ради простоты — база создаётся сама, ничего дополнительно ставить не нужно.

## Запуск

```bash
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python seeds.py
uvicorn app.main:app --reload
```

Swagger: http://localhost:8000/docs

## Схема БД

Таблиц шесть.

`users` — сами пользователи: UUID, имя/фамилия/отчество, email, хэш пароля, is_active и даты. Поле is_active=False означает мягкое удаление — запись остаётся в базе, войти нельзя.

`roles` — три роли: admin, moderator, user.

`permissions` — атомарные разрешения, каждое это пара resource + action. Например, `reports:read` или `admin_panel:read`. Дублировать нельзя — на эту пару стоит уникальный constraint.

`role_permissions` и `user_roles` — две M2M-таблицы: кто какую роль имеет и у какой роли какие разрешения.

`revoked_tokens` — чёрный список токенов после logout. Каждый JWT содержит claim `jti`; при выходе он сюда пишется и токен перестаёт работать, даже если ещё не истёк по времени.

## Права доступа

Схема: пользователь → роли → разрешения (ресурс + действие).

```
                  admin   moderator   user
users read          +         +        +
users write         +
users delete        +
reports read        +         +
admin_panel read    +
```

Проверка реализована в `app/services/permission.py` одним SQL-запросом через JOIN по трём таблицам. Нет токена или он недействителен — 401. Токен есть, но прав нет — 403.

## Аутентификация

Два JWT-токена: access (15 минут) и refresh (7 дней). При logout `jti` уходит в `revoked_tokens`. Через `/auth/refresh` можно получить новый access-токен — при этом старый refresh тоже отзывается и выдаётся свежая пара.

Мягкое удаление через `DELETE /users/me` ставит is_active=False и отзывает текущий токен. Данные в базе остаются.

## Эндпоинты

```
POST /auth/register
POST /auth/login
POST /auth/logout
POST /auth/refresh

GET    /users/me
PATCH  /users/me
DELETE /users/me

GET /resources/users        — требует users:read
GET /resources/reports      — требует reports:read
GET /resources/admin-panel  — требует admin_panel:read
```

Три ресурсных эндпоинта нужны для демонстрации RBAC: у каждого своё требуемое разрешение, удобно проверять разницу между ролями.

## Тестовые данные

После `python seeds.py`:

```
admin@test.com  / Admin1234!  — admin
moder@test.com  / Moder1234!  — moderator
user@test.com   / User1234!   — user
```

## Структура проекта

```
app/
  main.py
  config.py
  database.py
  models/           user, role, permission, token
  schemas/          user, auth
  api/              auth, users, resources
  services/         auth (JWT + bcrypt), permission (RBAC)
  core/
    dependencies.py   get_current_user, require_permission
alembic/
seeds.py
requirements.txt
.env.example
```
