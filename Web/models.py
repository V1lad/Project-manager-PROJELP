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
    
    chatRoom = db.relationship('ChatRoom', uselist=False)
    allowedUsers = db.Column(db.JSON, default='[]')
    subprojects = db.relationship('SubProject')
    
    # Корректно удаляет проект и его элементы
    def delete(self, db):
        for subproject in self.subprojects:
            subproject.delete(db)
            
        chatRoom = self.chatRoom
        chatRoom.delete(db)
            
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
    
    created_at = db.Column(db.String(31))
    planned_at = db.Column(db.String(31))
    
    # done ready abandoned in_progress
    title = db.Column(db.String, default='')
    content = db.Column(db.String, default='')
    status = db.Column(db.String, default='')
    priority = db.Column(db.Integer, default=0)
    progress = db.Column(db.Integer, default=0)
    progress_coefficient = db.Column(db.Integer, default=1)
    
    chatRoom = db.relationship('ChatRoom', uselist=False)
    
    # Корректно удаляет запись
    def delete(self, db):
        chatRoom = self.chatRoom
        if chatRoom:
            chatRoom.delete(db)
        db.session.delete(self)

    def next_status(self):
        statuses = ["ready", "in_progress", "done", "abandoned"]
        self.status = statuses[(statuses.index(self.status) + 1) % 4]
    
# Описывает сущность комната чата
class ChatRoom(db.Model):
    __tablename__ = 'chatrooms'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    
    parent_project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    parent_note_id = db.Column(db.Integer, db.ForeignKey('notes.id'))
    type = db.Column(db.String, default='ProjectChat')
        
    messages = db.relationship('Message')

    # Корректно удаляет себя
    def delete(self, db):
        for message in self.messages:
            message.delete(db)
        db.session.delete(self)
        

# Описывает сущность комната чата
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    text = db.Column(db.String(255), default='')
    
    created_at = db.Column(db.String(31))
    author_id = db.Column(db.Integer)
    author_name = db.Column(db.String(150))
    
    parent_id = db.Column(db.Integer, db.ForeignKey('chatrooms.id'))
    
    # Корректно удаляет себя
    def delete(self, db):
        db.session.delete(self)