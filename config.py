import os
# basedir = os.path.abspath(os.path.dirname(__file__))
# print('Basedir: {b}'.format(b=basedir))

# Be careful: Variable names need to be UPPERCASE


class Config:
    SECRET_KEY = os.urandom(24)

    # Config values from flaskrun.ini
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False
    # pythonanywhere disconnects clients after 5 minutes idle time. Set pool_recycle to avoid disconnection
    # errors in the log: https://help.pythonanywhere.com/pages/UsingSQLAlchemywithMySQL (from: PythonAnywhere -
    # some tips for specific web frameworks: Flask
    SQLALCHEMY_POOL_RECYCLE = 280

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    LOGLEVEL = "debug"
    # SERVER_NAME = 'localhost:17501'
    SERVER_NAME = 'localhost:50120'
    LOGDIR = "C:\\Temp\\Log"
    SQLALCHEMY_DATABASE_URI = "sqlite:///C:\\Development\\python\\lkb\\lkb\\data\\lkb.db"


class TestingConfig(Config):
    DEBUG = False
    # Set Loglevel to warning or worse (error, fatal) for readability
    LOGLEVEL = "info"
    TESTING = True
    SECRET_KEY = 'The Secret Test Key!'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:5999'
    LOGDIR = "C:\\Temp\\Log"
    SQLALCHEMY_DATABASE_URI = "sqlite:///C:\\Development\\python\\lkb\\lkb\\data\\lkb.db"


class ProductionConfig(Config):
    ADMINS = ['dirk@vermeylen.net']
    LOGLEVEL = "debug"
    # SERVER_NAME = 'localhost:5008'
    DEBUG = True
    LOGDIR = "/var/sites/lkb"
    SQLALCHEMY_DATABASE_URI = "sqlite:////home/dirk/lkb/lkb/data/lkb.db"
    # SERVER_NAME = '81.4.104.137:8181'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
