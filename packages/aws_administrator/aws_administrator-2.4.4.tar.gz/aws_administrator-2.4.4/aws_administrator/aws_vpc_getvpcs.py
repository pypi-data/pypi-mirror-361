#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""List VPCs in AWS accounts."""

from . import helper_aws_ec2
from . import helper_common
from . import helper_aws_entrypoint
from .helper_parameters import *  # NOQA
from multithreader import threads


def aws_vpc_getvpcs():
    """Get VPCs."""
    # Enter AWS environment.
    aws = helper_aws_entrypoint.enter_aws()

    # Create items for multithreading.
    items = {
        'session': aws['session'],
        'assumed_role_name': assumed_role_name,
        'external_id': external_id,
        'region': region
    }

    # Execute task with multithreading.
    vpcs = threads(
        helper_aws_ec2.get_vpcs,
        aws['account_ids'],
        items,
        thread_num=THREAD_NUM
    )

    # Write the list to JSON file.
    helper_common.write_json_obj(vpc_getvpcs_output_file, vpcs)


def main():
    """Execute main function."""
    aws_vpc_getvpcs()


if __name__ == '__main__':
    main()
