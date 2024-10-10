from abc import ABC, abstractmethod
from datetime import datetime, timezone


class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(tz=timezone.utc)


class MockClock(Clock):
    def __init__(self, fixed_time: datetime):
        self._fixed_time = fixed_time

    def now(self) -> datetime:
        return self._fixed_time
