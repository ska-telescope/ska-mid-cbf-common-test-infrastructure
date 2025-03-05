from __future__ import annotations

import logging

from assertpy import fail
from mock_power_switch import MockPowerSwitch
from ska_tango_testing.integration import TangoEventTracer
from tango import DevState
from tango.test_context import DeviceTestContext

from assertive_logging_observer.assertive_logging_observer import (
    AssertiveLoggingObserver,
    AssertiveLoggingObserverMode,
)
from test_logging.format import LOG_FORMAT

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
test_logger = logging.getLogger(__name__)


class TestAssertiveLoggingObserverCore:
    @classmethod
    def setup_class(cls: TestAssertiveLoggingObserver):

        cls.reporter = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.REPORTING, test_logger
        )

        cls.asserter = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.ASSERTING, test_logger
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
