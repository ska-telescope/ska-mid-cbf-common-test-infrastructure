"""
This module contains a mock tango device for testing LRCs in the
AssertiveLoggingObserver service.

Warning: There was some technical difficulty encountered (seg fault issues)
with using the same device in multiple tango.test_context.DeviceTestContext
instances sequentially, so it may be more difficult than appears to reuse this
device in other contexts.
"""

from __future__ import annotations

import logging
from threading import Event
from time import sleep
from typing import Callable, Optional

from ska_control_model import TaskStatus
from ska_tango_base.base.base_device import (
    DevVarLongStringArrayType,
    SKABaseDevice,
)
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tango_base.executor.executor_component_manager import (
    TaskExecutorComponentManager,
)
from tango import DevState
from tango.server import command

from ska_mid_cbf_common_test_infrastructure.test_logging.format import (
    LOG_FORMAT,
)

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
tango_logger = logging.getLogger(__name__)


class MockTangoDeviceComponentManager(TaskExecutorComponentManager):
    """
    Mock component manager for MockTangoDevice.
    """

    def __init__(self, turn_on_cmd_callback):
        super().__init__(tango_logger)
        self.turn_on_cmd_callback = turn_on_cmd_callback

    def _turn_on_immediately(
        self: MockTangoDeviceComponentManager,
        task_callback: Optional[Callable] = None,
        task_abort_event: Optional[Event] = None,
    ):
        """Task execution that turns mock device on immediately."""
        self.turn_on_cmd_callback()
        task_callback(
            result=(ResultCode.OK, "TurnOnImmediately completed OK"),
            status=TaskStatus.COMPLETED,
        )
        return

    def turn_on_immediately(
        self: MockTangoDeviceComponentManager,
        task_callback: Optional[Callable] = None,
    ) -> tuple[ResultCode, str]:
        """
        Component manager command that turns mock device on immediately.
        """
        return self.submit_task(
            self._turn_on_immediately,
            task_callback=task_callback,
        )

    def _turn_on_after_0p3_seconds(
        self: MockTangoDeviceComponentManager,
        task_callback: Optional[Callable] = None,
        task_abort_event: Optional[Event] = None,
    ):
        """Task execution that turns mock device on after 0.3s."""
        sleep(0.3)
        self.turn_on_cmd_callback()
        task_callback(
            result=(ResultCode.OK, "TurnOnAfter0p3Seconds completed OK"),
            status=TaskStatus.COMPLETED,
        )
        return

    def turn_on_after_0p3_seconds(
        self: MockTangoDeviceComponentManager,
        task_callback: Optional[Callable] = None,
    ) -> tuple[ResultCode, str]:
        """
        Component manager command that turns mock device on after 0.3s.
        """
        return self.submit_task(
            self._turn_on_after_0p3_seconds,
            task_callback=task_callback,
        )


class MockTangoDevice(SKABaseDevice):
    """
    Mock power switch device for testing LRCs in AssertiveLoggingObserver.
    """

    POWERSWITCH_FQDN = "test/device/power_switch"

    def init_device(self: MockTangoDevice):
        """
        Sets initial state to OFF.
        """
        super().init_device()
        self.set_state(DevState.OFF)

    def _turn_on(self: MockTangoDevice) -> None:
        """
        Callback function to set state to ON.
        """
        self.set_state(DevState.ON)
        self.push_change_event("state", DevState.ON)
        self.push_archive_event("state", DevState.ON)

    def init_command_objects(self: MockTangoDevice) -> None:
        """
        Sets up the command objects.
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
    def TurnOff(self: MockTangoDevice):
        """Command to turn off immediately."""
        self.set_state(DevState.OFF)
        self.push_change_event("state", DevState.OFF)
        self.push_archive_event("state", DevState.OFF)

    @command(dtype_out="DevVarLongStringArray")
    def TurnOnImmediately(self: MockTangoDevice) -> DevVarLongStringArrayType:
        """Command to turn on immediately."""
        command_handler = self.get_command_object("TurnOnImmediately")
        result_code, command_id = command_handler()
        return [[result_code], [command_id]]

    @command(dtype_out="DevVarLongStringArray")
    def TurnOnAfter0p3Seconds(
        self: MockTangoDevice,
    ) -> DevVarLongStringArrayType:
        """Command to turn on after a delay of 0.3s."""
        command_handler = self.get_command_object("TurnOnAfter0p3Seconds")
        result_code, command_id = command_handler()
        return [[result_code], [command_id]]

    def create_component_manager(
        self,
    ) -> MockTangoDeviceComponentManager:
        return MockTangoDeviceComponentManager(self._turn_on)
