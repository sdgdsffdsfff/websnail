from flask import Flask,render_template
from flask.ext.bootstrap import Bootstrap
from configs import config
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.codemirror import CodeMirror
from flask.ext.login import LoginManager

bootstrap = Bootstrap()
db = SQLAlchemy()
codemirror = CodeMirror()
login_manager = LoginManager()


def createApp(configenv):
	app = Flask(__name__)
	app.config.from_object(config[configenv])
	config[configenv].init_app(app)
	bootstrap.init_app(app)
	db.init_app(app)
	codemirror.init_app(app)
	login_manager.init_app(app)
	from .main import main as BluePrint
	app.register_blueprint(BluePrint)

	return(app)
