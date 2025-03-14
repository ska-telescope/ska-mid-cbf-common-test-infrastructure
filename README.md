# SKA Mid.CBF Common Test Infrastructure

This internal code repository contains common code for ska-mid-cbf-system-tests, ska-mid-cbf-fhs-system-tests, and ska-mid-cbf-int-tests.

Code repository: [here](https://gitlab.com/ska-telescope/ska-mid-cbf-common-test-infrastructure)

ReadtheDocs: [here](https://developer.skao.int/projects/ska-mid-cbf-common-test-infrastructure/en/latest/)

## Services

ska-mid-cbf-common-test-infrastructure contains multiple services for usage in test repositories with service source code located in the **src/ska-mid-cbf-common-test-infrastructure** directory and service unit testing located in the **tests** directory.

### List of Current Services
- assertive_logging_observer
- test_logging
- template_service

### Adding a New Service
1. start by duplicating the template_service structure in **src/ska-mid-cbf-common-test-infrastructure** and in **tests** and renaming directories according to new service name service_name
2. for TDD progression write tests for service in service_name in **tests** (discovery occurs by normal pytest rules)
3. implement source code in service_name in **src/ska-mid-cbf-common-test-infrastructure/service_name** to pass tests
5. go to **docs/src** and perform the following:
    - use sphinx-apidoc to generate module documentation in output dir service_name modifying the files as necessary to generate desired doc structure
    - delete the modules.rst file unless using it
    - in service_name.rst modify do document API as necessary (note: automodule will include all classes imported into your service's \_\_init\_\_.py if you add :import-members:, otherwise use ..autoclass:: with explicity python import paths to names to import classes one by one, more ways to use this file and included in sphinx documentation [here](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/build-the-docs.html#generating-documentation-from-docstrings))
    - link path to service_name.rst in new section in **docs/src/index.rst**
6. add service to "List of Current Services" in this README