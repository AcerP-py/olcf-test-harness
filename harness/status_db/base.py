from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path


class RunEvent(Enum):
    BUILD_START = 0
    BUILD_END = 1
    SUBMIT_START = 2
    SUBMIT_END = 3
    EXECUTE_START = 4
    EXECUTE_END = 5
    CHECK_START = 6
    CHECK_END = 7


class RunState(Enum):
    PENDING = 0
    BUILDING = 1
    SUBMITTED = 2
    EXECUTING = 3
    CHECKING = 4
    SUCCEEDED = 5
    FAILED = 6


class Run:
    # TODO: replace with other harness state

    def __init__(
        self, id: str, application: str, test: str, test_path: Path, run_path: Path
    ):
        self.id: str = id
        self.application: str = application
        self.test: str = test
        self.test_path: Path = test_path
        self.run_path: Path = run_path


class StatusDB(ABC):
    @abstractmethod
    def init_run(self, run: Run) -> None:
        pass

    @abstractmethod
    def log_run_event(self, run: Run, event: RunEvent) -> None:
        pass
