from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

# Создание экземпляра Flask приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'  # Секретный ключ для сессий


# Настройка пути к SQLite базе данных
# Абсолютный путь к базе данных внутри контейнера
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'comments.db')  # Путь к файлу БД
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}" 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Инициализация расширений
db = SQLAlchemy(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Определение модели Comment для хранения комментариев
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # Уникальный идентификатор
    user = db.Column(db.String(50), nullable=False)   # Имя пользователя (обязательное)
    text = db.Column(db.String(500), nullable=False)    # Текст комментария (обязательное)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Время создания (по умолчанию текущее)

    def to_dict(self):
        """Преобразует объект Comment в словарь для JSON-сериализации"""
        return {
            'id': self.id,
            'user': self.user,
            'text': self.text,
            'timestamp': self.timestamp.isoformat()
        }

# Создаём таблицы в базе данных
with app.app_context():
    db.create_all()

# Статические данные о котах
cats = [
    {"id": 1, "name": "Барсик", "description": "Любит спать и мурлыкать", "image": "/images/cat1.jpg"},
    {"id": 2, "name": "Мурка", "description": "Обожает играть с клубками", "image": "/images/cat2.jpg"},
    {"id": 3, "name": "Снежок", "description": "Пушистый и ласковый", "image": "/images/cat3.jpg"},
]

# Маршрут для получения списка котов
@app.route('/api/cats')
def get_cats():
    """Возвращает JSON-список всех котов"""
    return jsonify(cats)

# Маршрут для получения всех комментариев
@app.route('/api/comments')
def get_comments():
    """Возвращает все комментарии из БД, отсортированные по времени"""
    comments = Comment.query.order_by(Comment.timestamp.asc()).all()
    return jsonify([c.to_dict() for c in comments])

# Обработчик WebSocket-события для нового комментария
@socketio.on('new_comment')
def handle_new_comment(data):
    """Обрабатывает новое сообщение от клиента через WebSocket"""
    user = data.get('user')
    text = data.get('text')
    if user and text:
        comment = Comment(user=user, text=text)
        db.session.add(comment)
        db.session.commit()
        emit('comment_added', comment.to_dict(), broadcast=True)

if __name__ == '__main__':
    # Запускаем сервер SocketIO на всех интерфейсах, порт 5000
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
