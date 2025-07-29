#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Provide helper parameter values."""

import configparser

"""Provide helper parameter values."""
# Read parameters from configuration file.
config = configparser.ConfigParser(allow_no_value=True)
config.read('parameters.ini')

# Execution parameters.
DRY_RUN = config.getboolean('execution', 'DRY_RUN')
THREAD_NUM = config.getint('execution', 'THREAD_NUM')

# AWS entrypoint parameters.
auth_method = config.get('entrypoint', 'auth_method')
profile_name = config.get('entrypoint', 'profile_name')
access_key_id = config.get('entrypoint', 'access_key_id')
secret_access_key = config.get('entrypoint', 'secret_access_key')
sso_url = config.get('entrypoint', 'sso_url')
sso_role_name = config.get('entrypoint', 'sso_role_name')
sso_account_id = config.get('entrypoint', 'sso_account_id')
accounts_list_src = config.get('entrypoint', 'accounts_list_src')

# AWS environment parameters.
region = config.get('environment', 'region')
assumed_role_name = config.get('environment', 'assumed_role_name')
external_id = config.get('environment', 'external_id')
sso_instance_arn = config.get('environment', 'sso_instance_arn')
identity_store_id = config.get('environment', 'identity_store_id')

# AWS accounts parameters.
accounts = config.get('accounts', 'accounts')
ou = config.get('accounts', 'ou')
statuses = config.get('accounts', 'statuses')

# actions_get script parameters.
actions_get_output_file = config.get('actionsget', 'actions_get_output_file')
actions_get_service = config.get('actionsget', 'actions_get_service')
actions_get_filter = config.get('actionsget', 'actions_get_filter')

# sgs_get script parameters.
sgs_get_output_file = config.get('sgsget', 'sgs_get_output_file')

# sso_get script parameters.
sso_get_output_file = config.get('ssoget', 'sso_get_output_file')

# sso_json script parameters.
sso_json_input_file = config.get('ssojson', 'sso_json_input_file')
sso_json_output_file = config.get('ssojson', 'sso_json_output_file')

# sso_mappings script parameters.
sso_mappings_map_file = config.get('ssomappings', 'sso_mappings_map_file')
sso_mappings_input_file = config.get('ssomappings', 'sso_mappings_input_file')
sso_mappings_output_file = config.get('ssomappings', 'sso_mappings_output_file')
sso_mappings_old_user_heading = config.get('ssomappings', 'sso_mappings_old_user_heading')
sso_mappings_new_user_heading = config.get('ssomappings', 'sso_mappings_new_user_heading')
sso_mappings_old_group_pattern = config.get('ssomappings', 'sso_mappings_old_group_pattern')
sso_mappings_new_group_pattern = config.get('ssomappings', 'sso_mappings_new_group_pattern')

# sso_assign script parameters.
sso_assign_input_file = config.get('ssoassign', 'sso_assign_input_file')

# sso_update script parameters.
sso_update_user_map_file = config.get('ssoupdate', 'sso_update_user_map_file')
sso_update_group_map_file = config.get('ssoupdate', 'sso_update_group_map_file')
sso_update_old_user_heading = config.get('ssoupdate', 'sso_update_old_user_heading')
sso_update_new_user_heading = config.get('ssoupdate', 'sso_update_new_user_heading')
sso_update_old_group_heading = config.get('ssoupdate', 'sso_update_old_group_heading')
sso_update_new_group_heading = config.get('ssoupdate', 'sso_update_new_group_heading')

# sso_memberships script parameters.
sso_memberships_input_file = config.get('ssomemberships', 'sso_memberships_input_file')
sso_memberships_output_file = config.get('ssomemberships', 'sso_memberships_output_file')

# s3_getbuckets script parameters.
s3_getbuckets_output_file = config.get('s3getbuckets', 's3_getbuckets_output_file')
s3_getbuckets_prefix = config.get('s3getbuckets', 's3_getbuckets_prefix')

# vpc_getvpcs script parameters.
vpc_getvpcs_output_file = config.get('vpcgetvpcs', 'vpc_getvpcs_output_file')
