#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Provide common AWS SSO multithreaded functions."""

from time import sleep


def get_permission_sets(
    account_id: str,
    items: dict
) -> dict:
    """Get AWS Permission Set assignments from an AWS account."""
    print(f'Working on {account_id}...')

    try:
        # Get list of assigned Permission Sets in each account.
        # If latest Permission Set version provisioned to account.
        permission_sets_latest = items['sso_admin'].list_permission_sets_provisioned_to_account(
            AccountId=account_id,
            InstanceArn=items['sso_instance_arn'],
            ProvisioningStatus='LATEST_PERMISSION_SET_PROVISIONED'
        )

        # If latest Permission Set version not provisioned to account.
        permission_sets_notlatest = items['sso_admin'].list_permission_sets_provisioned_to_account(
            AccountId=account_id,
            InstanceArn=items['sso_instance_arn'],
            ProvisioningStatus='LATEST_PERMISSION_SET_NOT_PROVISIONED'
        )

        # Combine results from both lists.
        permission_sets = []
        if permission_sets_latest is not None:
            permission_sets.extend(permission_sets_latest['PermissionSets'])
        if permission_sets_notlatest is not None:
            permission_sets.extend(permission_sets_notlatest['PermissionSets'])

        # Get list of Users and Groups in all assigned Permission Sets for each account.
        response = []

        # Get assignments for each Permission Set.
        for permission_set in permission_sets:
            assignments = items['sso_admin'].list_account_assignments(
                AccountId=account_id,
                InstanceArn=items['sso_instance_arn'],
                PermissionSetArn=permission_set
            )

            # Get data for each Principal.
            principals = []
            for principal in assignments['AccountAssignments']:

                try:
                    # Get User human-readable name.
                    if principal['PrincipalType'] == 'USER':
                        user = items['identity_store'].describe_user(
                            IdentityStoreId=items['identity_store_id'],
                            UserId=principal['PrincipalId']
                        )
                        principal = {
                            'id': user['UserName'],
                            'type': 'USER'
                        }

                    # Get Group human-readable name.
                    elif principal['PrincipalType'] == 'GROUP':
                        group = items['identity_store'].describe_group(
                            IdentityStoreId=items['identity_store_id'],
                            GroupId=principal['PrincipalId']
                        )
                        principal = {
                            'id': group['DisplayName'],
                            'type': 'GROUP'
                        }

                    # Just in case the PrincipalType is not USER or GROUP.
                    # Should not be the case, though.
                    else:
                        principal = {
                            'id': 'Unknown principal',
                            'type': 'Unknown principal type'
                        }

                # Catch Principal with missing data while allowing the rest to continue.
                except Exception:
                    principal = {
                        'id': 'Unknown principal',
                        'type': 'Unknown principal type'
                    }

                # Add Principal to list for each Permission Set.
                principals.append(principal)

            # Get Permission Set human-readable name.
            name = items['sso_admin'].describe_permission_set(
                InstanceArn=items['sso_instance_arn'],
                PermissionSetArn=permission_set
            )

            # Add data for each Permission Set to final result.
            response.append({
                'permission_set': name['PermissionSet']['Name'],
                'principals': principals
            })

    # In case of any exceptions, return the error message but allow loop to continue.
    except Exception as e:
        response = [str(e)]

    return {
        'account_id': account_id,
        'details': response
    }


def read_users(
    data: list
) -> list:
    """Get Users from AWS SSO mappings data."""
    users = []
    for assignment in data:
        for detail in assignment['details']:
            for principal in detail['principals']:
                if principal['type'] == 'USER':
                    users.append(principal['id'])
    return list(set(users))


def read_groups(
    data: list
) -> list:
    """Get Groups from AWS SSO mappings data."""
    groups = []
    for assignment in data:
        for detail in assignment['details']:
            for principal in detail['principals']:
                if principal['type'] == 'GROUP':
                    groups.append(principal['id'])
    return list(set(groups))


def read_permission_sets(
    data: list
) -> list:
    """Read Permission Sets from dictionary."""
    permission_sets = []
    for detail in data:
        for item in detail:
            permission_sets.append(item['permission_set'])
    return list(set(permission_sets))


def get_all_permission_set_arns(
    sso_admin,
    sso_instance_arn: str
) -> list:
    """List all Permission Sets in the organization."""
    paginator = sso_admin.get_paginator('list_permission_sets')
    response_iterator = paginator.paginate(
        InstanceArn=sso_instance_arn
    )
    permission_sets = []
    for page in response_iterator:
        for permission_set in page['PermissionSets']:
            permission_sets.append(permission_set)
    return permission_sets


def get_user_id(
    user_name: str,
    items: dict
) -> dict:
    """Get AWS SSO User ID from user name."""
    print(f'Getting user ID for {user_name}...')
    try:
        response = items['identity_store'].get_user_id(
            IdentityStoreId=items['identity_store_id'],
            AlternateIdentifier={
                'UniqueAttribute': {
                    'AttributePath': 'userName',
                    'AttributeValue': user_name
                }
            }
        )
        user_id = response['UserId']
    except Exception:
        user_id = 'Unknown user'
    return {
        'user_name': user_name,
        'user_id': user_id
    }


def get_group_id(
    group_name: str,
    items: dict
) -> dict:
    """Get AWS SSO Group ID from group name."""
    print(f'Getting group ID for {group_name}...')
    try:
        response = items['identity_store'].get_group_id(
            IdentityStoreId=items['identity_store_id'],
            AlternateIdentifier={
                'UniqueAttribute': {
                    'AttributePath': 'displayName',
                    'AttributeValue': group_name
                }
            }
        )
        group_id = response['GroupId']
    except Exception:
        group_id = 'Unknown group'
    return {
        'group_name': group_name,
        'group_id': group_id
    }


def get_permission_set_arn(
    permission_set_name: str,
    items: dict
) -> dict:
    """Get AWS SSO Permission Set ARN from name."""
    print(f'Getting Permission Set ARN for {permission_set_name}...')
    try:
        for permission_set in items['permission_sets']:
            name = items['sso_admin'].describe_permission_set(
                InstanceArn=items['sso_instance_arn'],
                PermissionSetArn=permission_set
            )
            if name['PermissionSet']['Name'] == permission_set_name:
                arn = permission_set
                break
    except Exception:
        arn = 'Unknown permission set'
    return {
        'permission_set_name': permission_set_name,
        'permission_set_arn': arn
    }


def process_json(
    file_name: str,
    user_ids: list,
    group_ids: list,
    permission_set_arns: list
) -> str:
    """Replace principals and Permission Sets with their IDs."""
    with open(file_name, 'r') as f:
        data = f.read()
    for user_id in user_ids:
        data = data.replace(
            user_id['user_name'],
            user_id['user_id']
        )
    for group_id in group_ids:
        data = data.replace(
            group_id['group_name'],
            group_id['group_id']
        )
    for permission_set_arn in permission_set_arns:
        data = data.replace(
            permission_set_arn['permission_set_name'],
            permission_set_arn['permission_set_arn']
        )
    return data


def process_mappings(
    data: list,
    file_name: str,
    sso_mappings_old_user_heading: str,
    sso_mappings_new_user_heading: str,
    sso_mappings_old_group_pattern: str,
    sso_mappings_new_group_pattern: str
) -> str:
    """Replace principals with new identities."""
    with open(file_name, 'r') as f:
        mappings = f.read()
    for user in data:
        mappings = mappings.replace(
            user[sso_mappings_old_user_heading],
            user[sso_mappings_new_user_heading]
        )
    mappings = mappings.replace(
        sso_mappings_old_group_pattern,
        sso_mappings_new_group_pattern)
    return mappings


def assign_permission_sets(
    account_id: str,
    items: dict
) -> list:
    """Assign AWS Permission Sets to an AWS account."""
    print(f'Working on {account_id}...')

    responses = []

    try:
        # Loop through each Permission Set detail for the account.
        assignments = [
            assignment['details'] for assignment in items['data']
            if assignment['account_id'] == account_id
        ]
        for assignment in assignments:
            for detail in assignment:
                for principal in detail['principals']:

                    # Skip unknown principals.
                    if principal['id'] != 'Unknown principal':

                        # Check if the assignment already exists.
                        existing = items['sso_admin'].list_account_assignments_for_principal(
                            Filter={
                                'AccountId': account_id,
                            },
                            InstanceArn=items['sso_instance_arn'],
                            PrincipalId=principal['id'],
                            PrincipalType=principal['type']
                        )

                        # Create the assignment if it does not exist.
                        if existing['AccountAssignments'] == []:
                            response = items['sso_admin'].create_account_assignment(
                                InstanceArn=items['sso_instance_arn'],
                                TargetId=account_id,
                                TargetType='AWS_ACCOUNT',
                                PermissionSetArn=detail['permission_set'],
                                PrincipalType=principal['type'],
                                PrincipalId=principal['id']
                            )

                            # Check assignment status (timeout after 10 seconds).
                            status = 'IN_PROGRESS'
                            counter = 0
                            while status != 'SUCCEEDED' and counter < 10:
                                status_call = items['sso_admin'].describe_account_assignment_creation_status(
                                    AccountAssignmentCreationRequestId=response[
                                        'AccountAssignmentCreationStatus'
                                    ][
                                        'RequestId'
                                    ],
                                    InstanceArn=items['sso_instance_arn']
                                )
                                status = status_call['AccountAssignmentCreationStatus']['Status']
                                counter += 1
                                sleep(1)

                            # Collect responses.
                            responses.append(
                                {
                                    'account_id': account_id,
                                    'permission_set': detail['permission_set'],
                                    'principal': principal['id'],
                                    'status': status
                                }
                            )

                        # Skip the assignment if it already exists.
                        else:
                            responses.append(
                                {
                                    'account_id': account_id,
                                    'permission_set': detail['permission_set'],
                                    'principal': principal['id'],
                                    'status': 'Assignment already exists'
                                }
                            )

    except Exception as e:
        responses.append(
            {
                'account_id': account_id,
                'permission_set': 'Error assigning Permission Set',
                'principal': 'Error assigning Principal',
                'status': str(e)
            }
        )
    return responses


def assign_permission_sets_dry_run(
    account_id: str,
    items: dict
) -> list:
    """
    Assign AWS Permission Sets to an AWS account.

    Dry run version.
    Print the results without actually assigning the Permission Sets
    to verify target accounts.
    """
    print(f'Working on {account_id}...')

    responses = []

    try:
        assignments = [
            assignment['details'] for assignment in items['data']
            if assignment['account_id'] == account_id
        ]
        for assignment in assignments:
            for detail in assignment:
                for principal in detail['principals']:

                    # Skip unknown principals.
                    if principal['id'] != 'Unknown principal':

                        # Check if the assignment already exists.
                        existing = items['sso_admin'].list_account_assignments_for_principal(
                            Filter={
                                'AccountId': account_id,
                            },
                            InstanceArn=items['sso_instance_arn'],
                            PrincipalId=principal['id'],
                            PrincipalType=principal['type']
                        )

                        # Create the assignment if it does not exist.
                        if existing['AccountAssignments'] == []:
                            responses.append(
                                {
                                    'account_id': account_id,
                                    'permission_set': detail['permission_set'],
                                    'principal': principal['id'],
                                    'status': 'Dry run for target verification'
                                }
                            )

                        # Skip the assignment if it already exists.
                        else:
                            responses.append(
                                {
                                    'account_id': account_id,
                                    'permission_set': detail['permission_set'],
                                    'principal': principal['id'],
                                    'status': 'Dry run - assignment already exists'
                                }
                            )

    except Exception as e:
        responses.append(
            {
                'account_id': account_id,
                'permission_set': 'Error assigning Permission Set',
                'principal': 'Error assigning Principal',
                'status': str(e)
            }
        )
    return responses


def update_user_name(
    user_dict: dict,
    items: dict
) -> dict:
    """Update AWS SSO User name."""
    print(f'Working on {user_dict['old_user_name']}...')

    try:
        # Get User ID.
        user = items['identity_store'].get_user_id(
            IdentityStoreId=items['identity_store_id'],
            AlternateIdentifier={
                'UniqueAttribute': {
                    'AttributePath': 'userName',
                    'AttributeValue': user_dict['old_user_name']
                }
            }
        )
        user_id = user['UserId']

        # Announce planned change if DRY_RUN is True.
        if items['DRY_RUN']:
            print(
                f'Planned change: '
                f'{user_dict['old_user_name']} -> '
                f'{user_dict['new_user_name']} '
                f'for User ID: {user_id}.'
            )
            update_user = {'DRY_RUN': user_id}
            status = 'DRY_RUN'

        # Update User name if User ID exists.
        if user_id and not items['DRY_RUN']:
            update_user = items['identity_store'].update_user(
                IdentityStoreId=items['identity_store_id'],
                UserId=user_id,
                Operations=[
                    {
                        'AttributePath': 'userName',
                        'AttributeValue': user_dict['new_user_name']
                    },
                    {
                        'AttributePath': 'emails',
                        'AttributeValue': [
                            {
                                'Value': user_dict['new_user_name'],
                                'Primary': True
                            }
                        ]
                    },
                ]
            )
            status = update_user['ResponseMetadata']['HTTPStatusCode']

    except Exception as e:
        user_id = 'See status for error'
        status = {'Error': str(e)}

    return {
        'old_user_name': user_dict['old_user_name'],
        'new_user_name': user_dict['new_user_name'],
        'user_id': user_id,
        'status': status
    }


def update_group_name(
    group_dict: dict,
    items: dict
) -> dict:
    """Update AWS SSO Group name."""
    print(f'Working on {group_dict['old_group_name']}...')

    try:
        # Get Group ID.
        group = items['identity_store'].get_group_id(
            IdentityStoreId=items['identity_store_id'],
            AlternateIdentifier={
                'UniqueAttribute': {
                    'AttributePath': 'displayName',
                    'AttributeValue': group_dict['old_group_name']
                }
            }
        )
        group_id = group['GroupId']

        # Announce planned change if DRY_RUN is True.
        if items['DRY_RUN']:
            print(
                f'Planned change: '
                f'{group_dict['old_group_name']} -> '
                f'{group_dict['new_group_name']} '
                f'for Group ID: {group_id}.'
            )
            update_group = {'DRY_RUN': group_id}
            status = 'DRY_RUN'

        # Update Group name if Group ID exists.
        if group_id and not items['DRY_RUN']:
            update_group = items['identity_store'].update_group(
                IdentityStoreId=items['identity_store_id'],
                GroupId=group_id,
                Operations=[
                    {
                        'AttributePath': 'displayName',
                        'AttributeValue': group_dict['new_group_name']
                    },
                ]
            )
            status = update_group['ResponseMetadata']['HTTPStatusCode']

    except Exception as e:
        group_id = 'See status for error'
        status = {'Error': str(e)}

    return {
        'old_group_name': group_dict['old_group_name'],
        'new_group_name': group_dict['new_group_name'],
        'group_id': group_id,
        'status': status
    }


def get_group_memberships(
    group_name: str,
    items: dict
) -> dict:
    """Get AWS SSO Group memberships from group name."""
    print(f'Getting Group memberships for {group_name}...')
    try:
        # Get Group ID from name.
        group_id = get_group_id(group_name, items)['group_id']

        # Get Group memberships from ID.
        paginator = items['identity_store'].get_paginator('list_group_memberships')
        response_iterator = paginator.paginate(
            IdentityStoreId=items['identity_store_id'],
            GroupId=group_id
        )

        # List User IDs in Group.
        user_ids = []
        for page in response_iterator:
            for membership in page['GroupMemberships']:
                user_ids.append(membership['MemberId']['UserId'])

        # Get User names from IDs.
        user_names = []
        for user_id in user_ids:
            user_name = items['identity_store'].describe_user(
                IdentityStoreId=items['identity_store_id'],
                UserId=user_id
            )['UserName']
            user_names.append(user_name)

    except Exception as e:
        user_names = [str(e)]

    return {
        'group_name': group_name,
        'user_names': user_names
    }


def main():
    """Execute main function."""
    pass


if __name__ == '__main__':
    main()
