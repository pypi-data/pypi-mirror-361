#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Provide common AWS IAM multithreaded functions."""


def get_actions(
    session,
    service: str
) -> list:
    """
    Get AWS actions by service name.

    Ref: https://stackoverflow.com/questions/51930111/boto3-get-available-actions-per-service

    This is not 100% comprehensive. For example, it doesn't include "iam:PassRole".
    """
    actions = []

    match service:

        # If service is not specified, get all services.
        case None:

            # For non-IAM services.
            for service in session.get_available_services():
                service_client = session.client(service)
                actions.append(
                    {
                        "service": service,
                        "actions": service_client.meta.service_model.operation_names
                    }
                )

            # For IAM.
            iam = session.client('iam')
            actions.append(
                {
                    "service": "iam",
                    "actions": iam.meta.service_model.operation_names
                }
            )

        # Get actions for iam only.
        case 'iam':
            iam = session.client('iam')
            actions.append(
                {
                    "service": "iam",
                    "actions": iam.meta.service_model.operation_names
                }
            )

        # Get actions for specified service.
        case _:
            service_client = session.client(service)
            actions.append(
                {
                    "service": service,
                    "actions": service_client.meta.service_model.operation_names
                }
            )

    return actions


def filter_actions_keyword(
    data: list,
    keyword: str
) -> list:
    """Filter AWS actions by keyword."""
    filtered_actions = []
    for service in data:
        for action in service['actions']:
            if keyword in action:
                filtered_actions.append(f'{service['service']}:{action}')
    return filtered_actions


def main():
    """Execute main function."""
    pass


if __name__ == '__main__':
    main()
