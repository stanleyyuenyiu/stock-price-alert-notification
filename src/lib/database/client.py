from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy import create_engine
from contextlib import contextmanager, AbstractContextManager
from typing import Callable
import contextvars
import dataclasses

@dataclasses.dataclass
class DbClientConfig:
    dsn: str
    autoflush: bool = False
    autocommit: bool = False

session_context = contextvars.ContextVar("session", default=None)

class DbClient():
    def __init__(self, config:DbClientConfig) -> None:
        print("init DB client")
        engine = create_engine(
            config.dsn
        )
        self._cfg = config
        self._eng = engine
        self._session_factory = scoped_session(
            sessionmaker(
                autocommit=self._cfg.autocommit,
                autoflush=self._cfg.autoflush,
                bind=self._eng,
            ),
        )
        self._t = 0

    # def create_database(self) -> None:
    #     Base.metadata.create_all(self._engine)

    def has_session(self):
        return session_context.get() is not None

    def get_session(self):
        return session_context.get()

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session = session_context.get()
        if not session:
            print("init session")
            session: Session = self._session_factory()
            session_context.set(session)
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            print("close", session)
            session.close()