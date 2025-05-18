from flask import Flask
from flask_login import LoginManager
import pickle
from models import db, User
from routes import init_routes
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Load model
    with open(Config.MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize routes
    init_routes(app, model)

    return app

# Create app instance at module level
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 