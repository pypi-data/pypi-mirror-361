#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Collect AWS SSO Permission Set assignment data from multiple accounts."""

from . import helper_aws_sso
from . import helper_common
from . import helper_aws_entrypoint
from .helper_parameters import *  # NOQA
from multithreader import threads


def aws_sso_get():
    """Collect AWS SSO Permission Set assignment data."""
    # Enter AWS environment.
    aws = helper_aws_entrypoint.enter_aws()
    sso_admin = aws['session'].client(
        'sso-admin',
        region_name=region
    )
    identity_store = aws['session'].client(
        'identitystore',
        region_name=region
    )

    # Execute task with multithreading.
    items = {
        'sso_admin': sso_admin,
        'identity_store': identity_store,
        'sso_instance_arn': sso_instance_arn,
        'identity_store_id': identity_store_id
    }
    results = threads(
        helper_aws_sso.get_permission_sets,
        aws['account_ids'],
        items,
        thread_num=THREAD_NUM
    )

    # Write results to file.
    helper_common.write_json_obj(sso_get_output_file, results)


def main():
    """Execute main function."""
    aws_sso_get()


if __name__ == '__main__':
    main()
