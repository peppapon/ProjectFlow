import pytest
from src.database.models import Task, db
import os

class TestReportModule:
    '''Тесты модуля формирования отчётов (ReportModule)'''
    
    def test_report_by_user(self, client, auth_headers, executor_user, test_project, app):
        '''Тест отчёта по исполнителю'''
        # Создаем задачи для пользователя
        with app.app_context():
            task1 = Task(
                title='Task 1',
                project_id=test_project.id,
                creator_id=1,
                assignee_id=executor_user.id,
                status='new'
            )
            task2 = Task(
                title='Task 2',
                project_id=test_project.id,
                creator_id=1,
                assignee_id=executor_user.id,
                status='completed'
            )
            db.session.add_all([task1, task2])
            db.session.commit()
        
        response = client.get(f'/api/reports/by-user/{executor_user.id}', 
                            headers=auth_headers)
        
        assert response.status_code == 200
        assert 'user' in response.json
        assert response.json['total_tasks'] == 2
        assert 'status_breakdown' in response.json
        assert response.json['status_breakdown']['new'] == 1
        assert response.json['status_breakdown']['completed'] == 1
    
    def test_report_by_nonexistent_user(self, client, auth_headers):
        '''Тест отчёта по несуществующему пользователю'''
        response = client.get('/api/reports/by-user/9999', headers=auth_headers)
        
        assert response.status_code == 404
        assert 'User not found' in response.json['error']
    
    def test_report_by_project(self, client, auth_headers, test_project, app):
        '''Тест отчёта по проекту'''
        with app.app_context():
            task1 = Task(
                title='Task 1',
                project_id=test_project.id,
                creator_id=1,
                status='new',
                priority='high'
            )
            task2 = Task(
                title='Task 2',
                project_id=test_project.id,
                creator_id=1,
                status='in_progress',
                priority='low'
            )
            db.session.add_all([task1, task2])
            db.session.commit()
        
        response = client.get(f'/api/reports/by-project/{test_project.id}', 
                            headers=auth_headers)
        
        assert response.status_code == 200
        assert 'project' in response.json
        assert response.json['total_tasks'] == 2
        assert 'status_breakdown' in response.json
        assert 'priority_breakdown' in response.json
        assert response.json['priority_breakdown']['high'] == 1
        assert response.json['priority_breakdown']['low'] == 1
    
    def test_report_by_nonexistent_project(self, client, auth_headers):
        '''Тест отчёта по несуществующему проекту'''
        response = client.get('/api/reports/by-project/9999', headers=auth_headers)
        
        assert response.status_code == 404
        assert 'Project not found' in response.json['error']
    
    def test_report_by_period_success(self, client, auth_headers):
        '''Тест отчёта за период'''
        response = client.get('/api/reports/by-period',
            headers=auth_headers,
            query_string={
                'start_date': '2026-01-01T00:00:00',
                'end_date': '2026-12-31T23:59:59'
            }
        )
        
        assert response.status_code == 200
        assert 'period' in response.json
        assert 'created_tasks' in response.json
        assert 'completed_tasks' in response.json
    
    def test_report_by_period_missing_dates(self, client, auth_headers):
        '''Тест отчёта за период без указания дат'''
        response = client.get('/api/reports/by-period', headers=auth_headers)
        
        assert response.status_code == 400
        assert 'required' in response.json['error'].lower()
    
    def test_report_by_period_invalid_date_format(self, client, auth_headers):
        '''Тест отчёта за период с невалидным форматом даты'''
        response = client.get('/api/reports/by-period',
            headers=auth_headers,
            query_string={
                'start_date': 'invalid-date',
                'end_date': '2026-12-31'
            }
        )
        
        assert response.status_code == 400
        assert 'Invalid date format' in response.json['error']
    
    def test_summary_report(self, client, auth_headers, test_project, app):
        '''Тест сводного отчёта'''
        with app.app_context():
            task = Task(
                title='Test Task',
                project_id=test_project.id,
                creator_id=1,
                status='new',
                priority='medium'
            )
            db.session.add(task)
            db.session.commit()
        
        response = client.get('/api/reports/summary', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'summary' in response.json
        assert 'status_breakdown' in response.json
        assert 'priority_breakdown' in response.json
        assert response.json['summary']['total_tasks'] >= 1
    
    def test_export_excel(self, client, auth_headers, test_project, app):
        '''Тест экспорта отчёта в Excel'''
        with app.app_context():
            task = Task(
                title='Test Task for Excel',
                project_id=test_project.id,
                creator_id=1
            )
            db.session.add(task)
            db.session.commit()
        
        response = client.get('/api/reports/export/excel', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    def test_export_pdf(self, client, auth_headers, test_project, app):
        '''Тест экспорта отчёта в PDF'''
        with app.app_context():
            task = Task(
                title='Test Task for PDF',
                project_id=test_project.id,
                creator_id=1
            )
            db.session.add(task)
            db.session.commit()
        
        response = client.get('/api/reports/export/pdf', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
