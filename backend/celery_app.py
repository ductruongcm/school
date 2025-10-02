from celery import Celery
from configs import Configs

celery = Celery(__name__, 
                broker = Configs.CELERY_BROKER_URL, 
                backend = Configs.CELERY_RESULT_BACKEND,
                include = ['app.tasks']
                )
