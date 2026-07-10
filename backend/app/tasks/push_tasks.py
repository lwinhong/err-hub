from datetime import datetime, timezone

import croniter

from app.tasks import celery_app


def _get_celery_task():
    if celery_app is None:
        return None

    flask_app = celery_app.flask_app

    @celery_app.task(name='app.tasks.push_tasks.execute_push_task')
    def execute_push_task(schedule_id):
        """执行单个推送任务"""
        with flask_app.app_context():
            from app.models.push_schedule import PushSchedule
            from app.services.push_service import execute_push

            schedule = PushSchedule.query.get(schedule_id)
            if schedule and schedule.is_active:
                try:
                    execute_push(schedule)
                except Exception as e:
                    from app.extensions import db
                    from app.models.push_log import PushLog
                    log = PushLog(
                        schedule_id=schedule.id,
                        status='failed',
                        error_message=str(e),
                    )
                    db.session.add(log)
                    db.session.commit()

    @celery_app.task(name='app.tasks.push_tasks.check_and_execute_pushes')
    def check_and_execute_pushes():
        """检查并执行到期的推送任务"""
        with flask_app.app_context():
            from app.models.push_schedule import PushSchedule

            now = datetime.now(timezone.utc)
            active_schedules = PushSchedule.query.filter_by(is_active=True).all()

            for schedule in active_schedules:
                last_run = schedule.last_pushed_at or schedule.created_at
                # Strip tzinfo for comparison — croniter returns naive datetimes
                last_run_naive = last_run.replace(tzinfo=None) if last_run.tzinfo else last_run
                cron = croniter.croniter(schedule.cron_expression, last_run_naive)
                next_run = cron.get_next(datetime)

                if next_run <= now.replace(tzinfo=None):
                    execute_push_task.delay(str(schedule.id))

    return execute_push_task, check_and_execute_pushes


_execute_push_task, _check_and_execute_pushes = _get_celery_task() or (None, None)
