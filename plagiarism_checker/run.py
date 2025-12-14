import os
from app import create_app
from app.auth.utils import create_demo_users
from config import UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        create_demo_users()
    app.run(debug=True)
