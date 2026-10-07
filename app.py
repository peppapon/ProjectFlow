from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
from src.database.models import db
import os

def create_app(config_name='default'):
    '''Фабрика приложения Flask'''
    app = Flask(__name__)
    
    # Загрузка конфигурации
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Инициализация расширений
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # Регистрация blueprints
    from src.auth.routes import auth_bp
    from src.tasks.routes import tasks_bp
    from src.reports.routes import reports_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(reports_bp)
    
    # Создание таблиц БД
    with app.app_context():
        db.create_all()
        init_default_data()
    
    # Обработчики ошибок
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    # JWT обработчики
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({'error': 'Missing authorization header'}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({'error': 'Token has expired'}), 401
    
    # Главная страница
    @app.route('/')
    def index():
        return jsonify({
            'message': 'ProjectFlow API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'tasks': '/api/tasks',
                'reports': '/api/reports'
            }
        })
    
    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    return app

def init_default_data():
    '''Инициализация данных по умолчанию'''
    from src.database.models import User, Project
    
    # Создаем администратора если его нет
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@projectflow.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    # Создаем демо-проект если нет проектов
    if Project.query.count() == 0:
        demo_project = Project(
            name='Демонстрационный проект',
            description='Проект для демонстрации возможностей системы ProjectFlow'
        )
        db.session.add(demo_project)
    
    db.session.commit()

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
