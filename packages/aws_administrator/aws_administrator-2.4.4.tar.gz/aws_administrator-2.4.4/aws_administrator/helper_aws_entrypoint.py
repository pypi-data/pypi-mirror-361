#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Provide AWS auth and crawler options."""

from .helper_parameters import *  # NOQA
import boto3
import aws_crawler
from aws_authenticator import AWSAuthenticator as awsauth


def auth(
    auth_method: str,
    profile_name: str,
    access_key_id: str,
    secret_access_key: str,
    sso_url: str,
    sso_role_name: str,
    sso_account_id: str
):
    """Login to AWS."""
    if auth_method == 'profile':
        auth = awsauth(
            profile_name=profile_name
        )
        session = auth.profile()
    elif auth_method == 'iam':
        auth = awsauth(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key
        )
        session = auth.iam()
    elif auth_method == 'sso':
        auth = awsauth(
            sso_url=sso_url,
            sso_role_name=sso_role_name,
            sso_account_id=sso_account_id
        )
        session = auth.sso()
    else:
        raise ValueError('auth_method is not defined.')
    return session


def crawler(
    session,
    accounts_list_src: str,
    accounts: str,
    ou: str,
    statuses: str
) -> list:
    """Create AWS account list."""
    if accounts_list_src == 'accounts':
        account_ids = aws_crawler.create_account_list(
            accounts
        )
    elif accounts_list_src == 'ou':
        account_ids = aws_crawler.list_ou_accounts(
            session,
            ou
        )
    elif accounts_list_src == 'statuses':
        account_ids = aws_crawler.list_accounts(
            session,
            statuses
        )
    else:
        raise ValueError('accounts_list_src is not defined.')
    return account_ids


def enter_aws() -> dict:
    """Enter AWS environment."""
    session = auth(
        auth_method=auth_method,
        profile_name=profile_name,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        sso_url=sso_url,
        sso_role_name=sso_role_name,
        sso_account_id=sso_account_id
    )
    account_ids = crawler(
        session,
        accounts_list_src,
        accounts,
        ou,
        statuses
    )
    return {
        'session': session,
        'account_ids': account_ids
    }


def account_client_auth(
    account_id: str,
    items: dict,
    service: str
):
    """Authenticate and return AWS client for an account."""
    credentials = aws_crawler.get_credentials(
        items['session'],
        f'arn:aws:iam::{account_id}:role/{items["assumed_role_name"]}',
        items['external_id']
    )
    client = boto3.client(
        service,
        aws_access_key_id=credentials['aws_access_key_id'],
        aws_secret_access_key=credentials['aws_secret_access_key'],
        aws_session_token=credentials['aws_session_token'],
        region_name=items['region']
    )
    return client


def main():
    """Execute main function."""
    pass


if __name__ == '__main__':
    main()
