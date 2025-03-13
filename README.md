# SKA Mid.CBF Common Test Infrastructure

This internal code repository contains common code for ska-mid-cbf-system-tests, ska-mid-cbf-fhs-system-tests, and ska-mid-cbf-int-tests.

Code repository: [here](https://gitlab.com/ska-telescope/ska-mid-cbf-common-test-infrastructure)

ReadtheDocs: [here](https://developer.skao.int/projects/ska-mid-cbf-common-test-infrastructure/en/latest/)

## Services

ska-mid-cbf-common-test-infrastructure contains multiple services for usage in test repositories with service source code located in the **src** directory and service unit testing located in the **tests** directory.

### List of Current Services
- assertive_logging_observer
- template_service

### Adding a New Service
1. start by duplicating the template_service structure in **src** and in **tests** and renaming directories according to new service name service_name
2. add service_name to packages in pyproject.toml
3. for TDD progression write tests for service in service_name in **tests** (discovery occurs by normal pytest rules)
4. implement source code in service_name in **src** to pass tests
5. go to **docs/src** and perform the following:
    - use sphinx-apidoc to generate module documentation in output dir service_name modifying the files as necessary to generate desired doc structure
    - soft link to README in service_name and add with toctree to service_name.rst
    - link path to service_name.rst in new section in **docs/src/index.rst**
6. add service to "List of Current Services" in this README