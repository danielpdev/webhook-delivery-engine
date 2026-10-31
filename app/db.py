"""Database factory. Tests inject isolated URLs; imports never touch a database."""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def database(url=None):
    url = url or os.getenv("DATABASE_URL", "sqlite:///./demo.sqlite")
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False, "timeout": 20} if url.startswith("sqlite") else {},
        pool_pre_ping=True,
    )
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def configure(conn, _):
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA journal_mode=WAL")

    Base.metadata.create_all(engine)
    return engine, sessionmaker(engine, expire_on_commit=False)
