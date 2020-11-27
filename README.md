# alchq
SQLAlchemy-based task queue.

### install

`pip install alchq`  # TODO

### demo
```
from my_app import db
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
```

Creating a task:

```
from my_app import db
from my_app.tasks import MyTask


db.session.add(MyTask(operation="hop"))
db.session.commit()
```

Creating a worker using flask CLI:

```
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
```

Then you have access to this command-line command:
`flask alchq run`

This will start the queue and is easy to put into a docker container or kubernetes pod. (you can also just run it locally for testing)

### concept

Most of the time I'm creating a task queue in Python, I look to the amazing Celery project. However, I noticed that most of the time I need Celery, I also want to set up RabbitMQ, Redis, and Flower for consistency and monitoring. I also want to access my data in a SQL database. This results in a lot of config and sprawl for what's likely a simple task. We can replace all of the above with SQL.

Reading from / writing to SQL on a per-task basis is fairly expensive compared to a dedicated queue system, so this queue type is very appropriate for apps that are already running SQL as a data store and using SQLAlchemy. The idea is that once you create an instance of your model, it's given a status of PENDING, and then a worker process just checks for the oldest PENDING task, sets it to PROCESSING, executes it, and sets it to PROCESSED. Tasks that crash are set to ERROR, and the error() function on the base model is called to perform cleanup.

Since the task has access to both the Flask app and the database, it's maximally flexible. It can create more tasks and update itself. The Flask App can also implement its own monitoring and provide an API without relying on an external process like Flower.
