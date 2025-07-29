#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""
List S3 buckets in AWS accounts.

The bucket name prefix and region can be provided to tind specific buckets.
"""

from . import helper_aws_s3
from . import helper_common
from . import helper_aws_entrypoint
from .helper_parameters import *  # NOQA
from multithreader import threads


def aws_s3_getbuckets():
    """Get S3 buckets."""
    # Enter AWS environment.
    aws = helper_aws_entrypoint.enter_aws()

    # Create items for multithreading.
    items = {
        'session': aws['session'],
        'assumed_role_name': assumed_role_name,
        'external_id': external_id,
        's3_getbuckets_prefix': s3_getbuckets_prefix,
        'region': region
    }

    # Execute task with multithreading.
    buckets = threads(
        helper_aws_s3.get_buckets,
        aws['account_ids'],
        items,
        thread_num=THREAD_NUM
    )

    # Write the list to JSON file.
    helper_common.write_json_obj(s3_getbuckets_output_file, buckets)


def main():
    """Execute main function."""
    aws_s3_getbuckets()


if __name__ == '__main__':
    main()
