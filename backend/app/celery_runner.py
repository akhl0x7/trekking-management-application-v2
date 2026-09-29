from . import create_app
from . import tasks

app = create_app()
celery = tasks.celery
