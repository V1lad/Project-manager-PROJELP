from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from json import loads
from flask_mail import Mail, Message
from datetime import date
from .functions import get_date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import sys

db = SQLAlchemy()
DB_NAME = "database.db"

# Создание приложения
basedir = path.abspath(path.dirname(__file__))
        
app = Flask(__name__)    
# Конфигурируем базу данных
with open("web/keys/secret_key.txt", "r") as file:
    app.config['SECRET_KEY'] = file.readline()
    
with open("web/keys/mail.txt", "r") as file:
    app.config['MAIL_SERVER'] = 'smtp.mail.ru'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = 'projelp.notifications@mail.ru'
    app.config['MAIL_PASSWORD'] = file.readline()
    app.config['MAIL_DEFAULT_SENDER'] = 'projelp.notifications@mail.ru'
    
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + path.join(basedir, DB_NAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

# Подключаем модели для базы данных
from .models import User, Notification, Note, SubProject, Project

mail = Mail(app)
db.init_app(app)

# Инициализация планировщика
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_jobstore('sqlalchemy', url=app.config['SQLALCHEMY_DATABASE_URI'])


def send_notifications():
    # print("TRIGGERED", file=sys.stdout)  
    with app.app_context():
        now = date.today()
        pending = Notification.query.filter(
            Notification.planned_at == now
        ).all()
        for notification in pending:
            try:
                note = Note.query.filter_by(id=int(notification.parent_id)).first()
                subproject = SubProject.query.filter_by(id=int(note.parent_id)).first()
                project = Project.query.filter_by(id=int(subproject.parent_id)).first()
                
                if note.notifications_enabled == "True":
                    msg = Message(
                        subject=f"Близится дедлайн {note.title}",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=['PVlad29092003@mail.ru']
                    )

                    msg.body = f"В проекте {project.name} в разделе {subproject.name} подходит к концу задача {note.title}. \
                        \nВыполнение задачи запланировано не позднее {get_date(note.planned_at)}. На данный момент задача выполнена на {note.progress}%, её статус - {note.get_str_status()}."

                    mail.send(msg)

                    db.session.delete(notification)
                    db.session.commit()
            except Exception as e:
                app.logger.error(f"Error sending notification {notification.id}: {str(e)}")
                db.session.rollback()
    return
 
scheduler.add_job(
    send_notifications,
    IntervalTrigger(seconds=10),
    id='notification_job',
    replace_existing=True
)

scheduler.start()
# Подключаем чертежи из других файлов
from .views import views
from .auth import auth
from .projects import projects

# Регистрируем чертежи с соответственными адресами в приложении
app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(projects, url_prefix='/')

# Создаём БД
with app.app_context():
    db.create_all() 

    # Создаём администратора 
    if not User.query.filter_by(id=1).first():
        with open("web/keys/admin_password.txt", "r") as file:
            admin = User(email="vlad@mail.ru", firstName="Vlad", password=file.readline(), is_admin="True") 
            db.session.add(admin)
            db.session.commit()


# Подключаем управление аутенификацией
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)  

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def get_app():
    return app