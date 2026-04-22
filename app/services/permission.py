from sqlalchemy.orm import Session

from app.models.user import User


def has_permission(user: User, resource: str, action: str, db: Session) -> bool:
    """
    Проверяет, есть ли у пользователя разрешение на действие с ресурсом.
    Загружает роли пользователя и их разрешения из БД.
    """
    # Перезагружаем пользователя с ролями и разрешениями (eager load)
    from app.models.role import Role
    from app.models.permission import Permission

    result = (
        db.query(Permission)
        .join(Permission.roles)
        .join(Role.users)
        .filter(
            User.id == user.id,
            Permission.resource == resource,
            Permission.action == action,
        )
        .first()
    )
    return result is not None
