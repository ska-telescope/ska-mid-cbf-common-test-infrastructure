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
    """
    Core Test class for AssertiveLoggingObserver.
    """

    @classmethod
    def setup_class(cls: TestAssertiveLoggingObserverCore):
        """
        Create a reporter and an asserter version of AssertiveLoggingObserver
        to test with.
        """
        cls.reporter = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.REPORTING, test_logger
        )

        cls.asserter = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.ASSERTING, test_logger
        )


class TestAssertiveLoggingObserverBasic(TestAssertiveLoggingObserverCore):
    """
    Test basic reporting/assertions for AssertiveLoggingObserver.
    """

    def test_ALO_observe_bool(self: TestAssertiveLoggingObserverBasic):
        """
        Test reporter and asserter for correct behavior when observing bools.

        reporter behaviour:
        - log bool value stating PASS when correctly matching bool to called
          observe_bool and FAIL with a WARNING log otherwise.

        asserter behaviour:
        - log bool value stating PASS when correctly matching bool to called
          observe_bool and FAIL with an ERROR log otherwise.
        - raise AssertionError in FAIL situations.
        """
        self.reporter.observe_true(True)
        self.reporter.observe_false(False)
        self.reporter.observe_true(False)
        self.reporter.observe_false(True)

        self.asserter.observe_true(True)
        self.asserter.observe_false(False)

        try:
            self.asserter.observe_true(False)
            fail("Reached past observe_true")
        except AssertionError as exception:
            if "Reached past observe_true" in str(exception):
                raise exception

        try:
            self.asserter.observe_false(True)
            fail("Reached past observe_false")
        except AssertionError as exception:
            if "Reached past observe_false" in str(exception):
                raise exception

    def test_ALO_observe_equality(self: TestAssertiveLoggingObserverBasic):
        """
        Test reporter and asserter for correct behavior when checking
        equality of values.

        reporter behaviour:
        - log values stating PASS and equal if equal, and FAIL and not equal
          otherwise.

        asserter behaviour:
        - log values stating PASS and equal if equal, and FAIL and not equal
          otherwise.
        - raise AssertionError in FAIL situations.
        """
        self.reporter.observe_equality(1, 1)
        self.reporter.observe_equality("skao", "skao")
        self.reporter.observe_equality(2, 1)
        self.reporter.observe_equality("s", "skao")

        self.asserter.observe_equality(1, 1)
        self.asserter.observe_equality("skao", "skao")

        try:
            self.asserter.observe_equality(2, 1)
            fail("Reached past observe_equality")
        except AssertionError as exception:
            if "Reached past observe_equality" in str(exception):
                raise exception

        try:
            self.asserter.observe_equality("s", "skao")
            fail("Reached past observe_equality")
        except AssertionError as exception:
            if "Reached past observe_equality" in str(exception):
                raise exception


class TestAssertiveLoggingObserverLRC(TestAssertiveLoggingObserverCore):
    """
    Test LRC reporting/assertions for AssertiveLoggingObserver.
    """

    @classmethod
    def setup_class(cls: TestAssertiveLoggingObserverLRC):
        """
        Set-up DeviceTestContext of MockPowerSwitch for testing and set-up
        TangoEventTracer linking it to both the reporter and the asserter.
        """
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
        """
        Teardown DeviceTestContext of MockPowerSwitch for testing and also
        unsubscribing TangoEventTracer.
        """
        cls.tracer.unsubscribe_all()
        cls.context.__exit__(None, None, None)

    def setup_method(self: TestAssertiveLoggingObserverLRC, method):
        """
        Reset MockPowerSwitch and clear events between every test.
        """
        self.proxy.TurnOff()
        self.tracer.clear_events()

    def test_ALO_reporter_lrc_state_change_immediate_success(
        self: TestAssertiveLoggingObserverLRC,
    ):
        """
        Test reporter logs PASS on immediately successful LRC and state change.
        """
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
        """
        Test asserter logs PASS on immediately successful LRC and state change.
        """
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
        """
        Test reporter logs PASS on delayed successful LRC and state change.
        """
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
        """
        Test asserter logs PASS on delayed successful LRC and state change.
        """
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
        """
        Test reporter logs FAIL on unsuccessful time out on both LRC and
        state change.
        """
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
        """
        Test asserter logs FAIL on unsuccessful time out on both LRC and
        state change and throws an AssertionError for both.
        """
        cmd_result = self.proxy.TurnOnAfter0p3Seconds()

        try:
            self.asserter.observe_device_state_change(
                MockPowerSwitch.POWERSWITCH_FQDN,
                "state",
                DevState.ON,
                0.05,
            )
            fail("Reached past observe_device_state_change")
        except AssertionError as exception:
            if "Reached past observe_device_state_change" in str(exception):
                raise exception

        try:
            self.asserter.observe_lrc_result(
                MockPowerSwitch.POWERSWITCH_FQDN,
                cmd_result,
                "TurnOnAfter0p3Seconds",
                0.05,
            )
            fail("Reached past observe_lrc_result")
        except AssertionError as exception:
            if "Reached past observe_lrc_result" in str(exception):
                raise exception
