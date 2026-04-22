"""
Скрипт заполнения базы данных тестовыми данными.
Запуск: python seeds.py

Создаёт роли, разрешения и трёх тестовых пользователей:
  admin@test.com  / Admin1234!  — роль admin
  moder@test.com  / Moder1234!  — роль moderator
  user@test.com   / User1234!   — роль user
"""

from app.database import SessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.services.auth import hash_password

# Матрица разрешений: роль → список (ресурс, действие)
ROLE_PERMISSIONS: dict[str, list[tuple[str, str]]] = {
    "admin": [
        ("users", "read"),
        ("users", "write"),
        ("users", "delete"),
        ("reports", "read"),
        ("admin_panel", "read"),
    ],
    "moderator": [
        ("users", "read"),
        ("reports", "read"),
    ],
    "user": [
        ("users", "read"),
    ],
}

TEST_USERS = [
    {
        "first_name": "Алексей",
        "last_name": "Иванов",
        "middle_name": "Петрович",
        "email": "admin@test.com",
        "password": "Admin1234!",
        "role": "admin",
    },
    {
        "first_name": "Мария",
        "last_name": "Сидорова",
        "middle_name": "Викторовна",
        "email": "moder@test.com",
        "password": "Moder1234!",
        "role": "moderator",
    },
    {
        "first_name": "Дмитрий",
        "last_name": "Козлов",
        "middle_name": None,
        "email": "user@test.com",
        "password": "User1234!",
        "role": "user",
    },
]


def seed():
    db = SessionLocal()
    try:
        # --- Разрешения ---
        all_pairs: set[tuple[str, str]] = set()
        for perms in ROLE_PERMISSIONS.values():
            all_pairs.update(perms)

        permission_map: dict[tuple[str, str], Permission] = {}
        for resource, action in all_pairs:
            perm = db.query(Permission).filter(
                Permission.resource == resource, Permission.action == action
            ).first()
            if not perm:
                perm = Permission(resource=resource, action=action)
                db.add(perm)
                db.flush()
            permission_map[(resource, action)] = perm

        # --- Роли ---
        role_map: dict[str, Role] = {}
        role_descriptions = {
            "admin": "Полный доступ ко всем ресурсам системы",
            "moderator": "Чтение пользователей и отчётов",
            "user": "Базовый доступ к собственному профилю",
        }
        for role_name, perms in ROLE_PERMISSIONS.items():
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name, description=role_descriptions[role_name])
                db.add(role)
                db.flush()
            # Назначаем разрешения роли
            role.permissions = [permission_map[p] for p in perms]
            role_map[role_name] = role

        # --- Пользователи ---
        for u in TEST_USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                print(f"[пропуск] Пользователь {u['email']} уже существует")
                continue
            user = User(
                first_name=u["first_name"],
                last_name=u["last_name"],
                middle_name=u["middle_name"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
            )
            user.roles = [role_map[u["role"]]]
            db.add(user)
            print(f"[создан] {u['email']} (роль: {u['role']})")

        db.commit()
        print("\nБаза данных успешно заполнена тестовыми данными.")
        print("\nТестовые учётные записи:")
        print("  admin@test.com  / Admin1234!  — admin")
        print("  moder@test.com  / Moder1234!  — moderator")
        print("  user@test.com   / User1234!   — user")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
