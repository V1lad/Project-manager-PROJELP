import pytest
from Main import app
from faker import Faker

# Проверка создания нового проекта
def test_create_new_project():
    
    # Формирование запроса
    response = app.test_client().post("/new_project", json={
        "name":"Test_project",
        "shortDescription":"Test_project"
    })
    
    # Проверка редиректа на другую страницу
    assert response.status_code == 302
    

