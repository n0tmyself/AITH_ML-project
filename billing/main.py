import asyncio
import datetime
from contextlib import asynccontextmanager

import uvicorn
from celery.result import AsyncResult
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator, metrics

from .apps.broker.tasks import app_celery
from .apps.db.database import get_db, recreate_tables
from .apps.db.models import GenerationModel, TaskStatus
from .apps.handlers.logger import logger
from .apps.handlers.routers import all_routers


async def monitor_task(db: Session = Depends(get_db)):
    logger.info("Starting task monitoring...")
    try:
        while True:
            try:
                active_tasks = db.query(TaskStatus).all()
                logger.debug(f"Found {len(active_tasks)} active tasks to check")

                for task in active_tasks:
                    try:

                        result_task = AsyncResult(task.task_id, app=app_celery)

                        if result_task.ready():
                            logger.info(f"Task {task.task_id} is ready, processing...")

                            generation = (
                                db.query(GenerationModel)
                                .filter(GenerationModel.task_id == task.task_id)
                                .first()
                            )

                            if generation:
                                try:
                                    task_result = result_task.get()

                                    generation.result = task_result
                                    generation.status = True
                                    generation.processing_time = (
                                        datetime.datetime.now()
                                        - generation.created_date
                                    ).total_seconds()

                                    db.delete(task)
                                    db.commit()

                                    logger.info(
                                        f"Successfully updated generation {generation.id} with result"
                                    )

                                except Exception as e:
                                    db.rollback()
                                    logger.error(
                                        f"Error processing task result {task.task_id}: {str(e)}"
                                    )
                                    generation.status = False
                                    generation.result = f"Error: {str(e)}"
                                    db.commit()

                            else:
                                logger.warning(
                                    f"No generation found for task {task.task_id}, cleaning up"
                                )
                                db.delete(task)
                                db.commit()

                        elif result_task.failed():
                            logger.warning(f"Task {task.task_id} failed")

                            generation = (
                                db.query(GenerationModel)
                                .filter(GenerationModel.task_id == task.task_id)
                                .first()
                            )

                            if generation:
                                generation.status = False
                                generation.result = "Task failed"
                                db.delete(task)
                                db.commit()

                    except Exception as e:
                        logger.error(f"Error checking task {task.task_id}: {str(e)}")
                        continue

                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)

    except asyncio.CancelledError:
        logger.info("Task monitoring stopped gracefully")
        raise
    except Exception as e:
        logger.error(f"Monitoring crashed: {str(e)}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):

    monitor = asyncio.create_task(monitor_task())

    yield

    monitor.cancel()
    try:
        await monitor
    except asyncio.CancelledError:
        pass


app = FastAPI(title="MedAI", docs_url="/docs", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/openapi.json", "/favicon.ico"],
    inprogress_name="in_progress",
    inprogress_labels=True,
)

TRACKED_METRICS = [
    metrics.requests(),
    metrics.latency(),
]

for metric in TRACKED_METRICS:
    instrumentator.add(metric)

instrumentator.instrument(app, metric_namespace="service", metric_subsystem="service")
instrumentator.expose(app, include_in_schema=False, should_gzip=True)

for router in all_routers:
    app.include_router(router)

# recreate_tables()


@app.exception_handler(Exception)
async def custom_exception_handler(_: Request, exception: Exception):
    return JSONResponse(status_code=500, content={"message": str(exception)})


@app.get("/", include_in_schema=False)
def docs():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        app="billing.main:app",
        host="0.0.0.0", 
        port=8000, 
        log_level="info", 
        reload=True
    )
