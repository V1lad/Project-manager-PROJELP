from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from flask_login import login_required, current_user
from .models import Project, User, SubProject, Note
from .functions import has_access_to_project
import json

DB_MAX_INT = 10000000000000000
projects = Blueprint('projects', __name__)

# Показывает все ваши проекты
@projects.route('/projects', methods=["GET"])
@login_required
def allProjects():
    
    projects = current_user.ownedProjects
    
    return render_template("projects.html", user=current_user, available_projects = projects)

# Управляет функционалом по редакитированию информации о конкретном проекте
@projects.route('/projects/<int:index>/redact', methods=["POST"])
@login_required
def redactProject(index):
    project = Project.query.filter_by(id=index).first()
    
    # Если у пользователя нет доступа - останавливаем дальнейшую работу
    if not has_access_to_project(user=current_user, project=project):
        return render_template("forbidden.html", user=current_user)
    
    # Получение информации из запроса
    name = request.form.get('name')
    shortDescription = request.form.get('shortDescription')
    fullDescription = request.form.get('fullDescription')
    goal = request.form.get('goal')
    delete_word = request.form.get('delete')
    user_id = request.form.get('user_id')
    to_delete_user_id = request.form.get('to_delete_user_id')
    is_project_done_id = request.form.get('done')
    
    # Получаем актуальную информацию из БД
    allowed_users_list = json.loads(project.allowedUsers)
    allowed_users = [User.query.filter_by(id=int(i)).first() for i in allowed_users_list]
    
    # В случае некорректной информации останавливаем выполнение
    if not project:
        return redirect(url_for('allProjects'))

    # Удаление проекта
    if delete_word == "УДАЛИТЬ":
        project.delete(db)
        db.session.commit()
        return redirect(url_for('projects.allProjects'))
    
    if name:
        project.name = name
    elif fullDescription:
        project.fullDescription = fullDescription
    elif shortDescription:
        project.shortDescription = shortDescription
    elif goal:
        project.goal = goal
    elif to_delete_user_id:
        allowed_users_list.remove(to_delete_user_id)
        project.allowedUsers = json.dumps(allowed_users_list)
        allowed_users.remove(User.query.filter_by(id=to_delete_user_id).first())
        
    # Изменение состояния проекта
    elif is_project_done_id:
        if project.done == "True":
            project.done = "False"
        else:
            project.done = "True"
            
            
    # Добавление пользователей к проекту
    elif user_id:
        user_to_add = User.query.filter_by(id=user_id).first()
        if not user_to_add:
            flash("Пользователь с таким ID не найден", category="error")
            return render_template("redact_project.html", project=project, user=current_user, allowed_users=allowed_users)
        
        elif project.owner_id == user_to_add.id:
            flash("Вы не можете добавить владельца", category="error")
            return render_template("redact_project.html", project=project, user=current_user, allowed_users=allowed_users)

        else:
            # Проверяем, если ли уже у запрашиваемого пользователя доступ к проекту
            if user_id not in allowed_users_list:
                allowed_users_list.append(user_id)
                added_user = User.query.filter_by(id=user_id).first()
                allowed_users.append(added_user)
                project.allowedUsers = json.dumps(allowed_users_list)
            else:
                flash("Пользователю с таким ID уже предоставлен доступ", category="error")
                
    db.session.commit()
    
    return render_template("redact_project.html", project=project, user=current_user, allowed_users=allowed_users)

# Описывает создание проекта
@projects.route('/new_project', methods=["GET", "POST"])
@login_required
def newProject():
    if request.method == "GET":
        return render_template("new_project.html", user=current_user)
    
    elif request.method == "POST":
        name = request.form.get('name')
        shortDescription = request.form.get('shortDescription')

        new_project = Project(name=name, shortDescription=shortDescription, owner_id=current_user.id)
        
        db.session.add(new_project)
        db.session.commit()
        
        return redirect(url_for('projects.allProjects'))

# Описывает логику просмотра проекта
@projects.route('/projects/<int:index>', methods=["POST"])
@login_required
def showProject(index):
    if request.method == "POST":
        
        project = Project.query.filter_by(id=index).first()
        
        if not has_access_to_project(user=current_user, project=project):
            return render_template("forbidden.html", user=current_user)
    
        to_create_subproject_name = request.form.get('to_create_subproject_name')
        
        subprojects = project.subprojects
        
        if to_create_subproject_name:
            subproject = SubProject(name = to_create_subproject_name, parent_id = project.id)
            db.session.add(subproject)
            subprojects.append(subproject)
            
        db.session.commit()
        return render_template("show_project.html", project=project, user=current_user, subprojects=subprojects)

# Описывает редактирования раздела
@projects.route('/projects/<int:index>/<int:subproject>/redact', methods=["POST"])
@login_required
def redactSubProject(index, subproject):
    if request.method == "POST":
        
        project = Project.query.filter_by(id=index).first()
        
        if not has_access_to_project(user=current_user, project=project):
            return render_template("forbidden.html", user=current_user)
        
        name = request.form.get('name')
        description = request.form.get('description')
        delete_word = request.form.get('delete')
        is_subproject_done_id = request.form.get('done')
        
        subproject = SubProject.query.filter_by(id=subproject).first()
        
        if delete_word == "УДАЛИТЬ":
            subproject.delete(db)
            db.session.commit()
            return redirect(url_for('projects.allProjects'))
        
        if name:
            subproject.name = name
        elif description:
            subproject.shortDescription = description

        if is_subproject_done_id:
            if subproject.done == "True":
                subproject.done = "False"
            else:
                subproject.done = "True"
            
        db.session.commit()    
        return render_template("redact_subproject.html", project=project, user=current_user, subproject=subproject)
    
@projects.route('/projects/<int:index>/<int:subproject>', methods=["POST"])
@login_required
def showSubProject(index, subproject):
    if request.method == "POST":
        
        project = Project.query.filter_by(id=index).first()
        if not has_access_to_project(user=current_user, project=project):
            return render_template("forbidden.html", user=current_user)
        
        create_note = request.form.get('create_note')
        content = request.form.get('content')
        content_id = request.form.get('content_id')
        delete = request.form.get('delete')
        complete = request.form.get('complete')
        
        
        subproject = SubProject.query.filter_by(id=subproject).first()
        
        if create_note:
            note = Note(parent_id=subproject.id, content=create_note, done="False")
            db.session.add(note)
            
        elif delete:
            note = Note.query.filter_by(id=int(delete)).first()
            note.delete(db)

        elif complete:   
            note = Note.query.filter_by(id=int(complete)).first()

            if note.done == "True":
                note.done = "False"
            else:
                note.done = "True"

            
        elif content_id:
            note = Note.query.filter_by(id=int(content_id)).first()
            note.content = content
            
        db.session.commit()
        return render_template("show_subproject.html", project=project, user=current_user, subproject=subproject)

# Обрабатывает запросы по адресу /other_projects с методами Get и Post 
@projects.route('/other_projects', methods=["GET", "POST"])
@login_required
def showOtherProjects():
    # Управялет логикой сохранения проектов других пользователей
    # Только аутентифицированный пользователь имеет доступ к функционалу данной подпрограммы
    # Метод POST подаётся при нажатии на кнопку
    if request.method == "POST":
        
        # Получаем значвения ID проекта из форм страницы
        delete_project_id = request.form.get('delete_project_id')
        add_project_id = request.form.get('add_project')
        
        # Загружаем из БД уже добавленные пользователем проекты
        added_projects = json.loads(current_user.addedProjects)
        saved_projects = [Project.query.filter_by(id=int(i)).first() for i in added_projects]
        
        # Если добавляем проект
        if add_project_id:
            # Проверяем на корректный ввод числа
            try:
                int_add_project_id = int(add_project_id)
            except ValueError:
                # Иначе выводим ошибку и возвращаем страницу без изменений
                flash('Введён некорректный идентификтор')
                return render_template("other_projects.html", user=current_user, available_projects = saved_projects)
            # Проверяем на переполнение целого числа в БД
            if int_add_project_id >= DB_MAX_INT:
                flash('Слишком большой номер проекта')
                return render_template("other_projects.html", user=current_user, available_projects = saved_projects)
            
            # Введённые данные корректны, пытаемся запросить нужный проект
            project = Project.query.filter_by(id=int(int_add_project_id)).first()
            if not project:
                flash('Проекта с таким ID не существует')
            # Проект существует, проверяем есть ли доступ
            elif has_access_to_project(user=current_user, project=project):
                if  project.owner_id == current_user.id:
                    flash('Вы владелец этого проекта')
                elif add_project_id in added_projects:
                    flash('Вы уже сохранили данный проект')
                else:
                    # Долбавляем проект в сохранённые у пользователя
                    added_projects.append(add_project_id)
                    saved_projects.append(project)
            else:
                flash('Доступ к запрашиваемому проекту запрещён')
                
        # Удаление проекта из добавленных           
        elif delete_project_id:
            if delete_project_id in added_projects:
                # Проверяем на корректный ввод числа
                try:
                    int_delete_project_id = int(delete_project_id)
                except ValueError:
                    flash('Введён некорректный идентификтор')
                    return render_template("other_projects.html", user=current_user, available_projects = saved_projects)
                if int_delete_project_id >= DB_MAX_INT:
                    flash('Слишком большой номер проекта')
                    return render_template("other_projects.html", user=current_user, available_projects = saved_projects)
                
                # Введённые данные корректны, удаляем введённый проект
                project = Project.query.filter_by(id=int_delete_project_id).first()
                added_projects.remove(delete_project_id)
                saved_projects.remove(project)
        
        # Сохраняем проект в поля пользователя  
        current_user.addedProjects = json.dumps(added_projects)
        # Сохраняем изменения в БД
        db.session.commit()
        return render_template("other_projects.html", user=current_user, available_projects = saved_projects)
    
    # При переходе по адресу
    elif request.method == "GET":   
        # При переходе по адресу
        # Загружаем из БД уже добавленные пользователем проекты
        added_projects = json.loads(current_user.addedProjects)
        saved_projects = [Project.query.filter_by(id=int(i)).first() for i in added_projects]
        
        # Отображаем страницу
        return render_template("other_projects.html", user=current_user, available_projects = saved_projects)
    