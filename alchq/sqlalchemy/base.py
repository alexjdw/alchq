import enum
from sqlalchemy import Enum, func, text


class StatusEnum(enum.Enum):
    PENDING = 0
    PROCESSING = 1
    COMPLETED = 2
    ERROR = 3


def BaseQueue(db):
    """ This is actually a factory-style function that plugs into your db. """

    class BaseQueue(db.Model):
        __abstract__ = True
        id = db.Column()
        time_created = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())
        time_updated = db.Column(db.TIMESTAMP, nullable=False,
                                 server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
        status = db.Column(Enum(StatusEnum))

        # Quick access for ENUM values.
        PENDING = StatusEnum.PENDING
        PROCESSING = StatusEnum.PROCESSING
        COMPLETED = StatusEnum.COMPLETED
        ERROR = StatusEnum.ERROR

        def run(self):
            raise NotImplementedError("run() method not implemented on derived class.")

        def error(self):
            pass

        @property
        def _alchq_base_query(self):
            return db.session.query(self.__class__)

        def _alchq_commit(self):
            db.session.commit(self)

    return BaseQueue
