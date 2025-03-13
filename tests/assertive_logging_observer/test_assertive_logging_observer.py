"""
Note: ALO unit testing does not directly test log message content due to
potential brittleness w.r.t message changes and testing against logs, testing
philosophy is only testing that ALO is asserting properly.
"""

from __future__ import annotations

import logging

from assertpy import assert_that, fail
from mock_tango_device import MockTangoDevice
from tango import DevState
from tango.test_context import DeviceTestContext

from assertive_logging_observer import (
    AssertiveLoggingObserver,
    AssertiveLoggingObserverMode,
)
from test_logging.format import LOG_FORMAT

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
test_logger = logging.getLogger(__name__)


class TestAssertiveLoggingObserverBasic:
    """
    Test basic reporting/assertions for AssertiveLoggingObserver.
    """

    @classmethod
    def setup_class(cls: TestAssertiveLoggingObserverBasic):
        """
        Create a reporter and an asserter version of AssertiveLoggingObserver
        to test with, with use_event_tracer False.
        """
        cls.reporter = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.REPORTING,
            test_logger,
            use_event_tracer=False,
        )

        cls.asserter = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.ASSERTING,
            test_logger,
            use_event_tracer=False,
        )

    def test_ALO_reporter_observe_bool(
        self: TestAssertiveLoggingObserverBasic,
    ):
        """
        Test reporter behavior for observe_true and observe_false:
        - log bool value stating PASS when correctly matching bool to called
          observe_bool and FAIL otherwise.
        """
        self.reporter.observe_true(True)
        self.reporter.observe_false(False)
        self.reporter.observe_true(False)
        self.reporter.observe_false(True)

    def test_ALO_asserter_observe_bool(
        self: TestAssertiveLoggingObserverBasic,
    ):
        """
        Test reporter behavior for observe_true and observe_false:
        - log bool value stating PASS when correctly matching bool to called
          observe_bool and FAIL otherwise.
        - raise AssertionError in FAIL situations.
        """
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

    def test_ALO_reporter_observe_equality(
        self: TestAssertiveLoggingObserverBasic,
    ):
        """
        Test reporter behavior for observe_equality:
        - log values stating PASS and equal if equal, and FAIL and not equal
          otherwise.
        """
        self.reporter.observe_equality(1, 1)
        self.reporter.observe_equality("skao", "skao")
        self.reporter.observe_equality(2, 1)
        self.reporter.observe_equality("s", "skao")

    def test_ALO_asserter_observe_equality(
        self: TestAssertiveLoggingObserverBasic,
    ):
        """
        Test asserter behavior for observe_equality:
        - log values stating PASS and equal if equal, and FAIL and not equal
          otherwise.
        - raise AssertionError in FAIL situations.
        """
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


class TestAssertiveLoggingObserverLRC:
    """
    Test LRC reporting/assertions for AssertiveLoggingObserver.
    """

    @classmethod
    def setup_class(cls: TestAssertiveLoggingObserverLRC):
        """
        Set-up DeviceTestContext of MockTangoDevice for testing and create a
        reporter and an asserter version of AssertiveLoggingObserver to test
        with, subscribed to necessary test events and attributes.
        """
        cls.context = DeviceTestContext(
            MockTangoDevice,
            device_name=MockTangoDevice.POWERSWITCH_FQDN,
            process=True,
        )
        cls.proxy = cls.context.__enter__()

        cls.reporter = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.REPORTING, test_logger
        )

        cls.asserter = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.ASSERTING, test_logger
        )

        cls.reporter.subscribe_event_tracer(
            MockTangoDevice.POWERSWITCH_FQDN, "longRunningCommandResult"
        )
        cls.reporter.subscribe_event_tracer(
            MockTangoDevice.POWERSWITCH_FQDN, "state"
        )

        cls.asserter.subscribe_event_tracer(
            MockTangoDevice.POWERSWITCH_FQDN, "longRunningCommandResult"
        )
        cls.asserter.subscribe_event_tracer(
            MockTangoDevice.POWERSWITCH_FQDN, "state"
        )

    @classmethod
    def teardown_class(cls: TestAssertiveLoggingObserverLRC):
        """
        Teardown DeviceTestContext of MockTangoDevice for testing and also
        unsubscribing TangoEventTracer.
        """
        cls.reporter.reset_event_tracer()
        cls.asserter.reset_event_tracer()
        cls.context.__exit__(None, None, None)

    def setup_method(self: TestAssertiveLoggingObserverLRC, method):
        """
        Reset MockTangoDevice, clear events between every test, and ensure
        tracers are correctly set.
        """
        self.proxy.TurnOff()
        self.reporter.clear_events()
        self.asserter.clear_events()

    def test_ALO_reporter_lrc_state_change_immediate_success(
        self: TestAssertiveLoggingObserverLRC,
    ):
        """
        Test reporter logs PASS on immediately successful LRC and state change.
        """
        cmd_result = self.proxy.TurnOnImmediately()

        self.reporter.observe_device_attr_change(
            MockTangoDevice.POWERSWITCH_FQDN,
            "state",
            DevState.ON,
            1,
        )

        self.reporter.observe_lrc_ok(
            MockTangoDevice.POWERSWITCH_FQDN,
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

        self.asserter.observe_device_attr_change(
            MockTangoDevice.POWERSWITCH_FQDN,
            "state",
            DevState.ON,
            1,
        )

        self.asserter.observe_lrc_ok(
            MockTangoDevice.POWERSWITCH_FQDN,
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

        self.reporter.observe_device_attr_change(
            MockTangoDevice.POWERSWITCH_FQDN,
            "state",
            DevState.ON,
            1,
        )

        self.reporter.observe_lrc_ok(
            MockTangoDevice.POWERSWITCH_FQDN,
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

        self.asserter.observe_device_attr_change(
            MockTangoDevice.POWERSWITCH_FQDN,
            "state",
            DevState.ON,
            1,
        )

        self.asserter.observe_lrc_ok(
            MockTangoDevice.POWERSWITCH_FQDN,
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

        self.reporter.observe_device_attr_change(
            MockTangoDevice.POWERSWITCH_FQDN,
            "state",
            DevState.ON,
            0.05,
        )

        self.reporter.observe_lrc_ok(
            MockTangoDevice.POWERSWITCH_FQDN,
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
            self.asserter.observe_device_attr_change(
                MockTangoDevice.POWERSWITCH_FQDN,
                "state",
                DevState.ON,
                0.05,
            )
            fail("Reached past observe_device_attr_change")
        except AssertionError as exception:
            if "Reached past observe_device_attr_change" in str(exception):
                raise exception

        try:
            self.asserter.observe_lrc_ok(
                MockTangoDevice.POWERSWITCH_FQDN,
                cmd_result,
                "TurnOnAfter0p3Seconds",
                0.05,
            )
            fail("Reached past observe_lrc_ok")
        except AssertionError as exception:
            if "Reached past observe_lrc_ok" in str(exception):
                raise exception

    def test_ALO_destructor(
        self: TestAssertiveLoggingObserverLRC
    ):
        """
        Test that destructor successfully unsubscribes associated event_tracer.
        """
        to_destroy = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.REPORTING,
            test_logger
        )
        to_destroy.subscribe_event_tracer(
            MockTangoDevice.POWERSWITCH_FQDN, "state"
        )
        event_tracer_keep = to_destroy.event_tracer

        # Explicitly call destroyer
        del to_destroy

        self.proxy.TurnOnImmediately()

        try:
            assert_that(event_tracer_keep).within_timeout(
                1
            ).has_change_event_occurred(
                device_name=MockTangoDevice.POWERSWITCH_FQDN,
                attribute_name="state",
                attribute_value=DevState.ON,
            )
            fail("Reached past assert_that")

        except AssertionError as assertion_err:
            if "Reached past assert_that" in str(assertion_err):
                raise assertion_err

    def test_ALO_lrc_fail_if_no_event_tracer(
        self: TestAssertiveLoggingObserverLRC,
    ):
        """
        Test that AssertiveLoggingObserver correctly throws RuntimeError
        in both modes if event_tracer if missing for
        observe_device_attr_change and observe_lrc_ok.
        """
        test_reporter = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.REPORTING,
            test_logger,
            use_event_tracer=False,
        )

        test_asserter = AssertiveLoggingObserver(
            AssertiveLoggingObserverMode.ASSERTING,
            test_logger,
            use_event_tracer=False,
        )

        cmd_result = self.proxy.TurnOnImmediately()

        try:
            test_reporter.observe_device_attr_change(
                MockTangoDevice.POWERSWITCH_FQDN,
                "state",
                DevState.ON,
                1,
            )
            fail("Reached past observe_device_attr_change")
        except RuntimeError:
            pass

        try:
            test_reporter.observe_lrc_ok(
                MockTangoDevice.POWERSWITCH_FQDN,
                cmd_result,
                "TurnOnImmediately",
                1,
            )
            fail("Reached past observe_lrc_ok")
        except RuntimeError:
            pass

        try:
            test_asserter.observe_device_attr_change(
                MockTangoDevice.POWERSWITCH_FQDN,
                "state",
                DevState.ON,
                1,
            )
            fail("Reached past observe_device_attr_change")
        except RuntimeError:
            pass

        try:
            test_asserter.observe_lrc_ok(
                MockTangoDevice.POWERSWITCH_FQDN,
                cmd_result,
                "TurnOnImmediately",
                1,
            )
            fail("Reached past observe_lrc_ok")
        except RuntimeError:
            pass
