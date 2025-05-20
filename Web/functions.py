from json import loads
import re

# Возвращает True если у пользователя есть доступ к проекту
def has_access_to_project(user, project):
    if project.owner_id == user.id:
        return True

    if user.is_admin == "True":
        return True
    
    allowed_users = loads(project.allowedUsers)
    return [str(user.id), 0] in allowed_users or [str(user.id), 1] in allowed_users

# Возвращает True если у пользователя есть доступ к редактированию проекта
def has_redact_rights_to_project(user, project):
    if project.owner_id == user.id:
        return True

    if user.is_admin == "True":
        return True
    
    allowed_users = loads(project.allowedUsers)
    return [str(user.id), 1] in allowed_users



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

# Очистка названия для листа Excel
def clean_sheet_name(name):
    return re.sub(r'[\\/*?:[\]]', '', name[:30])