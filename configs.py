import os

class TestingConfig:
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost:3306/websnail'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:%s@%s:3306/websnail" %(os.environ.get("MYSQL_PASSWORD"),os.environ.get("HOST_NAME"))
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'what does the fox say?'
    CODEMIRROR_LANGUAGES = ['python']
    CODEMIRROR_ADDONS = (
            ('display','placeholder'),
    )
    CODEMIRROR_THEME = 'mbo'
    WTF_CSRF_SECRET_KEY = "whatever"

    @staticmethod
    def init_app(app):
        pass

class ProductionConfig:
    pass

class BaseConfig:
    logpath = ''
    statusfile = ''
    reportfile = ''
    scriptpath = ''

config = {
    'testing':TestingConfig,
    'production':ProductionConfig
}
