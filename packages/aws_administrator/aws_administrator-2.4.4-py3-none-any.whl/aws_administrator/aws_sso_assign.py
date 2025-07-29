#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Assign AWS SSO Permission Sets to multiple accounts."""

from pprint import pprint as pp
from . import helper_aws_sso
from . import helper_common
from . import helper_aws_entrypoint
from .helper_parameters import *  # NOQA
from multithreader import threads


def aws_sso_assign():
    """Assign AWS SSO Permission Sets."""
    # Enter AWS environment.
    aws = helper_aws_entrypoint.enter_aws()
    sso_admin = aws['session'].client(
        'sso-admin',
        region_name=region
    )

    # Create accounts list from JSON file.
    data = helper_common.read_json(sso_assign_input_file)
    account_ids = [account['account_id'] for account in data]

    # Execute task with multithreading.
    items = {
        'sso_admin': sso_admin,
        'sso_instance_arn': sso_instance_arn,
        'data': data
    }
    results = threads(
        helper_aws_sso.assign_permission_sets_dry_run,
        account_ids,
        items,
        thread_num=THREAD_NUM
    ) if DRY_RUN else threads(
        helper_aws_sso.assign_permission_sets,
        account_ids,
        items,
        thread_num=THREAD_NUM
    )

    # Print results.
    pp(results)


def main():
    """Execute main function."""
    aws_sso_assign()


if __name__ == '__main__':
    main()
