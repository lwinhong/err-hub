import os

import redis
from flask import Flask, send_from_directory
from flask_cors import CORS

from app.config import DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate


def create_app():
    app = Flask(__name__, static_folder='static')

    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    app.redis = redis.from_url(app.config['REDIS_URL'])

    # ---- SDK 静态文件路由 ----
    @app.route('/sdk/<path:filename>')
    def serve_sdk(filename):
        return send_from_directory(
            app.static_folder, filename,
            mimetype='application/javascript',
            max_age=3600,
        )

    from app.api.v1 import bp as api_v1_bp
    from app.api.v1.auth import bp as auth_bp
    from app.api.v1.projects import bp as projects_bp
    from app.api.v1.errors import bp as errors_bp
    from app.api.v1.dashboard import bp as dashboard_bp
    from app.api.v1.users import bp as users_bp
    from app.api.v1.settings import bp as settings_bp
    from app.api.v1.captcha import bp as captcha_bp

    app.register_blueprint(api_v1_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(captcha_bp)

    from app.cli import register_cli
    register_cli(app)

    return app
