"""
Code for the Assertive Logging Observer which allows optional assertion of
state change and success of LRCs or just reporting of state of LRC without
assertion.
"""
from __future__ import annotations

import logging
from enum import Enum
from time import sleep
from typing import Any

from assertpy import assert_that
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
        self: AssertiveLoggingObserver,
        mode: AssertiveLoggingObserverMode,
        logger: logging.Logger,
    ):
        self.mode = mode
        self.logger = logger
        self.event_tracer = None

    def set_event_tracer(
        self: AssertiveLoggingObserver, event_tracer: TangoEventTracer
    ) -> None:
        """a"""
        self.event_tracer = event_tracer

    def _format_report(
        self: AssertiveLoggingObserver, function_name: str, result: str
    ) -> str:
        return f"AssertiveLoggingObserver.{function_name} received {result}"

    def observe_true(self: AssertiveLoggingObserver, test_bool: bool) -> None:
        """Observes true in given test_bool"""
        self.logger.info(self._format_report("observe_true", test_bool))
        if self.mode == AssertiveLoggingObserverMode.ASSERTING:
            assert_that(test_bool).is_true()

    def observe_false(self: AssertiveLoggingObserver, test_bool: bool) -> None:
        """Observes false in given test_bool"""
        self.logger.info(self._format_report("observe_false", test_bool))
        if self.mode == AssertiveLoggingObserverMode.ASSERTING:
            assert_that(test_bool).is_false()

    def observe_device_state_change(
        self: AssertiveLoggingObserver,
        device_name: str,
        target_state_name: str,
        target_state: Any,
        timeout_state_change: int,
    ) -> None:
        """s"""
        print(device_name)
        print(target_state_name)
        print(target_state)
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

        # else:

    def observe_lrc_result(
        self: AssertiveLoggingObserver,
        device_name: str,
        device_lrc_cmd_result: Any,
        lrc_cmd_name: str,
        timeout_lrc: int,
    ):
        """s"""
        print(device_lrc_cmd_result)
        print(device_name)
        print(lrc_cmd_name)
        print(timeout_lrc)
        print(self.event_tracer.events)
        assert False

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
