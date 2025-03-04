"""
Code for the Assertive Logging Observer which allows optional assertion of
state change and success of LRCs or just reporting of state of LRC without
assertion.
"""

import logging
from enum import Enum


class AssertiveLoggingObserverMode(Enum):
    """Possible reporting modes for AssertiveLoggingObserver"""

    REPORTING = 0
    ASSERTING = 1


class AssertiveLoggingObserver:
    """
    Observing object which is set in an AssertiveLoggingObserverMode and acts
    as an observer in test functionality. Depending on the mode it is
    set to the observer will:
    - assert and report progress and results if in
      AssertiveLoggingObserverMode.ASSERTING
    - only report progress and results if in
      AssertiveLoggingObserverMode.REPORTING
    """

    def __init__(
        self, mode: AssertiveLoggingObserverMode, logger: logging.Logger
    ):
        self.mode = mode
        self.logger = logger

    def _format_report(self, function_name: str, result: str) -> str:
        return f"AssertiveLoggingObserver.{function_name} received {result}"

    def observe_true(self, test_bool: bool) -> None:
        """Observes true in given test_bool"""
        self.logger.info(self._format_report("observe_true", test_bool))
        if self.mode == AssertiveLoggingObserverMode.ASSERTING:
            assert (
                test_bool
            ), f'Error: {self._format_report("observe_false", test_bool)}'

    def observe_false(self, test_bool: bool) -> None:
        """Observes false in given test_bool"""
        self.logger.info(self._format_report("observe_false", test_bool))
        if self.mode == AssertiveLoggingObserverMode.ASSERTING:
            assert (
                not test_bool
            ), f'Error: {self._format_report("observe_false", test_bool)}'
