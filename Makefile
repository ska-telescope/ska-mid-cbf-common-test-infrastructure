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