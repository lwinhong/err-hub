from app import create_app

flask_app = create_app()
celery = flask_app.celery # type: ignore

# Import tasks AFTER celery is initialized so tasks can register properly.
# push_tasks.py references celery_app at module level; if imported before
# init_celery() runs, the tasks are never registered.
from app.tasks import push_tasks  # noqa: E402, F401
