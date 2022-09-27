import logging
from importlib import import_module
from pathlib import Path

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.future import Engine
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.orm import registry
from sqlalchemy.orm import sessionmaker

from core import settings

try:
    from sqlalchemy.orm import declarative_base
    from sqlalchemy.orm import DeclarativeMeta
except ImportError:
    # SQLAlchemy <= 1.3
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.ext.declarative import DeclarativeMeta

# Scope the session to the current greenlet if greenlet is available,
# otherwise fall back to the current thread.
try:
    from greenlet import getcurrent as _ident_func
except ImportError:
    from threading import get_ident as _ident_func

log: logging.Logger = logging.getLogger(__name__)


class Database:
    ENGINE: Engine = create_engine(settings.DATABASE_URL, future=True)

    # When using the ORM, the MetaData collection remains present,
    # however it itself is contained within an ORM-only object known as the registry.
    REGISTRY: registry = registry()

    # In the most common approach, each mapped class descends from a common base class known as the declarative base.
    # We get a new declarative base from the registry using the registry.generate_base() method.
    BASE = REGISTRY.generate_base()

    # The steps of creating the registry and “declarative base” classes can be combined into one step
    # using the historically familiar declarative_base() function.
    #   from sqlalchemy.orm import declarative_base
    #   Base = declarative_base()

    # Normal session, we need do anything with session, when we finish work, we need to close it manually.
    # Or using session.begin() in a context manager.
    sess: Session = sessionmaker(ENGINE)

    session: scoped_session = scoped_session(sess, scopefunc=_ident_func)

    def __init__(self):
        try:
            self.session()
        except Exception as e:
            log.exception(f"[Database] Session started failed due to {e}")
        log.info("[Database] Connection successful, session started.")

    @property
    def metadata(self) -> MetaData:
        # Having a single MetaData object for an entire application is the most common case,
        # represented as a module-level variable in a single place in an application,
        # often in a “models” or “dbschema” type of package.
        # A MetaData object that will store a collection of Table objects.
        return self.REGISTRY.metadata

    def create_all(self):
        self.metadata.create_all(self.ENGINE)

    def drop_all(self):
        self.metadata.drop_all(self.ENGINE)


db = Database()


# load models
def load_models(path: str = "models"):
    loaded_models: list = []
    for path in sorted(Path(path).rglob("*.py")):
        module_path: str = ".".join(path.parent.parts + (path.stem,))
        module = import_module(module_path)

        for name in vars(module).keys():
            try:
                if isinstance(getattr(module, name), DeclarativeMeta):
                    table_name: str = getattr(module, name).__tablename__
                    print(f"Registering table '{table_name}'")
                    loaded_models.append(getattr(module, name))

            except Exception:
                pass

    print(f"Loaded {len(loaded_models)} tables")


load_models(settings.MODELS_PATH)
