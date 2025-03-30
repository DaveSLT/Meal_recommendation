from flask import Flask
from flask_login import LoginManager
from os import path

from .models import db, User

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dave wapo'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/meal_recommendation'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    # Create database if it doesn't exist
    with app.app_context():
        db.drop_all()
        db.create_all()
    
    return app