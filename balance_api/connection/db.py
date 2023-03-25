import types
import functools

import backoff
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, Session as OrmSession
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from balance_api import config


@contextmanager
def session_scope() -> OrmSession:
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


engine = create_engine(config.SQLALCHEMY_DATABASE_URI, insertmanyvalues_page_size=100)
Session = sessionmaker(bind=engine)


def database_operation(**backoff_kwargs):
    def decorator(func):
        @retry_on_database_error(**backoff_kwargs)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with session_scope() as session:
                kwargs["session"] = session
                return_value = func(*args, **kwargs)

                if isinstance(return_value, types.GeneratorType):
                    raise TypeError(
                        "database_operation doesn't support usage with generator type"
                    )

                return return_value

        return wrapper

    return decorator


def should_giveup_retrying_database_operation(exc):
    return not exc.connection_invalidated


def retry_on_database_error(**kwargs):
    kwargs.setdefault("max_time", 60)
    return backoff.on_exception(
        backoff.expo,
        OperationalError,
        giveup=should_giveup_retrying_database_operation,
        **kwargs
    )
