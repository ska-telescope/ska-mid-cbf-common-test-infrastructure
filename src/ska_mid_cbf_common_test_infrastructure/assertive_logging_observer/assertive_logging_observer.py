"""
Code for the AssertiveLoggingObserver which allows optional assertion or only
reporting of observations within test functionality.
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from assertpy import assert_that, fail
from ska_tango_base.base.base_device import DevVarLongStringArrayType
from ska_tango_testing.integration import TangoEventTracer


class AssertiveLoggingObserverMode(Enum):
    """
    Available modes for AssertiveLoggingObserver:

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
      observations
    - if in mode AssertiveLoggingObserverMode.ASSERTING report and assert on
      observations

    """

    def __init__(
        self: AssertiveLoggingObserver,
        mode: AssertiveLoggingObserverMode,
        logger: logging.Logger,
        use_event_tracer: bool = True,
    ):
        """
        Initialize a AssertiveLoggingObserver instance.

        :param mode: behavior mode for observations.
        :param logger: logger to log observations to.
        :param use_event_tracer: whether to assosiciate a TangoEventTracer to
            ALO or not.
        """
        self.logger = logger
        self.event_tracer = TangoEventTracer() if use_event_tracer else None
        self.mode = mode
        if self.mode == AssertiveLoggingObserverMode.ASSERTING:
            logger.info(
                "AssertiveLoggingObserver instantiated in mode: "
                f"{AssertiveLoggingObserverMode.ASSERTING}"
            )
        else:
            logger.info(
                "AssertiveLoggingObserver instantiated in mode: "
                f"{AssertiveLoggingObserverMode.REPORTING}"
            )

    def __del__(self: AssertiveLoggingObserver):
        if self.event_tracer is not None:
            self.reset_event_tracer()

    def _check_event_tracer(self: AssertiveLoggingObserver):
        """Checks if event_tracer exists and throws RuntimeError if not."""
        if self.event_tracer is None:
            raise RuntimeError(
                "No event_tracer associated with AssertiveLoggingObserver"
            )

    def subscribe_event_tracer(
        self: AssertiveLoggingObserver,
        device_name: str,
        attr_name: str,
    ):
        """
        Subscribe event tracer to given attr_name for given device_name.

        :param device_name: name of device to track attribute of
        :param attr_name: attribute to track events for
        """
        self._check_event_tracer()
        self.logger.info(
            f"ALO event_tracer subscribed to {device_name}: {attr_name}"
        )
        self.event_tracer.subscribe_event(device_name, attr_name)

    def clear_events(self: AssertiveLoggingObserver):
        """
        Clear events in event_tracer.
        """
        self.event_tracer.clear_events()

    def reset_event_tracer(self: AssertiveLoggingObserver):
        """
        Reset event_tracer back to original state.
        """
        self.clear_events()
        self.event_tracer.unsubscribe_all()

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
        Log message of FAIL observation to logger.
        """
        self.logger.error(
            f"FAIL: AssertiveLoggingObserver.{function_name} "
            f"observed: {result}"
        )

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

    def observe_device_attr_change(
        self: AssertiveLoggingObserver,
        device_name: str,
        target_attr_name: str,
        target_attr_val: Any,
        timeout_attr_change_sec: float,
    ):
        """
        Observes a change of attr target_attr_name to target attr
        target_attr_val for device FQDN device_name within a timeout of
        timeout_attr_change_sec seconds. PASS behavior is attr change
        successfully occurs within timeout, and FAIL otherwise.

        REQUIRES: for success requires the event_tracer is set and is
        subscribed to device_name for target_attr_name.

        :param device_name: FQDN of device to observe attr change from.
        :param target_attr_name: attribute name to attr to observe.
        :param target_attr_val: attribute value of new attr for
            target_attr_name to change to.
        :param timeout_attr_change_sec: maximum timeout to wait for attr
            change (seconds).
        :raises RuntimeError: error if use with no even_tracer.
        """
        self._check_event_tracer()

        try:

            assert_that(self.event_tracer).within_timeout(
                timeout_attr_change_sec
            ).has_change_event_occurred(
                device_name=device_name,
                attribute_name=target_attr_name,
                attribute_value=target_attr_val,
            )
            self._log_pass(
                "observe_device_attr_change",
                f"successfully captured (device: {device_name} | "
                f"state_name: {target_attr_name} | "
                f"target_attr_val: {target_attr_val} | "
                f"within timeout: {timeout_attr_change_sec}s)",
            )

        except AssertionError as exception:

            self._log_fail(
                "observe_device_attr_change",
                f"did not capture (device: {device_name} | "
                f"state_name: {target_attr_name} | "
                f"target_attr_val: {target_attr_val} | "
                f"within timeout: {timeout_attr_change_sec}s)",
            )
            if self.mode == AssertiveLoggingObserverMode.ASSERTING:
                raise exception

    def observe_lrc_ok(
        self: AssertiveLoggingObserver,
        device_name: str,
        lrc_cmd_result: DevVarLongStringArrayType,
        lrc_cmd_name: str,
        timeout_lrc_sec: float,
    ):
        """
        Observes longRunningCommandResult results in
        [0, "{lrc_cmd_name} completed OK"] for device FQDN device_name within
        a timeout of timeout_lrc_sec seconds. PASS behavior is stated
        longRunningCommandResult succesfully occurs within timeout, and FAIL
        otherwise. Long running command (LRC) concept can be found at
        https://developer.skao.int/projects/ska-tango-base/en/latest/concepts/
        long-running-commands.html.

        REQUIRES: for success requires the event_tracer is set and is
        subscribed to device_name for longRunningCommandResult.

        :param device_name: FQDN of device to observe longRunningCommandResult
            from.
        :param lrc_cmd_result: DevVarLongStringArrayType containing LRC ID as
            second item in iterable.
        :param lrc_cmd_name: basic command name of LRC.
        :param timeout_lrc_sec: maximum timeout to wait for successful
            longRunningCommandResult (seconds).
        :raises RuntimeError: error if use with no even_tracer.
        """
        self._check_event_tracer()

        try:

            assert_that(self.event_tracer).within_timeout(
                timeout_lrc_sec
            ).has_change_event_occurred(
                device_name=device_name,
                attribute_name="longRunningCommandResult",
                attribute_value=(
                    f"{lrc_cmd_result[1][0]}",
                    f'[0, "{lrc_cmd_name} completed OK"]',
                ),
            )
            self._log_pass(
                "observe_lrc_ok",
                f"successfully captured (device: {device_name} | "
                f"LRC_command: {lrc_cmd_result[1][0]} | "
                f"result: "
                f'[0, "{lrc_cmd_name} completed OK"]'
                " | "
                f"within timeout: {timeout_lrc_sec}s)",
            )

        except AssertionError as exception:

            self._log_fail(
                "observe_lrc_ok",
                f"did not capture (device: {device_name} | "
                f"LRC_command: {lrc_cmd_result[1][0]} | "
                f"result: "
                f'[0, "{lrc_cmd_name} completed OK"]'
                " | "
                f"within timeout: {timeout_lrc_sec}s)",
            )
            if self.mode == AssertiveLoggingObserverMode.ASSERTING:
                raise exception
