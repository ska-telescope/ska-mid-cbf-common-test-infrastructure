PROJECT = ska-mid-cbf-common-test-infrastructure

# include core make support
include .make/base.mk

# include raw support
include .make/raw.mk

# include OCI Images support
include .make/oci.mk

# include k8s support
include .make/k8s.mk

# Include Python support
include .make/python.mk

python-fix-isort:
	$(PYTHON_RUNNER) isort --profile black --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_ISORT) $(PYTHON_LINT_TARGET)

python-fix-black:
	$(PYTHON_RUNNER) black --exclude .+\.ipynb --line-length $(PYTHON_LINE_LENGTH) $(PYTHON_SWITCHES_FOR_BLACK) $(PYTHON_LINT_TARGET)