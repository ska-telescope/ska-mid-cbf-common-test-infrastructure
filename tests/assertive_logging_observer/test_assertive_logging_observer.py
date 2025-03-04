import logging

import assertive_logging_observer.assertive_logging_observer as alo
from test_logging.format import LOG_FORMAT

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
_logger = logging.getLogger(__name__)


class TestAssertiveLoggingObserver:
    @classmethod
    def setup_class(cls):

        cls.reporter = alo.AssertiveLoggingObserver(
            alo.AssertiveLoggingObserverMode.REPORTING, _logger
        )

        cls.asserter = alo.AssertiveLoggingObserver(
            alo.AssertiveLoggingObserverMode.ASSERTING, _logger
        )

    def test_ALO_observe_bool(self):

        self.reporter.observe_true(True)
        self.reporter.observe_false(False)
        self.reporter.observe_true(False)
        self.reporter.observe_false(True)

        self.asserter.observe_true(True)
        self.asserter.observe_false(False)

        try:
            self.asserter.observe_true(False)
            assert False, "Did not assert correctly"
        except AssertionError as e:
            print(e)

        try:
            self.asserter.observe_false(True)
            assert False, "Did not assert correctly"
        except AssertionError as e:
            print(e)
