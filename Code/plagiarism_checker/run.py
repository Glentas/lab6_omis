from app import create_app, db
from app.auth.utils import create_demo_users

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        create_demo_users()  # Создаём демо-пользователей при первом запуске
    app.run(debug=True)
