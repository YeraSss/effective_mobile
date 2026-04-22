from fastapi import FastAPI

from app.api import auth, resources, users

app = FastAPI(
    title="Система аутентификации и авторизации",
    description=(
        "Кастомная RBAC-система: регистрация, вход/выход, управление профилем, "
        "разграничение прав доступа к ресурсам."
    ),
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(resources.router)


@app.get("/", tags=["Статус"])
def root():
    return {"status": "ok", "docs": "/docs"}
