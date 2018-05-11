import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/rice_safety_app"

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True