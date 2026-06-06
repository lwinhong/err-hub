import os
from datetime import timedelta


class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'postgresql://errhub:errhub@db:5432/errhub'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 90))
    SUPERADMIN_USERNAME = os.environ.get('SUPERADMIN_USERNAME', 'admin')
    SUPERADMIN_PASSWORD = os.environ.get('SUPERADMIN_PASSWORD', 'admin123')
    # API 滥用防护
    RATE_LIMIT_PER_PROJECT = int(os.environ.get('RATE_LIMIT_PER_PROJECT', 60))
    RATE_LIMIT_PER_IP = int(os.environ.get('RATE_LIMIT_PER_IP', 120))
    DAILY_ERROR_LIMIT = int(os.environ.get('DAILY_ERROR_LIMIT', 10000))
    MAX_ERROR_PAYLOAD_SIZE = int(os.environ.get('MAX_ERROR_PAYLOAD_SIZE', 65536))


class ProductionConfig:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'postgresql://errhub:errhub@db:5432/errhub'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 90))
    SUPERADMIN_USERNAME = os.environ.get('SUPERADMIN_USERNAME', 'admin')
    SUPERADMIN_PASSWORD = os.environ.get('SUPERADMIN_PASSWORD', 'admin123')
    # API 滥用防护
    RATE_LIMIT_PER_PROJECT = int(os.environ.get('RATE_LIMIT_PER_PROJECT', 60))
    RATE_LIMIT_PER_IP = int(os.environ.get('RATE_LIMIT_PER_IP', 120))
    DAILY_ERROR_LIMIT = int(os.environ.get('DAILY_ERROR_LIMIT', 10000))
    MAX_ERROR_PAYLOAD_SIZE = int(os.environ.get('MAX_ERROR_PAYLOAD_SIZE', 65536))
