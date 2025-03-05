"""
Code for the Assertive Logging Observer which allows optional assertion of
state change and success of LRCs or just reporting of state of LRC without
assertion.
"""

import logging
from enum import Enum
from time import sleep
from typing import Any

import tango
from assertpy import assert_that, fail
from ska_tango_testing.integration import TangoEventTracer


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

    def set_event_tracer(self, event_tracer: TangoEventTracer) -> None:
        self.event_tracer = event_tracer

    def _format_report(self, function_name: str, result: str) -> str:
        return f"AssertiveLoggingObserver.{function_name} received {result}"

    def observe_true(self, test_bool: bool) -> None:
        """Observes true in given test_bool"""
        self.logger.info(self._format_report("observe_true", test_bool))
        if self.mode == AssertiveLoggingObserverMode.ASSERTING:
            assert_that(test_bool).is_true()

    def observe_false(self, test_bool: bool) -> None:
        """Observes false in given test_bool"""
        self.logger.info(self._format_report("observe_false", test_bool))
        if self.mode == AssertiveLoggingObserverMode.ASSERTING:
            assert_that(test_bool).is_false()

    def observe_device_lrc_state_change(
        self,
        device_lrc_cmd_result: Any,
        device_name: str,
        lrc_cmd_name: str,
        target_state_name: str,
        target_state: Any,
        timeout_state_change: int,
        timeout_lrc: int,
    ) -> None:
        """"""
        sleep(timeout_state_change)
        print(self.event_tracer.events)
        assert False
        # if self.mode == AssertiveLoggingObserverMode.ASSERTING:

        #     assert_that(self.event_tracer).within_timeout(
        #         timeout_state_change
        #     ).has_change_event_occurred(
        #         device_name=device_name,
        #         attribute_name=target_state_name,
        #         attribute_value=target_state,
        #     )

        #     assert_that(self.event_tracer).within_timeout(
        #         timeout_lrc
        #     ).has_change_event_occurred(
        #         device_name=device_name,
        #         attribute_name="longRunningCommandResult",
        #         attribute_value=(
        #             f"{device_lrc_cmd_result[1][0]}",
        #             f'[0, "{lrc_cmd_name} completed OK"]',
        #         ),
        #     )

        # else:
