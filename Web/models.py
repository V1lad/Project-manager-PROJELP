from . import db
from flask_login import UserMixin

# Описывает сущность пользователь
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String(150), unique=True)
    firstName = db.Column(db.String(150), default='')
    password = db.Column(db.String(150))
    
    addedProjects = db.Column(db.JSON, default='[]')

    ownedProjects = db.relationship('Project')

# Описывает сущность проект
class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    name = db.Column(db.String(150), default='')
    shortDescription = db.Column(db.String(255), default='')
    fullDescription = db.Column(db.String(255), default='')
    goal = db.Column(db.String(255), default='')
    done = db.Column(db.String, default="False")
    
    allowedUsers = db.Column(db.JSON, default='[]')
    subprojects = db.relationship('SubProject')
    
    # Корректно удаляет проект и его элементы
    def delete(self, db):
        for subproject in self.subprojects:
            subproject.delete(db)
        db.session.delete(self)
        
# Описывает сущность раздел
class SubProject(db.Model):
    __tablename__ = 'subprojects'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    
    parent_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    name = db.Column(db.String(150), default='')
    shortDescription = db.Column(db.String(255), default='')
    done = db.Column(db.String, default="False")
    
    notes = db.relationship('Note')
    
    # Корректно раздел и его элементы
    def delete(self, db):
        for note in self.notes:
            note.delete(db)
        db.session.delete(self)
        
# Описывает сущность запись
class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    
    parent_id = db.Column(db.Integer, db.ForeignKey('subprojects.id'))
    
    content = db.Column(db.String, default='')
    done = db.Column(db.String, default="False")
    
     # Корректно удаляет запись
    def delete(self, db):
        db.session.delete(self)
    