from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.database.models import db, Task, Project, User
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

# Определение разрешенных переходов статусов (конечный автомат)
STATUS_TRANSITIONS = {
    'new': ['in_progress', 'rejected'],
    'in_progress': ['review', 'rejected'],
    'review': ['completed', 'rejected'],
    'completed': [],  # Завершенные задачи не могут менять статус
    'rejected': ['new', 'in_progress']  # Отклоненные могут быть возвращены в работу
}

def is_valid_transition(current_status, new_status):
    """Проверка валидности перехода статуса"""
    return new_status in STATUS_TRANSITIONS.get(current_status, [])

@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Создание новой задачи"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('project_id'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Проверка существования проекта
    project = Project.query.get(data['project_id'])
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Создание задачи
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        project_id=data['project_id'],
        creator_id=current_user_id,
        assignee_id=data.get('assignee_id'),
        priority=data.get('priority', 'medium'),
        status='new'
    )
    
    if data.get('due_date'):
        try:
            task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid due_date format'}), 400
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        'message': 'Task created successfully',
        'task': task.to_dict()
    }), 201

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Получение списка задач с фильтрацией"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'executor')
    
    # Базовый запрос
    query = Task.query
    
    # Фильтрация по роли
    if role == 'executor':
        # Исполнители видят только свои задачи
        query = query.filter_by(assignee_id=current_user_id)
    elif role == 'manager':
        # Менеджеры видят задачи своих проектов
        # В упрощенной версии - все задачи
        pass
    # admin видит все задачи
    
    # Фильтры из query параметров
    project_id = request.args.get('project_id', type=int)
    status = request.args.get('status')
    assignee_id = request.args.get('assignee_id', type=int)
    
    if project_id:
        query = query.filter_by(project_id=project_id)
    if status:
        query = query.filter_by(status=status)
    if assignee_id:
        query = query.filter_by(assignee_id=assignee_id)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    
    return jsonify({
        'tasks': [task.to_dict() for task in tasks],
        'count': len(tasks)
    }), 200

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Получение задачи по ID"""
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task.to_dict()), 200

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Обновление задачи"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'executor')
    
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Проверка прав доступа
    if role == 'executor' and task.assignee_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        try:
            task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid due_date format'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': 'Task updated successfully',
        'task': task.to_dict()
    }), 200

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Удаление задачи"""
    claims = get_jwt()
    role = claims.get('role', 'executor')
    
    if role not in ['admin', 'manager']:
        return jsonify({'error': 'Access denied'}), 403
    
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'}), 200

@tasks_bp.route('/<int:task_id>/status', methods=['PATCH'])
@jwt_required()
def change_status(task_id):
    """Изменение статуса задачи (с проверкой разрешенных переходов)"""
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'executor')
    
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400
    
    # Проверка валидности перехода
    if not is_valid_transition(task.status, new_status):
        return jsonify({
            'error': f'Invalid status transition from {task.status} to {new_status}',
            'allowed_transitions': STATUS_TRANSITIONS.get(task.status, [])
        }), 400
    
    task.status = new_status
    
    # Если задача завершена, устанавливаем время завершения
    if new_status == 'completed':
        task.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': f'Task status changed to {new_status}',
        'task': task.to_dict()
    }), 200

@tasks_bp.route('/<int:task_id>/assign', methods=['PATCH'])
@jwt_required()
def assign_task(task_id):
    """Назначение исполнителя задачи"""
    claims = get_jwt()
    role = claims.get('role', 'executor')
    
    if role not in ['admin', 'manager']:
        return jsonify({'error': 'Only admins and managers can assign tasks'}), 403
    
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    assignee_id = data.get('assignee_id')
    
    if not assignee_id:
        return jsonify({'error': 'Assignee ID is required'}), 400
    
    # Проверка существования пользователя
    assignee = User.query.get(assignee_id)
    if not assignee:
        return jsonify({'error': 'Assignee not found'}), 404
    
    task.assignee_id = assignee_id
    db.session.commit()
    
    return jsonify({
        'message': 'Task assigned successfully',
        'task': task.to_dict()
    }), 200

@tasks_bp.route('/transitions', methods=['GET'])
def get_status_transitions():
    """Получение матрицы переходов статусов"""
    return jsonify({
        'transitions': STATUS_TRANSITIONS,
        'statuses': ['new', 'in_progress', 'review', 'completed', 'rejected']
    }), 200
