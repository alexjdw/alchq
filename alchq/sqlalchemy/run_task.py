import os
from time import time

class Config:
    TASKS_PER_BATCH = os.environ.get("ALCHQ_TASKS_PER_BATCH", 20)


def run_tasks_forever(Q, sleep_time_when_no_tasks=.01):
    """ Cleans out the queue and then sleeps for a bit before checking for new tasks. """
    while True:
        run_all_tasks(Q)
        time.sleep(sleep_time_when_no_tasks)


def run_all_tasks(Q):
    """ Cleans out the queue. """
    ids = Q._alchq_base_query.order_by(
        Q.time_created.asc()
    ).limit(
        Config.TASKS_PER_BATCH
    ).update(
        status=Q.PROCESSING
    ).returning(Q.id)
    tasks = Q._alchq_base_query.filter(Q.id.in_(ids)).all()

    while tasks:
        for task in tasks:
            try:
                task.run()
            except Exception as e:
                task.status = Q.ERROR
            task.status = Q.COMPLETED
            task._alchq_commit()

        ids = Q._alchq_base_query.order_by(
            Q.time_created.asc()
        ).limit(Config.TASKS_PER_BATCH).update(status=Q.PROCESSING).returning(Q.id)

        tasks = Q._alchq_base_query.filter(Q.id.in_(ids)).all()


def run_n_tasks(Q, count):
    """ Runs N tasks. If less tasks are queued."""
    batch_count = (count, Config.TASKS_PER_BATCH)[count < Config.TASKS_PER_BATCH]
    query = Q._alchq_base_query
    ids = query.order_by(
        Q.time_created.asc()
    ).limit(batch_count).update(status=Q.PROCESSING).returning(Q.id)
    tasks = Q._alchq_base_query.filter(Q.id.in_(ids)).all()

    while count and tasks:
        for task in tasks:
            try:
                task.run()
            except Exception as e:
                task.status = Q.ERROR
            task.status = Q.COMPLETED
            task._alchq_commit()

        ids = Q._alchq_base_query.order_by(
            Q.time_created.asc()
        ).limit(batch_count).update(status=Q.PROCESSING).returning(Q.id)

        tasks = Q._alchq_base_query.filter(Q.id.in_(ids)).all()

        count -= len(tasks)


def run_one_task(queue):
    return run_n_tasks(queue, 1)
