from .tasks import app_celery

if __name__ == "__main__":
    app_celery.worker_main(argv=["worker", "--pool=solo", "--loglevel=info"])
