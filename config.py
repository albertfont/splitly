import os
import configparser

class Config:
    """Base configuration."""
    DEBUG = False
    #Load configuration from config.ini file or environment variables
    config = configparser.ConfigParser()
    config.read('config.ini')
    SECRET_KEY = config.get('DEFAULT', 'SECRET_KEY', fallback=os.environ.get('SECRET_KEY', 'default_secret_key'))
    SQLALCHEMY_DATABASE_URI = config.get('DEFAULT', 'DATABASE_URI', fallback=os.environ.get('DATABASE_URI', 'sqlite:///trip_expenses.sqlite'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = config.get('DEFAULT', 'UPLOAD_FOLDER', fallback=os.environ.get('UPLOAD_FOLDER', './uploads'))

    MAIL_SERVER = config.get('MAIL', 'SERVER', fallback=os.environ.get('MAIL_SERVER', 'smtp.gmail.com'))
    MAIL_PORT = config.get('MAIL', 'PORT', fallback=os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = config.get('MAIL', 'USE_TLS', fallback=os.environ.get('MAIL_USE_TLS', True))
    MAIL_USERNAME = config.get('MAIL', 'USERNAME', fallback=os.environ.get('MAIL_USERNAME', 'trip_expense@gmail.com'))
    MAIL_PASSWORD = config.get('MAIL', 'PASSWORD', fallback=os.environ.get('MAIL_PASSWORD', 'your_password_here'))
    MAIL_DEFAULT_SENDER = config.get('MAIL', 'DEFAULT_SENDER', fallback=os.environ.get('MAIL_DEFAULT_SENDER', 'trip_expense@gmail.com'))