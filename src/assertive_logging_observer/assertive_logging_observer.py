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
    """
    Available modes for AssertiveLoggingObserver.
    - REPORTING means AssertiveLoggingObserver will just report observations.
    - ASSERTING means AssertiveLoggingObserver will report and assert
      observations.
    """

    REPORTING = 0
    ASSERTING = 1


class AssertiveLoggingObserver:
    """
    Observing object which observes values, expressions, and commands in test
    functionality and (depending on set mode) has the following behavior:
    - if in mode AssertiveLoggingObserverMode.REPORTING only report on
      observations (WARN on FAILs)
    - if in mode AssertiveLoggingObserverMode.ASSERTING report and assert on
      observations (ERROR on FAILs)
    """

    def __init__(
        self: AssertiveLoggingObserver,
        mode: AssertiveLoggingObserverMode,
        logger: logging.Logger,
    ):
        """
        Initialize a AssertiveLoggingObserver instance.

        :param mode: behavior mode for observations.
        :param logger: logger to log observations to.
        """
        self.mode = mode
        self.logger = logger
        self.event_tracer = None

    def set_event_tracer(
        self: AssertiveLoggingObserver, event_tracer: TangoEventTracer
    ):
        """
        Sets the event_tracer for state change observations and LRC
        observations.

        :param event_tracer: TangoEventTracer to observer events from, must
            be subscribed to:
            - correct state attribute of correct device FQDN for calls to
              observe_device_state_change
            - longRunningCommandResult of correct device FQDN for calls to
              observe_lrc_result
        """
        self.event_tracer = event_tracer

    def remove_event_tracer(self: AssertiveLoggingObserver):
        """
        Remove the current event_tracer.
        """
        self.event_tracer = None

    def _log_pass(
        self: AssertiveLoggingObserver, function_name: str, result: str
    ):
        """
        Log message of PASS observation to logger.
        """
        self.logger.info(
            f"PASS: AssertiveLoggingObserver.{function_name} "
            f"observed: {result}"
        )

    def _log_fail(
        self: AssertiveLoggingObserver, function_name: str, result: str
    ):
        """
        Log message of FAIL observation to logger, WARNING if in REPORTING
        and ERROR if in ASSERTING.
        """
        msg = (
            f"FAIL: AssertiveLoggingObserver.{function_name} "
            f"observed: {result}"
        )
        if self.mode == AssertiveLoggingObserverMode.ASSERTING:
            self.logger.error(msg)
        else:
            self.logger.warning(msg)

    def observe_true(self: AssertiveLoggingObserver, test_bool: bool):
        """
        Observes True for given test_bool.

        :param test_bool: bool to observe if is True.
        """
        if test_bool:
            self._log_pass("observe_true", test_bool)
        else:
            self._log_fail("observe_true", test_bool)
            if self.mode == AssertiveLoggingObserverMode.ASSERTING:
                fail()

    def observe_false(self: AssertiveLoggingObserver, test_bool: bool):
        """
        Observes False for given test_bool.

        :param test_bool: bool to observe if is False.
        """
        if not test_bool:
            self._log_pass("observe_false", test_bool)
        else:
            self._log_fail("observe_false", test_bool)
            if self.mode == AssertiveLoggingObserverMode.ASSERTING:
                fail()

    def observe_equality(
        self: AssertiveLoggingObserver, test_val1: Any, test_val2: Any
    ):
        """
        Observes equality between given test_val1 and test_val2.

        :param test_val1: first value to observe if is equal to test_val2.
        :param test_val2: second value to observe if is equal to test_val1.
        """
        if test_val1 == test_val2:
            self._log_pass("observe_equality", f"{test_val1} == {test_val2}")
        else:
            self._log_fail("observe_equality", f"{test_val1} =/= {test_val2}")
            if self.mode == AssertiveLoggingObserverMode.ASSERTING:
                fail()

    def observe_device_state_change(
        self: AssertiveLoggingObserver,
        device_name: str,
        target_state_name: str,
        target_state: Any,
        timeout_state_change: float,
    ):
        """s"""
        if self.event_tracer is None:
            raise RuntimeError(
                "event_tracer must not be None for "
                "AssertiveLoggingObserver.observe_device_state_change"
            )

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
        if self.event_tracer is None:
            raise RuntimeError(
                "event_tracer must not be None for "
                "AssertiveLoggingObserver.observe_lrc_result"
            )

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
