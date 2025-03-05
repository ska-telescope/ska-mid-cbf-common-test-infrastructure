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

from test_logging.format import LOG_FORMAT

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
tango_logger = logging.getLogger(__name__)


class MockPowerSwitchComponentManager(TaskExecutorComponentManager):
    def __init__(self, turn_on_cmd_callback):
        super().__init__(tango_logger)
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
