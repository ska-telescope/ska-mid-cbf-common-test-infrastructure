"""
Code for the Assertive Logging Observer which allows optional assertion of
state change and success of LRCs or just reporting of state of LRC without
assertion.
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Any

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

    def _log_pass(
        self: AssertiveLoggingObserver, function_name: str, result: str
    ) -> str:
        self.logger.info(
            f"PASS: AssertiveLoggingObserver.{function_name} "
            f"observed: {result}"
        )

    def _log_fail(
        self: AssertiveLoggingObserver, function_name: str, result: str
    ) -> str:
        msg = (
            f"FAIL: AssertiveLoggingObserver.{function_name} "
            f"observed: {result}"
        )
        if self.mode == AssertiveLoggingObserverMode.ASSERTING:
            self.logger.error(msg)
        else:
            self.logger.warning(msg)

    def observe_true(self: AssertiveLoggingObserver, test_bool: bool) -> None:
        """Observes true in given test_bool"""
        if test_bool:
            self._log_pass("observe_true", test_bool)
        else:
            self._log_fail("observe_true", test_bool)
            if self.mode == AssertiveLoggingObserverMode.ASSERTING:
                fail()

    def observe_false(self: AssertiveLoggingObserver, test_bool: bool) -> None:
        """Observes false in given test_bool"""
        if not test_bool:
            self._log_pass("observe_false", test_bool)
        else:
            self._log_fail("observe_false", test_bool)
            if self.mode == AssertiveLoggingObserverMode.ASSERTING:
                fail()

    def observe_device_state_change(
        self: AssertiveLoggingObserver,
        device_name: str,
        target_state_name: str,
        target_state: Any,
        timeout_state_change: float,
    ) -> None:
        """s"""
        try:

            assert_that(self.event_tracer).within_timeout(
                timeout_state_change
            ).has_change_event_occurred(
                device_name=device_name,
                attribute_name=target_state_name,
                attribute_value=target_state,
            )

            self._log_pass(
                "observe_device_state_change",
                f"successfully captured (device: {device_name} | "
                f"state: {target_state_name} | "
                f"state_change: {target_state} | "
                f"within timeout: {timeout_state_change}s)",
            )

        except AssertionError as exception:

            self._log_fail(
                "observe_device_state_change",
                f"did not capture (device: {device_name} | "
                f"state: {target_state_name} | "
                f"state_change: {target_state} | "
                f"within timeout: {timeout_state_change}s)",
            )

            if self.mode == AssertiveLoggingObserverMode.ASSERTING:
                raise exception

    def observe_lrc_result(
        self: AssertiveLoggingObserver,
        device_name: str,
        device_lrc_cmd_result: Any,
        lrc_cmd_name: str,
        timeout_lrc: float,
    ):
        """s"""
        try:

            assert_that(self.event_tracer).within_timeout(
                timeout_lrc
            ).has_change_event_occurred(
                device_name=device_name,
                attribute_name="longRunningCommandResult",
                attribute_value=(
                    f"{device_lrc_cmd_result[1][0]}",
                    f'[0, "{lrc_cmd_name} completed OK"]',
                ),
            )

            self._log_pass(
                "observe_lrc_result",
                f"successfully captured (device: {device_name} | "
                f"LRC_command: {device_lrc_cmd_result[1][0]} | "
                f"result: "
                f'[0, "{lrc_cmd_name} completed OK"]'
                " | "
                f"within timeout: {timeout_lrc}s)",
            )

        except AssertionError as exception:

            self._log_fail(
                "observe_lrc_result",
                f"did not capture (device: {device_name} | "
                f"LRC_command: {device_lrc_cmd_result[1][0]} | "
                f"result: "
                f'[0, "{lrc_cmd_name} completed OK"]'
                " | "
                f"within timeout: {timeout_lrc}s)",
            )

            if self.mode == AssertiveLoggingObserverMode.ASSERTING:
                raise exception
