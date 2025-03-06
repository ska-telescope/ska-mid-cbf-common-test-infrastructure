The assertive_logging_observer service provides a single object observer class
AssertiveLoggingObserver which can be set in
AssertiveLoggingObserverMode.REPORTING mode or
AssertiveLoggingObserverMode.ASSERTING mode, and respectively either logs
observations the observer makes of given values or logs and asserts on the
given values in line moreso with a test. This service is meant to be used in
test functionality for I&T test repositories so that functionality can be
flexible to have fatal assertions for test code but be non-fatal for
shared prototyping usage of code.

API documentation is available in generated docs file.