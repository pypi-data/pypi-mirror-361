#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Provide common helper functions."""

import sys
import csv
import json
import datetime
import logging
from typing import Union, Dict, List


__application__ = "aws_administrator_common_helper"


def get_current_time() -> str:
    """Get current date and time in UTC."""
    return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d_%H-%M-%S')


def exception_handler(type, value, tb) -> None:
    """Handle uncaught exceptions."""
    logger = logging.getLogger(f'{__name__}')
    logging.basicConfig(
        filename=f'/tmp/{__application__}.{get_current_time()}.log',
        level=logging.WARNING
    )
    log_level = 30
    # NOTSET (0), DEBUG (10), INFO (20), WARNING (30), ERROR (40), CRITICAL (50), NONE (100)
    logger.setLevel(log_level)

    error_message = (
        f'{type.__name__}: {tb.tb_frame.f_code.co_name} '
        f'at line {tb.tb_lineno} in {tb.tb_frame.f_code.co_filename}: '
        f'{str(value)}'
    )
    print(error_message)
    logger.error(f'{get_current_time()}:Exception: {str(error_message)}')


def read_csv(
    file_name: str
) -> list:
    """Read CSV file and convert to dictionaries."""
    with open(file_name, 'r') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
    return data


def dicts_to_csv(
    data: list
) -> list:
    """Convert dicts data to CSV list."""
    csv_data = [list(data[0].keys())]
    for row in data:
        csv_data.append(list(row.values()))
    return csv_data


def export_csv(
    data: list,
    file: str
) -> None:
    """Export data to CSV file."""
    with open(file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def read_json(
    file_name: str
) -> dict:
    """Read JSON file."""
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


def write_json_obj(
    file_name: str,
    data: Union[Dict, List]
) -> None:
    """Write JSON to file."""
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4, default=str)


def write_json_str(
    file_name: str,
    data: str
) -> None:
    """Write JSON strings to file."""
    with open(file_name, 'w') as f:
        f.write(data)


def get_value_from_tag(
    tags: list,
    tag_key: str
) -> str:
    """Get tag value for a tag key from a list of tags."""
    value = ''
    for tag in tags:
        if tag['Key'] == tag_key:
            value = tag['Value']
            break
    return value


def main():
    """Execute main function."""
    pass


sys.excepthook = exception_handler

if __name__ == '__main__':
    main()
