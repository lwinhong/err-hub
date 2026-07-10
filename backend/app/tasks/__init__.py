celery_app = None


def init_celery(app):
    global celery_app
    try:
        from celery import Celery

        celery = Celery(
            app.import_name,
            broker=app.config['REDIS_URL'],
            backend=app.config['REDIS_URL'],
        )
        celery.conf.update(app.config)

        from celery.schedules import crontab
        celery.conf.beat_schedule = {
            'check-push-schedules': {
                'task': 'app.tasks.push_tasks.check_and_execute_pushes',
                'schedule': crontab(minute='*/1'),
            },
        }
        celery.conf.timezone = 'UTC'

        celery.flask_app = app
        celery_app = celery
        app.celery = celery
    except ImportError:
        app.logger.warning('celery not installed, background push tasks disabled')
