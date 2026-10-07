import pytest
from src.database.models import User, db

class TestAuthModule:
    '''Тесты модуля авторизации (AuthModule)'''
    
    def test_register_success(self, client):
        '''Тест успешной регистрации пользователя'''
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'role': 'executor'
        })
        
        assert response.status_code == 201
        assert 'user' in response.json
        assert response.json['user']['username'] == 'testuser'
        assert response.json['message'] == 'User registered successfully'
    
    def test_register_duplicate_username(self, client, admin_user):
        '''Тест регистрации с существующим username'''
        response = client.post('/api/auth/register', json={
            'username': 'admin',
            'email': 'newemail@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 409
        assert 'Username already exists' in response.json['error']
    
    def test_register_duplicate_email(self, client, admin_user):
        '''Тест регистрации с существующим email'''
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'admin@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 409
        assert 'Email already exists' in response.json['error']
    
    def test_register_missing_fields(self, client):
        '''Тест регистрации без обязательных полей'''
        response = client.post('/api/auth/register', json={
            'username': 'testuser'
        })
        
        assert response.status_code == 400
        assert 'Missing required fields' in response.json['error']
    
    def test_login_success(self, client, admin_user):
        '''Тест успешного входа'''
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert response.json['message'] == 'Login successful'
    
    def test_login_invalid_credentials(self, client, admin_user):
        '''Тест входа с неверными данными'''
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert 'Invalid credentials' in response.json['error']
    
    def test_login_nonexistent_user(self, client):
        '''Тест входа несуществующего пользователя'''
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        assert 'Invalid credentials' in response.json['error']
    
    def test_get_profile_success(self, client, auth_headers):
        '''Тест получения профиля'''
        response = client.get('/api/auth/profile', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'username' in response.json
        assert response.json['username'] == 'admin'
    
    def test_get_profile_without_token(self, client):
        '''Тест получения профиля без токена'''
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401
    
    def test_update_profile_success(self, client, auth_headers):
        '''Тест обновления профиля'''
        response = client.put('/api/auth/profile', 
            headers=auth_headers,
            json={'email': 'newemail@test.com'}
        )
        
        assert response.status_code == 200
        assert response.json['user']['email'] == 'newemail@test.com'
    
    def test_logout(self, client, auth_headers):
        '''Тест выхода из системы'''
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['message'] == 'Logout successful'
    
    def test_reset_password(self, client, admin_user):
        '''Тест восстановления пароля'''
        response = client.post('/api/auth/reset-password', json={
            'email': 'admin@test.com'
        })
        
        assert response.status_code == 200
        assert 'password reset' in response.json['message'].lower()
