#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Provide common AWS EC2 multithreaded functions."""

from . import helper_common
from . import helper_aws_entrypoint


def get_sgs(
    account_id: str,
    items: dict
) -> dict:
    """Get AWS Security Group details from an AWS account."""
    print(f'Working on {account_id}...')

    try:
        # Get auth credentials for each account.
        client = helper_aws_entrypoint.account_client_auth(
            account_id,
            items,
            'ec2'
        )

        # Get all Security Group details in the specified region.
        paginator = client.get_paginator('describe_security_groups')
        response_iterator = paginator.paginate()

        # Read through pages of Security Group details.
        sg_list = []
        for page in response_iterator:
            for sg in page['SecurityGroups']:
                sg_list.append(sg)

        # Process details.
        if sg_list == []:
            number_of_sgs = 0
            sgs = None
        else:
            number_of_sgs = len(sg_list)
            sgs = [sg['GroupId'] for sg in sg_list]

    # In case of any exceptions, return the error message but allow loop to continue.
    except Exception as e:
        number_of_sgs = 0
        sgs = [str(e)]

    return {
        'account_id': account_id,
        'number_of_sgs': number_of_sgs,
        'details': sgs
    }


def get_vpcs(
    account_id: str,
    items: dict
) -> dict:
    """Get VPC details in an AWS account."""
    print(f'Working on {account_id}...')

    try:
        # Get auth credentials for each account.
        client = helper_aws_entrypoint.account_client_auth(
            account_id,
            items,
            'ec2'
        )

        # Use a paginator to handle multiple pages of results.
        paginator = client.get_paginator('describe_vpcs')
        response_iterator = paginator.paginate()

        # Collect VPC information.
        vpcs = []
        for page in response_iterator:
            for vpc in page.get('Vpcs', []):
                vpc_tags = vpc.get('Tags', [])
                vpc_name = helper_common.get_value_from_tag(vpc_tags, 'Name')
                vpc_cidrs = vpc.get('CidrBlockAssociationSet', [])
                cidrs = [
                    {
                        'block': vpc_cidr.get('CidrBlock'),
                        'state': vpc_cidr.get('CidrBlockState', {}).get('State')
                    }
                    for vpc_cidr in vpc_cidrs
                ]
                vpc_info = {
                    'vpc_id': vpc.get('VpcId'),
                    'vpc_name': vpc_name,
                    'cidrs': cidrs,
                    'is_default': vpc.get('IsDefault', False)
                }
                vpcs.append(vpc_info)

    except Exception as e:
        vpcs = [
            {
                'error': str(e)
            }
        ]

    return {
        'account_id': f"'{account_id}",
        'vpcs': vpcs
    }


def main():
    """Execute main function."""
    pass


if __name__ == '__main__':
    main()
