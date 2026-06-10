import click
from flask import current_app
from sqlalchemy import inspect, text

from app.extensions import db
from app.models.user import User


def register_cli(app):
    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        _sync_missing_columns()
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

    def _sync_missing_columns():
        """检测并补齐已有表中缺失的列"""
        inspector = inspect(db.engine)
        existing_tables = set(inspector.get_table_names())
        added = []

        for table_name, table in db.metadata.tables.items():
            if table_name not in existing_tables:
                continue
            existing_cols = {c['name'] for c in inspector.get_columns(table_name)}
            for column in table.columns:
                if column.name not in existing_cols:
                    col_type = column.type.compile(db.engine.dialect)
                    default = ''
                    if column.default is not None and column.default.is_scalar:
                        val = column.default.arg
                        if isinstance(val, str):
                            default = f" DEFAULT '{val}'"
                        else:
                            default = f" DEFAULT {val}"
                    sql = f'ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}{default}'
                    db.session.execute(text(sql))
                    added.append(f'{table_name}.{column.name}')

        if added:
            db.session.commit()
            click.echo(f'Added missing columns: {", ".join(added)}')

    @app.cli.command('cleanup')
    def cleanup():
        from app.services.cleanup import cleanup_old_errors
        from app.models.setting import SystemSetting
        db_val = SystemSetting.get_value('data_retention_days')
        retention_days = int(db_val) if db_val is not None else current_app.config['DATA_RETENTION_DAYS']
        count = cleanup_old_errors(retention_days)
        click.echo(f'Deleted {count} errors older than {retention_days} days.')
