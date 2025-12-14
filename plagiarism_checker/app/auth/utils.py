from app.models import User

def create_demo_users():
    from app import db
    from werkzeug.security import generate_password_hash
    users = [
        User(name="Студент", email="student@example.com", role="student",
             password_hash=generate_password_hash("123")),
        User(name="Преподаватель", email="teacher@example.com", role="teacher",
             password_hash=generate_password_hash("123")),
        User(name="Админ", email="admin@example.com", role="admin",
             password_hash=generate_password_hash("123")),
    ]
    for u in users:
        if not User.query.filter_by(email=u.email).first():
            db.session.add(u)
    db.session.commit()
