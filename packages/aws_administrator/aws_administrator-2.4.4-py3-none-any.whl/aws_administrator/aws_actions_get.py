#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Get AWS actions for services."""

from pprint import pprint as pp
from . import helper_aws_iam
from . import helper_common
from . import helper_aws_entrypoint
from .helper_parameters import *  # NOQA


def aws_actions_get():
    """Get AWS actions for services."""
    # Enter AWS environment.
    aws = helper_aws_entrypoint.enter_aws()

    # Get actions.
    actions = helper_aws_iam.get_actions(
        aws['session'],
        actions_get_service
    )

    # Write policies to JSON file.
    helper_common.write_json_obj(actions_get_output_file, actions)

    # Filter actions by keyword.
    if actions_get_filter:
        filtered_actions = helper_aws_iam.filter_actions_keyword(
            actions,
            actions_get_filter
        )
        pp(filtered_actions)


def main():
    """Execute main function."""
    aws_actions_get()


if __name__ == '__main__':
    main()
