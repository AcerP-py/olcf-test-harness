import sqlite3 as sq
from pathlib import Path
from typing import Optional

from harness.config import oth_config

from .base import Run, RunEvent, RunState, StatusDB


class SqliteStatusDB(StatusDB):
    schema: str = """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS runs (
            id          INTEGER NOT NULL PRIMARY KEY,
            application TEXT    NOT NULL,
            test        TEXT    NOT NULL,
            test_path   TEXT    NOT NULL,
            run_path    TEXT    NOT NULL,
            state       INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS events (
            run          INTEGER PRIMARY KEY,
            build_start  TEXT,
            build_end    TEXT,
            submit_start TEXT,
            submit_end   TEXT,
            binary_start TEXT,
            binary_end   TEXT,
            check_start  TEXT,
            check_end    TEXT,

            CONSTRAINT events_run_fk
                FOREIGN KEY (run)
                REFERENCES runs (id)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION
        );
    """
    init_run_query: str = """
        INSERT INTO runs (
            id, application, test, test_path, run_path, state
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """

    def __init__(self, path: Optional[Path] = None):
        self.db_path: Path = (
            path if path else Path(oth_config.get("status_sqlite_db_path")).absolute()
        )

        self.connection: sq.Connection = sq.connect(str(self.db_path))
        self.cursor: sq.Cursor = self.connection.cursor()

        self.cursor.executescript(self.schema)
        self.connection.commit()

    def init_run(self, run: Run) -> None:
        self.cursor.execute(
            self.init_run_query,
            (
                run.id,
                run.application,
                run.test,
                run.test_path,
                run.run_path,
                RunState.PENDING.value,
            ),
        )
        self.connection.commit()

    def log_run_event(self, run: Run, event: RunEvent) -> None:
        pass
