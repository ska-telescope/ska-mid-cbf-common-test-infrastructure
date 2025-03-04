from enum import Enum


def hello():
    print("Hello")


class AssertiveLoggingObserverMode(Enum):
    REPORTING = 0
    ASSERTING = 1


class AssertiveLoggingObserver:
    def __init__(self, mode: AssertiveLoggingObserverMode):
        self.mode = mode
