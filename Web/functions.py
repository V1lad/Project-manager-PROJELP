from json import loads
from .models import Project, SubProject, Note

# Возвращает True если у пользователя есть доступ к проекту
def has_access_to_project(user, project):
    if project.owner_id == user.id:
        return True
    else:
        allowed_users = loads(project.allowedUsers)
        if str(user.id) in allowed_users:
            return True
        else:
            return False
        
