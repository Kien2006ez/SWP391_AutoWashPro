from app.services.auth_service import users


def _hide_password(user: dict) -> dict:
    return {k: v for k, v in user.items() if k != "password"}


def get_all_users():
    return [_hide_password(u) for u in users]


def get_user_by_id(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return _hide_password(user)
    return None


def update_user_role(user_id: int, role: str):
    for user in users:
        if user["id"] == user_id:
            user["role"] = role
            return _hide_password(user)
    return None


def update_user_status(user_id: int, status: str):
    for user in users:
        if user["id"] == user_id:
            user["status"] = status
            return _hide_password(user)
    return None


def delete_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            users.remove(user)
            return True
    return False
