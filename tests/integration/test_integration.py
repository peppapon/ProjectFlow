import pytest
from src.database.models import Task, User, Project, db
from datetime import datetime, timedelta

class TestIntegration:
    '''Интеграционные тесты системы ProjectFlow'''
    
    def test_full_task_lifecycle(self, client, app, test_project):
        '''Тест полного жизненного цикла задачи: создание → переходы статусов → отчёт'''
        
        # 1. Регистрация пользователя-менеджера
        response = client.post('/api/auth/register', json={
            'username': 'manager1',
            'email': 'manager1@test.com',
            'password': 'manager123',
            'role': 'manager'
        })
        assert response.status_code == 201
        
        # 2. Вход менеджера
        response = client.post('/api/auth/login', json={
            'username': 'manager1',
            'password': 'manager123'
        })
        assert response.status_code == 200
        manager_token = response.json['access_token']
        manager_headers = {'Authorization': f'Bearer {manager_token}'}
        manager_id = response.json['user']['id']
        
        # 3. Регистрация исполнителя
        response = client.post('/api/auth/register', json={
            'username': 'executor1',
            'email': 'executor1@test.com',
            'password': 'executor123',
            'role': 'executor'
        })
        assert response.status_code == 201
        executor_id = response.json['user']['id']
        
        # 4. Создание задачи менеджером
        response = client.post('/api/tasks', 
            headers=manager_headers,
            json={
                'title': 'Интеграционная тестовая задача',
                'description': 'Задача для проверки полного цикла',
                'project_id': test_project.id,
                'priority': 'high'
            }
        )
        assert response.status_code == 201
        task_id = response.json['task']['id']
        assert response.json['task']['status'] == 'new'
        
        # 5. Назначение исполнителя
        response = client.patch(f'/api/tasks/{task_id}/assign',
            headers=manager_headers,
            json={'assignee_id': executor_id}
        )
        assert response.status_code == 200
        assert response.json['task']['assignee_id'] == executor_id
        
        # 6. Вход исполнителя
        response = client.post('/api/auth/login', json={
            'username': 'executor1',
            'password': 'executor123'
        })
        executor_token = response.json['access_token']
        executor_headers = {'Authorization': f'Bearer {executor_token}'}
        
        # 7. Переход new → in_progress
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=executor_headers,
            json={'status': 'in_progress'}
        )
        assert response.status_code == 200
        assert response.json['task']['status'] == 'in_progress'
        
        # 8. Переход in_progress → review
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=executor_headers,
            json={'status': 'review'}
        )
        assert response.status_code == 200
        assert response.json['task']['status'] == 'review'
        
        # 9. Переход review → completed
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=manager_headers,
            json={'status': 'completed'}
        )
        assert response.status_code == 200
        assert response.json['task']['status'] == 'completed'
        assert response.json['task']['completed_at'] is not None
        
        # 10. Проверка что задача появляется в отчёте по исполнителю
        response = client.get(f'/api/reports/by-user/{executor_id}',
            headers=manager_headers
        )
        assert response.status_code == 200
        assert response.json['total_tasks'] == 1
        assert response.json['status_breakdown']['completed'] == 1
        
        # 11. Проверка что задача появляется в отчёте по проекту
        response = client.get(f'/api/reports/by-project/{test_project.id}',
            headers=manager_headers
        )
        assert response.status_code == 200
        assert response.json['total_tasks'] >= 1
        
        # 12. Проверка сводного отчёта
        response = client.get('/api/reports/summary',
            headers=manager_headers
        )
        assert response.status_code == 200
        assert response.json['summary']['total_tasks'] >= 1
    
    def test_task_rejection_and_reopen(self, client, app, test_project):
        '''Тест отклонения задачи и возврата в работу'''
        
        # Создаем менеджера
        response = client.post('/api/auth/register', json={
            'username': 'manager2',
            'email': 'manager2@test.com',
            'password': 'manager123',
            'role': 'manager'
        })
        manager_id = response.json['user']['id']
        
        response = client.post('/api/auth/login', json={
            'username': 'manager2',
            'password': 'manager123'
        })
        token = response.json['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Создаем задачу
        response = client.post('/api/tasks',
            headers=headers,
            json={
                'title': 'Задача с отклонением',
                'project_id': test_project.id
            }
        )
        task_id = response.json['task']['id']
        
        # new → in_progress
        client.patch(f'/api/tasks/{task_id}/status',
            headers=headers, json={'status': 'in_progress'})
        
        # in_progress → rejected (отклонение)
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=headers, json={'status': 'rejected'})
        assert response.status_code == 200
        assert response.json['task']['status'] == 'rejected'
        
        # rejected → in_progress (возврат в работу)
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=headers, json={'status': 'in_progress'})
        assert response.status_code == 200
        assert response.json['task']['status'] == 'in_progress'
        
        # in_progress → review → completed
        client.patch(f'/api/tasks/{task_id}/status',
            headers=headers, json={'status': 'review'})
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=headers, json={'status': 'completed'})
        assert response.status_code == 200
    
    def test_multiple_users_access_control(self, client, app, test_project):
        '''Тест контроля доступа для разных ролей пользователей'''
        
        # Создаем администратора
        client.post('/api/auth/register', json={
            'username': 'admin_test',
            'email': 'admin_test@test.com',
            'password': 'admin123',
            'role': 'admin'
        })
        response = client.post('/api/auth/login', json={
            'username': 'admin_test',
            'password': 'admin123'
        })
        admin_headers = {'Authorization': f'Bearer {response.json[\"access_token\"]}'}
        
        # Создаем исполнителя
        client.post('/api/auth/register', json={
            'username': 'executor_test',
            'email': 'executor_test@test.com',
            'password': 'executor123',
            'role': 'executor'
        })
        response = client.post('/api/auth/login', json={
            'username': 'executor_test',
            'password': 'executor123'
        })
        executor_headers = {'Authorization': f'Bearer {response.json[\"access_token\"]}'}
        executor_id = response.json['user']['id']
        
        # Админ создает задачу
        response = client.post('/api/tasks',
            headers=admin_headers,
            json={
                'title': 'Задача для проверки прав',
                'project_id': test_project.id,
                'assignee_id': executor_id
            }
        )
        task_id = response.json['task']['id']
        
        # Исполнитель может видеть свою задачу
        response = client.get(f'/api/tasks/{task_id}', headers=executor_headers)
        assert response.status_code == 200
        
        # Исполнитель не может удалять задачи
        response = client.delete(f'/api/tasks/{task_id}', headers=executor_headers)
        assert response.status_code == 403
        
        # Админ может удалять задачи
        response = client.delete(f'/api/tasks/{task_id}', headers=admin_headers)
        assert response.status_code == 200
    
    def test_report_export_flow(self, client, app, test_project):
        '''Тест экспорта отчётов в различных форматах'''
        
        # Создаем пользователя
        client.post('/api/auth/register', json={
            'username': 'reporter',
            'email': 'reporter@test.com',
            'password': 'reporter123',
            'role': 'manager'
        })
        response = client.post('/api/auth/login', json={
            'username': 'reporter',
            'password': 'reporter123'
        })
        headers = {'Authorization': f'Bearer {response.json[\"access_token\"]}'}
        
        # Создаем несколько задач
        for i in range(3):
            client.post('/api/tasks',
                headers=headers,
                json={
                    'title': f'Задача {i+1}',
                    'project_id': test_project.id,
                    'priority': ['low', 'medium', 'high'][i % 3]
                }
            )
        
        # Экспорт в Excel
        response = client.get('/api/reports/export/excel', headers=headers)
        assert response.status_code == 200
        assert 'xlsx' in response.content_type or 'spreadsheet' in response.content_type
        
        # Экспорт в PDF
        response = client.get('/api/reports/export/pdf', headers=headers)
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
    
    def test_invalid_status_transitions_blocked(self, client, app, test_project):
        '''Тест блокировки недопустимых переходов статусов'''
        
        client.post('/api/auth/register', json={
            'username': 'test_transitions',
            'email': 'test_transitions@test.com',
            'password': 'test123',
            'role': 'manager'
        })
        response = client.post('/api/auth/login', json={
            'username': 'test_transitions',
            'password': 'test123'
        })
        headers = {'Authorization': f'Bearer {response.json[\"access_token\"]}'}
        
        # Создаем задачу
        response = client.post('/api/tasks',
            headers=headers,
            json={'title': 'Тест переходов', 'project_id': test_project.id}
        )
        task_id = response.json['task']['id']
        
        # Попытка перейти напрямую new → completed (недопустимо)
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=headers, json={'status': 'completed'})
        assert response.status_code == 400
        assert 'Invalid status transition' in response.json['error']
        
        # Валидный переход new → in_progress
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=headers, json={'status': 'in_progress'})
        assert response.status_code == 200
        
        # Попытка вернуться in_progress → new (недопустимо)
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=headers, json={'status': 'new'})
        assert response.status_code == 400
