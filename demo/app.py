from alchq import BaseQueue


class MyTask(BaseQueue):
    """ A task. """
    id = db.Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    operation = db.Column(db.String())
    retries = db.Column(db.Integer(), default=0)

    # time_created: added by BaseQueue
    # time_updated: added by BaseQueue
    # status: added by BaseQueue

    def run(self):
        """ Run when the next task is available. """
        if self.operation == "hop":
            print("Hippity-hop!")
        elif self.operation == "skip":
            print("Skipped a beat!")
        elif self.operation == "jump":
            print("Jumped 3 feet!")
        else:
            raise ValueError("Operation wasn't hop, skip, or jump!")

    def error(self, exc):
        """ Runs if the task fails for any reason. """
        from flask import current_app as app

        if isinstance(exc, ValueError):
            app.logger.error("I found a ValueError!")

        elif self.retries < 3:
            # create a whole new entry
            # this way the data that failed sticks around
            retry = MyTask(
                operation=self.operation,
                retries=self.retries + 1
            )
            db.session.add(retry)
            db.session.commit()
        else:
            app.logger.error("Max retries exceeded.")

from my_app import db
from my_app.tasks import MyTask


db.session.add(MyTask(operation="hop"))
db.session.commit()


def configure_queue_worker(app):
    queue = AppGroup("alchq_queue")

    @queue.command("run")
    def run():
        from alchq import worker
        from my_app.tasks import MyTask

        worker.process_forever(MyTask)
        # also avaiable:
        # worker.process_one(MyTask)  -> processes task one time.
        # worker.process_n(MyTask, n) -> processes task n times.

    app.cli.add_command(test_cli)


# in your flask app setup:
configure_queue_worker(app)
