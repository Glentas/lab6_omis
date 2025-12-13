from app.models import User

def get_all_users():
    return User.query.all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def create_user(name, email, role, password):
    from werkzeug.security import generate_password_hash
    from app import db
    user = User(
        name=name,
        email=email,
        role=role,
        password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    return user

def update_user(user_id, name, email, role):
    from app import db
    user = get_user_by_id(user_id)
    if user:
        user.name = name
        user.email = email
        user.role = role
        db.session.commit()
    return user
