from json import loads
from .models import Project, SubProject, Note

# Возвращает True если у пользователя есть доступ к проекту
def has_access_to_project(user, project):
    if project.owner_id == user.id:
        return True

    allowed_users = loads(project.allowedUsers)
    return str(user.id) in allowed_users

# Приводит время из БД к виду для показа на странице
def get_time(time_str):
    # 2025-05-16-18-21 --> 16:18 16.05.2025
    dates = time_str.split("-")
    return f"{dates[3]}:{dates[4]} {'.'.join(dates[0:3][::-1])}"

# Приводит дату из БД к виду для показа на странице
def get_date(time_str):
    # 2025-05-16 --> 16.05.2025
    dates = time_str.split("-")
    return f"{'.'.join(dates[0:3][::-1])}"