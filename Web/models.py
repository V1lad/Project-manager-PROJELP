from . import db
from flask_login import UserMixin
import sys

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
    progress = db.Column(db.Integer, default=0)
    
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

        return 
    
    def update_progress(self, db):
        max_progress = len(self.subprojects) * 100
        current_progress = 0
        
        for subproject in self.subprojects:  
            subproject.update_progress(db)
            current_progress += subproject.progress
            
        if max_progress == 0:
            self.progress = 0
        else:
            self.progress = round(current_progress * 100/max_progress)
            
        db.session.commit()
        return  
    
# Описывает сущность раздел
class SubProject(db.Model):
    __tablename__ = 'subprojects'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    
    parent_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    name = db.Column(db.String(150), default='')
    shortDescription = db.Column(db.String(255), default='')
    done = db.Column(db.String, default="False")
    progress = db.Column(db.Integer, default=0)
        
    notes = db.relationship('Note')
    
    def update_progress(self, db):
        max_coef = 0
        current_coef = 0
        
        for note in self.notes:  
            progress = int(note.progress)
            progress_coefficient = int(note.progress_coefficient)
            
            progress * progress_coefficient
                
            current_coef += progress * progress_coefficient
            max_coef += 100 * progress_coefficient
        
        if max_coef == 0:
            self.progress = 0
        else:   
            self.progress = round(current_coef * 100/max_coef)

        db.session.commit()
        return  

    # Корректно раздел и его элементы
    def delete(self, db):
        for note in self.notes:
            note.delete(db)
        db.session.delete(self)
        return
    
# Описывает сущность запись
class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    
    parent_id = db.Column(db.Integer, db.ForeignKey('subprojects.id'))
    
    planned_at = db.Column(db.String(31), default="")
    
    # done ready abandoned in_progress
    title = db.Column(db.String, default='')
    content = db.Column(db.String, default='')
    status = db.Column(db.String, default='')
    priority = db.Column(db.Integer, default=0)
    progress = db.Column(db.Integer, default=0)
    progress_coefficient = db.Column(db.Integer, default=1)
    notifications_enabled = db.Column(db.String, default='False')
    
    chatRoom = db.relationship('ChatRoom', uselist=False)
    notification = db.relationship('Notification', uselist=False)
    
    # Корректно удаляет запись
    def delete(self, db):
        chatRoom = self.chatRoom
        if chatRoom:
            chatRoom.delete(db)
            
        notification = self.notification
        if notification:
            notification.delete(db)
        db.session.delete(self)
        return
    
    def next_status(self):
        statuses = ["ready", "in_progress", "done", "abandoned"]
        self.status = statuses[(statuses.index(self.status) + 1) % 4]
        
        if self.status == "done":
            self.progress = 100
    
    def get_str_status(self):
        if self.status == "ready":
            return "не начата"
        elif self.status == "in_progress":
            return "в работе"
        elif self.status == "done":
            return "выполнена"
        else:
            return "отложена"
        
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
        return

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
        return
    
# Описывает сущность уведомление
class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    
    planned_at = db.Column(db.String)
    
    parent_id = db.Column(db.Integer, db.ForeignKey('notes.id'))
    
    # Корректно удаляет себя
    def delete(self, db):
        db.session.delete(self)
        return