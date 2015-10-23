class TestingConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost:3306/websnail'
    SECRET_KEY = 'what does the fox say?'
    CODEMIRROR_LANGUAGES = ['python']
    CODEMIRROR_ADDONS = (
            ('display','placeholder'),
    )
    CODEMIRROR_THEME = 'mbo'
    WTF_CSRF_SECRET_KEY = "whatever"

    SERVICE_TYPES = [
            'OCR',
            'NLP',
            'SEARCH',
            '1v1'
        ]

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
