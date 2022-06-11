from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# from flask_login import LoginManager

app = Flask(__name__)
manager = Manager(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# login_manager = LoginManager()
# login_manager.init_app(app)

from app import routes

   