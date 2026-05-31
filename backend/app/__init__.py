import os

import redis
from flask import Flask
from flask_cors import CORS

from app.config import DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate


def create_app():
    app = Flask(__name__)

    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    app.redis = redis.from_url(app.config['REDIS_URL'])

    from app.api.v1 import bp as api_v1_bp
    from app.api.v1.auth import bp as auth_bp
    from app.api.v1.projects import bp as projects_bp
    from app.api.v1.errors import bp as errors_bp
    from app.api.v1.dashboard import bp as dashboard_bp

    app.register_blueprint(api_v1_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(dashboard_bp)

    from app.cli import register_cli
    register_cli(app)

    return app
