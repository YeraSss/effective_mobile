from fastapi import APIRouter, Depends

from app.core.dependencies import require_permission
from app.models.user import User

router = APIRouter(prefix="/resources", tags=["Демо-ресурсы (RBAC)"])


@router.get("/users")
def get_users_resource(current_user: User = Depends(require_permission("users", "read"))):
    """
    Демо-ресурс: список пользователей.
    Требует разрешение users:read (есть у ролей: admin, moderator, user).
    """
    return {
        "resource": "users",
        "action": "read",
        "accessed_by": current_user.email,
        "message": "Доступ к списку пользователей разрешён",
    }


@router.get("/reports")
def get_reports(current_user: User = Depends(require_permission("reports", "read"))):
    """
    Демо-ресурс: отчёты.
    Требует разрешение reports:read (есть у ролей: admin, moderator).
    """
    return {
        "resource": "reports",
        "action": "read",
        "accessed_by": current_user.email,
        "message": "Доступ к отчётам разрешён",
    }


@router.get("/admin-panel")
def get_admin_panel(current_user: User = Depends(require_permission("admin_panel", "read"))):
    """
    Демо-ресурс: административная панель.
    Требует разрешение admin_panel:read (только роль: admin).
    """
    return {
        "resource": "admin_panel",
        "action": "read",
        "accessed_by": current_user.email,
        "message": "Добро пожаловать в панель администратора!",
    }
