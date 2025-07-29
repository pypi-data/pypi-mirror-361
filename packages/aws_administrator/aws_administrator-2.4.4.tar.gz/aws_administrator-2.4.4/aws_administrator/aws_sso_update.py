#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Update AWS SSO User and Group names from mappings files."""

from pprint import pprint as pp
from . import helper_aws_sso
from . import helper_common
from . import helper_aws_entrypoint
from .helper_parameters import *  # NOQA
from multithreader import threads


def aws_sso_update():
    """Update AWS SSO User and Group names from mappings files."""
    # Enter AWS environment.
    aws = helper_aws_entrypoint.enter_aws()
    identity_store = aws['session'].client(
        'identitystore',
        region_name=region
    )

    # Prepare items for multithreading.
    items = {
        'identity_store': identity_store,
        'identity_store_id': identity_store_id,
        'DRY_RUN': DRY_RUN
    }

    # Read User CSV file and execute updates with multithreading.
    if (
        sso_update_user_map_file
        and sso_update_old_user_heading
        and sso_update_new_user_heading
    ):
        user_data = helper_common.read_csv(sso_update_user_map_file)
        user_dicts = [
            {
                'old_user_name': row[sso_update_old_user_heading],
                'new_user_name': row[sso_update_new_user_heading]
            } for row in user_data
        ]
        user_updates = threads(
            helper_aws_sso.update_user_name,
            user_dicts,
            items,
            thread_num=THREAD_NUM
        )
        pp(user_updates)

    # Read Group CSV file and execute updates with multithreading.
    if (
        sso_update_group_map_file
        and sso_update_old_group_heading
        and sso_update_new_group_heading
    ):
        group_data = helper_common.read_csv(sso_update_group_map_file)
        group_dicts = [
            {
                'old_group_name': row[sso_update_old_group_heading],
                'new_group_name': row[sso_update_new_group_heading]
            } for row in group_data
        ]
        group_updates = threads(
            helper_aws_sso.update_group_name,
            group_dicts,
            items,
            thread_num=THREAD_NUM
        )
        pp(group_updates)


def main():
    """Execute main function."""
    aws_sso_update()


if __name__ == '__main__':
    main()
