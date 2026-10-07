import pytest
from src.database.models import Task, db
from datetime import datetime, timedelta

class TestTaskModule:
    '''Тесты модуля управления задачами (TaskModule)'''
    
    def test_create_task_success(self, client, auth_headers, test_project):
        '''Тест успешного создания задачи'''
        response = client.post('/api/tasks', 
            headers=auth_headers,
            json={
                'title': 'Test Task',
                'description': 'Test description',
                'project_id': test_project.id,
                'priority': 'high'
            }
        )
        
        assert response.status_code == 201
        assert response.json['task']['title'] == 'Test Task'
        assert response.json['task']['status'] == 'new'
        assert response.json['message'] == 'Task created successfully'
    
    def test_create_task_missing_fields(self, client, auth_headers):
        '''Тест создания задачи без обязательных полей'''
        response = client.post('/api/tasks', 
            headers=auth_headers,
            json={'description': 'Test'}
        )
        
        assert response.status_code == 400
        assert 'Missing required fields' in response.json['error']
    
    def test_create_task_invalid_project(self, client, auth_headers):
        '''Тест создания задачи с несуществующим проектом'''
        response = client.post('/api/tasks', 
            headers=auth_headers,
            json={
                'title': 'Test Task',
                'project_id': 9999
            }
        )
        
        assert response.status_code == 404
        assert 'Project not found' in response.json['error']
    
    def test_get_tasks_list(self, client, auth_headers, test_project, app):
        '''Тест получения списка задач'''
        # Создаем тестовые задачи
        with app.app_context():
            task = Task(
                title='Test Task',
                description='Description',
                project_id=test_project.id,
                creator_id=1,
                status='new'
            )
            db.session.add(task)
            db.session.commit()
        
        response = client.get('/api/tasks', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'tasks' in response.json
        assert response.json['count'] >= 1
    
    def test_get_task_by_id(self, client, auth_headers, test_project, app):
        '''Тест получения задачи по ID'''
        with app.app_context():
            task = Task(
                title='Test Task',
                project_id=test_project.id,
                creator_id=1
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['title'] == 'Test Task'
    
    def test_get_nonexistent_task(self, client, auth_headers):
        '''Тест получения несуществующей задачи'''
        response = client.get('/api/tasks/9999', headers=auth_headers)
        
        assert response.status_code == 404
        assert 'Task not found' in response.json['error']
    
    def test_update_task_success(self, client, auth_headers, test_project, app):
        '''Тест успешного обновления задачи'''
        with app.app_context():
            task = Task(
                title='Old Title',
                project_id=test_project.id,
                creator_id=1,
                assignee_id=1
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = client.put(f'/api/tasks/{task_id}',
            headers=auth_headers,
            json={'title': 'New Title', 'priority': 'high'}
        )
        
        assert response.status_code == 200
        assert response.json['task']['title'] == 'New Title'
        assert response.json['task']['priority'] == 'high'
    
    def test_delete_task_success(self, client, auth_headers, test_project, app):
        '''Тест успешного удаления задачи'''
        with app.app_context():
            task = Task(
                title='Task to Delete',
                project_id=test_project.id,
                creator_id=1
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['message'] == 'Task deleted successfully'
    
    def test_change_status_valid_transition(self, client, auth_headers, test_project, app):
        '''Тест изменения статуса задачи (валидный переход)'''
        with app.app_context():
            task = Task(
                title='Test Task',
                project_id=test_project.id,
                creator_id=1,
                status='new'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        # new -> in_progress (валидный переход)
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=auth_headers,
            json={'status': 'in_progress'}
        )
        
        assert response.status_code == 200
        assert response.json['task']['status'] == 'in_progress'
    
    def test_change_status_invalid_transition(self, client, auth_headers, test_project, app):
        '''Тест изменения статуса задачи (невалидный переход)'''
        with app.app_context():
            task = Task(
                title='Test Task',
                project_id=test_project.id,
                creator_id=1,
                status='new'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        # new -> completed (невалидный переход, должен пройти через in_progress)
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=auth_headers,
            json={'status': 'completed'}
        )
        
        assert response.status_code == 400
        assert 'Invalid status transition' in response.json['error']
    
    def test_change_status_completed_no_further_transitions(self, client, auth_headers, test_project, app):
        '''Тест что завершенная задача не может менять статус'''
        with app.app_context():
            task = Task(
                title='Test Task',
                project_id=test_project.id,
                creator_id=1,
                status='completed'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = client.patch(f'/api/tasks/{task_id}/status',
            headers=auth_headers,
            json={'status': 'new'}
        )
        
        assert response.status_code == 400
        assert 'Invalid status transition' in response.json['error']
    
    def test_assign_task_success(self, client, auth_headers, test_project, executor_user, app):
        '''Тест назначения исполнителя задачи'''
        with app.app_context():
            task = Task(
                title='Test Task',
                project_id=test_project.id,
                creator_id=1
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = client.patch(f'/api/tasks/{task_id}/assign',
            headers=auth_headers,
            json={'assignee_id': executor_user.id}
        )
        
        assert response.status_code == 200
        assert response.json['task']['assignee_id'] == executor_user.id
    
    def test_get_status_transitions(self, client):
        '''Тест получения матрицы переходов статусов'''
        response = client.get('/api/tasks/transitions')
        
        assert response.status_code == 200
        assert 'transitions' in response.json
        assert 'statuses' in response.json
        assert 'new' in response.json['statuses']
