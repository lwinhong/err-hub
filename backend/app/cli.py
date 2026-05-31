import click
from flask import current_app

from app.extensions import db
from app.models.user import User


def register_cli(app):
    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        username = current_app.config['SUPERADMIN_USERNAME']
        password = current_app.config['SUPERADMIN_PASSWORD']
        existing = User.query.filter_by(username=username).first()
        if not existing:
            admin = User(username=username, is_admin=True)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            click.echo(f'Superadmin user "{username}" created.')
        else:
            click.echo(f'Superadmin user "{username}" already exists.')
        click.echo('Database initialized.')

    @app.cli.command('cleanup')
    def cleanup():
        from app.services.cleanup import cleanup_old_errors
        retention_days = current_app.config['DATA_RETENTION_DAYS']
        count = cleanup_old_errors(retention_days)
        click.echo(f'Deleted {count} errors older than {retention_days} days.')
