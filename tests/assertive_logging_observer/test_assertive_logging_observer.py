from __future__ import annotations

import logging
from threading import Event
from time import sleep
from typing import Callable, Optional

from assertpy import fail
from ska_control_model import TaskStatus
from ska_tango_base.base.base_device import (
    DevVarLongStringArrayType,
    SKABaseDevice,
)
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tango_base.executor.executor_component_manager import (
    TaskExecutorComponentManager,
)
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState
from tango.server import command
from tango.test_context import DeviceTestContext

import assertive_logging_observer.assertive_logging_observer as alo
from test_logging.format import LOG_FORMAT

# from ska_tango_test import ThreadedTestTangoContextManager

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
test_logger = logging.getLogger(__name__)


class MockPowerSwitchComponentManager(TaskExecutorComponentManager):
    def __init__(self, turn_on_cmd_callback):
        super().__init__(test_logger)
        self.turn_on_cmd_callback = turn_on_cmd_callback

    def _turn_on_immediately(
        self: MockPowerSwitchComponentManager,
        task_callback: Optional[Callable] = None,
        task_abort_event: Optional[Event] = None,
    ):
        self.turn_on_cmd_callback()
        task_callback(
            result=(ResultCode.OK, "TurnOnImmediately completed OK"),
            status=TaskStatus.COMPLETED,
        )
        return

    def turn_on_immediately(
        self: MockPowerSwitchComponentManager,
        task_callback: Optional[Callable] = None,
    ) -> tuple[ResultCode, str]:
        """"""
        return self.submit_task(
            self._turn_on_immediately,
            task_callback=task_callback,
        )

    def _turn_on_after_0p3_seconds(
        self: MockPowerSwitchComponentManager,
        task_callback: Optional[Callable] = None,
        task_abort_event: Optional[Event] = None,
    ):
        sleep(0.3)
        self.turn_on_cmd_callback()
        task_callback(
            result=(ResultCode.OK, "TurnOnAfter0p3Seconds completed OK"),
            status=TaskStatus.COMPLETED,
        )
        return

    def turn_on_after_0p3_seconds(
        self: MockPowerSwitchComponentManager,
        task_callback: Optional[Callable] = None,
    ) -> tuple[ResultCode, str]:
        """"""
        return self.submit_task(
            self._turn_on_after_0p3_seconds,
            task_callback=task_callback,
        )


class MockPowerSwitch(SKABaseDevice):

    POWERSWITCH_FQDN = "test/device/power_switch"

    def init_device(self: MockPowerSwitch):
        super().init_device()
        self.set_state(DevState.OFF)

    def _turn_on(self: MockPowerSwitch) -> None:
        self.set_state(DevState.ON)
        self.push_change_event("state", DevState.ON)
        self.push_archive_event("state", DevState.ON)

    def init_command_objects(self: MockPowerSwitch) -> None:
        """
        Sets up the command objects
        """
        super().init_command_objects()

        self.register_command_object(
            "TurnOnImmediately",
            SubmittedSlowCommand(
                command_name="TurnOnImmediately",
                command_tracker=self._command_tracker,
                component_manager=self.component_manager,
                method_name="turn_on_immediately",
                logger=self.logger,
            ),
        )

        self.register_command_object(
            "TurnOnAfter0p3Seconds",
            SubmittedSlowCommand(
                command_name="TurnOnAfter0p3Seconds",
                command_tracker=self._command_tracker,
                component_manager=self.component_manager,
                method_name="turn_on_after_0p3_seconds",
                logger=self.logger,
            ),
        )

    @command()
    def TurnOff(self: MockPowerSwitch):
        self.set_state(DevState.OFF)
        self.push_change_event("state", DevState.OFF)
        self.push_archive_event("state", DevState.OFF)

    @command(dtype_out="DevVarLongStringArray")
    def TurnOnImmediately(self: MockPowerSwitch) -> DevVarLongStringArrayType:
        command_handler = self.get_command_object("TurnOnImmediately")
        result_code, command_id = command_handler()
        return [[result_code], [command_id]]

    @command(dtype_out="DevVarLongStringArray")
    def TurnOnAfter0p3Seconds(
        self: MockPowerSwitch,
    ) -> DevVarLongStringArrayType:
        command_handler = self.get_command_object("TurnOnAfter0p3Seconds")
        result_code, command_id = command_handler()
        return [[result_code], [command_id]]

    def create_component_manager(
        self,
    ) -> MockPowerSwitchComponentManager:
        return MockPowerSwitchComponentManager(self._turn_on)


class TestAssertiveLoggingObserverCore:
    @classmethod
    def setup_class(cls: TestAssertiveLoggingObserver):

        cls.reporter = alo.AssertiveLoggingObserver(
            alo.AssertiveLoggingObserverMode.REPORTING, test_logger
        )

        cls.asserter = alo.AssertiveLoggingObserver(
            alo.AssertiveLoggingObserverMode.ASSERTING, test_logger
        )


class TestAssertiveLoggingObserver(TestAssertiveLoggingObserverCore):
    def test_ALO_observe_bool(self: TestAssertiveLoggingObserver):

        self.reporter.observe_true(True)
        self.reporter.observe_false(False)
        self.reporter.observe_true(False)
        self.reporter.observe_false(True)

        self.asserter.observe_true(True)
        self.asserter.observe_false(False)

        try:
            self.asserter.observe_true(False)
            fail("Reached past observe_true")
        except AssertionError as e:
            if "Reached past observe_true" in str(e):
                raise e

        try:
            self.asserter.observe_false(True)
            fail("Reached past observe_false")
        except AssertionError as e:
            if "Reached past observe_false" in str(e):
                raise e


class TestAssertiveLoggingObserverLRC(TestAssertiveLoggingObserverCore):
    @classmethod
    def setup_class(cls: TestAssertiveLoggingObserver):

        super().setup_class()

        cls.context = DeviceTestContext(
            MockPowerSwitch,
            device_name=MockPowerSwitch.POWERSWITCH_FQDN,
            process=True,
        )
        cls.proxy = cls.context.__enter__()
        cls.tracer = TangoEventTracer()
        cls.tracer.subscribe_event(
            MockPowerSwitch.POWERSWITCH_FQDN, "longRunningCommandResult"
        )
        cls.tracer.subscribe_event(MockPowerSwitch.POWERSWITCH_FQDN, "state")
        cls.asserter.set_event_tracer(cls.tracer)
        cls.reporter.set_event_tracer(cls.tracer)

    @classmethod
    def teardown_class(cls: TestAssertiveLoggingObserverLRC):
        cls.tracer.unsubscribe_all()
        cls.context.__exit__(None, None, None)

    def setup_method(self: TestAssertiveLoggingObserverLRC, method):
        self.proxy.TurnOff()
        self.tracer.clear_events()

    def test_ALO_reporter_lrc_state_change_immediate_success(
        self: TestAssertiveLoggingObserverLRC,
    ):

        cmd_result = self.proxy.TurnOnImmediately()

        self.reporter.observe_device_state_change(
            MockPowerSwitch.POWERSWITCH_FQDN,
            "state",
            DevState.ON,
            1,
        )

        self.reporter.observe_lrc_result(
            MockPowerSwitch.POWERSWITCH_FQDN,
            cmd_result,
            "TurnOnImmediately",
            1,
        )

    def test_ALO_asserter_lrc_state_change_immediate_success(
        self: TestAssertiveLoggingObserverLRC,
    ):

        cmd_result = self.proxy.TurnOnImmediately()

        self.asserter.observe_device_state_change(
            MockPowerSwitch.POWERSWITCH_FQDN,
            "state",
            DevState.ON,
            1,
        )

        self.asserter.observe_lrc_result(
            MockPowerSwitch.POWERSWITCH_FQDN,
            cmd_result,
            "TurnOnImmediately",
            1,
        )

    def test_ALO_reporter_lrc_state_change_delayed_success(
        self: TestAssertiveLoggingObserverLRC,
    ):

        cmd_result = self.proxy.TurnOnAfter0p3Seconds()

        self.reporter.observe_device_state_change(
            MockPowerSwitch.POWERSWITCH_FQDN,
            "state",
            DevState.ON,
            1,
        )

        self.reporter.observe_lrc_result(
            MockPowerSwitch.POWERSWITCH_FQDN,
            cmd_result,
            "TurnOnAfter0p3Seconds",
            1,
        )

    def test_ALO_asserter_lrc_state_change_delayed_success(
        self: TestAssertiveLoggingObserverLRC,
    ):

        cmd_result = self.proxy.TurnOnAfter0p3Seconds()

        self.asserter.observe_device_state_change(
            MockPowerSwitch.POWERSWITCH_FQDN,
            "state",
            DevState.ON,
            1,
        )

        self.asserter.observe_lrc_result(
            MockPowerSwitch.POWERSWITCH_FQDN,
            cmd_result,
            "TurnOnAfter0p3Seconds",
            1,
        )

    def test_ALO_reporter_lrc_state_change_timeout_failure(
        self: TestAssertiveLoggingObserverLRC,
    ):
        cmd_result = self.proxy.TurnOnAfter0p3Seconds()

        self.reporter.observe_device_state_change(
            MockPowerSwitch.POWERSWITCH_FQDN,
            "state",
            DevState.ON,
            0.05,
        )

        self.reporter.observe_lrc_result(
            MockPowerSwitch.POWERSWITCH_FQDN,
            cmd_result,
            "TurnOnAfter0p3Seconds",
            0.05,
        )

    def test_ALO_asserter_lrc_state_change_timeout_failure(
        self: TestAssertiveLoggingObserverLRC,
    ):
        cmd_result = self.proxy.TurnOnAfter0p3Seconds()

        try:
            self.asserter.observe_device_state_change(
                MockPowerSwitch.POWERSWITCH_FQDN,
                "state",
                DevState.ON,
                0.05,
            )
            fail("Reached past observe_device_state_change")
        except AssertionError as e:
            if "Reached past observe_device_state_change" in str(e):
                raise e

        try:
            self.asserter.observe_lrc_result(
                MockPowerSwitch.POWERSWITCH_FQDN,
                cmd_result,
                "TurnOnAfter0p3Seconds",
                0.05,
            )
            fail("Reached past observe_lrc_result")
        except AssertionError as e:
            if "Reached past observe_lrc_result" in str(e):
                raise e
