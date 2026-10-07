import pytest
from app import create_app
from src.database.models import db, User, Project, Task

@pytest.fixture(scope='function')
def app():
    '''Создание тестового приложения'''
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    '''Тестовый клиент Flask'''
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    '''Тестовый CLI runner'''
    return app.test_cli_runner()

@pytest.fixture
def admin_user(app):
    '''Создание администратора для тестов'''
    with app.app_context():
        user = User(username='admin', email='admin@test.com', role='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def manager_user(app):
    '''Создание менеджера для тестов'''
    with app.app_context():
        user = User(username='manager', email='manager@test.com', role='manager')
        user.set_password('manager123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def executor_user(app):
    '''Создание исполнителя для тестов'''
    with app.app_context():
        user = User(username='executor', email='executor@test.com', role='executor')
        user.set_password('executor123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_project(app):
    '''Создание тестового проекта'''
    with app.app_context():
        project = Project(
            name='Test Project',
            description='Test project description'
        )
        db.session.add(project)
        db.session.commit()
        return project

@pytest.fixture
def auth_headers(client, admin_user):
    '''Получение JWT токена для тестов'''
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}
