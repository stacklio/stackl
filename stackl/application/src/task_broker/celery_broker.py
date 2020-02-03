from celery import Celery

class CeleryWrapper(TaskBroker):

    
    def __init__(self):
        self.app = Celery('tasks', broker='redis://localhost')

    @app.task
    def add(self, x, y):
        return x + y
