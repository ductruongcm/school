from celery_app import celery
from app import launch

flask_app = launch()

celery.conf.update(flask_app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask


