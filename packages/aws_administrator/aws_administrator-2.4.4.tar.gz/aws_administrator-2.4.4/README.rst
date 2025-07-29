=====================
**aws_administrator**
=====================

Overview
--------

Run AWS administrative scripts.

Available scripts (see each script's docstring for more information):

- aws_actions_get - Get AWS actions for services.
- aws_sgs_get - Collect AWS Security Group details from multiple accounts.
- aws_sso_assign - Assign AWS SSO Permission Sets to multiple accounts.
- aws_sso_get - Collect AWS SSO Permission Set assignment data from multiple accounts.
- aws_sso_json - Convert human-readable SSO data to AWS IDs.
- aws_sso_mappings - Update AWS SSO mappings data with new principals.
- aws_sso_memberships - Get AWS SSO membership details from mappings data.
- aws_sso_update - Update AWS SSO User and Group names from mappings files.
- aws_s3_getbuckets - List S3 buckets in AWS accounts.
- aws_vpc_getvpcs - Collect AWS VPC details from multiple accounts.

Helper modules:

- helper_aws_iam - Provide common AWS IAM multithreaded functions.
- helper_aws_ec2 - Provide common AWS EC2 multithreaded functions.
- helper_aws_sso - Provide common AWS SSO multithreaded functions.
- helper_aws_s3 - Provide common AWS S3 multithreaded functions.
- helper_aws_entrypoint - Provide AWS auth and crawler options.
- helper_common - Provide common helper functions.
- helper_parameters - Provide helper parameter values.

Usage
------

Installation:

.. code-block:: BASH

    pip3 install aws_administrator
    # or
    python3 -m pip install aws_administrator

Prerequisite steps:

1. Copy the "parameters.ini" file: https://gitlab.com/fer1035_python/modules/pypi-aws_administrator/-/blob/main/src/aws_administrator/extras/parameters.ini to your current working directory.

2. Update the file with the necessary values. To specify a value for a parameter, add the value in the following format: PARAMETER_NAME **= VALUE**. The examples for this is available for the DRY_RUN and THREAD_NUM parameters.

Example (Python shell):

.. code-block:: PYTHON

    # Get AWS SSO Permission Set details from all accounts in an organization.

    from aws_administrator import aws_sso_get
    aws_sso_get.aws_sso_get()

Extra Features
---------------

- Some scripts have a DRY_RUN option which can be set in the "parameters.ini" file.
- The number of threads (THREAD_NUM) for multithreaded scripts can be set in the "parameters.ini" file.
