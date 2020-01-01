"""
Copyright 2020 (c) GlibGlob Ltd.
Author: Laurence
Email: vesper.porta@protonmail.com

Load and parse a CSV file.
"""

import os
from os.path import isfile, join

from models import Stat, StatType, StatGroup


data_path = 'datasheets/'
data_extension = '.csv'
LOADED_INFO = {}


def _get_file(name):
    os.chdir(os.path.dirname(__file__))
    path = join(os.getcwd(), data_path, '{}{}'.format(name, data_extension))
    if not isfile(path):
        raise Exception('Failed to find data source. path={}'.format(path))
    file = open(path, encoding='UTF-8')
    return file


def _str_to_float(value):
    try:
        return float(value)
    except ValueError:
        pass
    try:
        return int(value)
    except ValueError:
        pass
    return value


def _define_row_data_in_object(row, headers, class_definition=None):
    if not row:
        return None
    kay_value_ids = ['cross', 'affect', 'spread', 'draw', ]
    skip_ids = ['mult', 'value', ]
    rtn = class_definition() if class_definition else Stat()
    index = -1
    for key in headers:
        index += 1
        key_low = key.lower().replace(' ', '_')
        value = row[index]
        if not value or key_low in skip_ids:
            continue
        if '|' in value:
            value = value.split('|')
        if key_low in ['type']:
            # Race type required for this value
            value = StatType(name=value)
        if key_low in ['group']:
            # Race type required for this value
            value = StatGroup(name=value)
        if key_low in kay_value_ids:
            value = getattr(rtn, key_low) or []
            if row[index]:
                value.append(
                    StatType(row[index], ratio=_str_to_float(row[index + 1])))
        if not hasattr(rtn, key_low):
            rtn.unknown[key] = value
        setattr(rtn, key_low, value)
    return rtn


def load_stat_csv(name, row_data=False, group=None):
    file = _get_file(name)
    index = -1
    info = {
        'name': name, 'plural': name, 'description': '', 'base_value': 0,
        'headers': [],
    }
    LOADED_INFO[name] = info
    if not group:
        group = StatGroup(
            name=info['plural'],
            description=info['description'],
        )
    stats = []
    try:
        for line in file:
            index += 1
            row = line.replace('\n', '').split(',')
            if '"' in line:
                consolidate = False
                count = -1
                consolidate_index = -1
                consolidating = ''
                strip_indexes = []
                for item in row:
                    count += 1
                    if '"' in item:
                        consolidate = not consolidate
                        if consolidate:
                            consolidate_index = count
                    if consolidate:
                        consolidating += '{}{}'.format(
                            ',' if count > consolidate_index else '',
                            item
                        )
                    elif consolidate_index > 0:
                        row[consolidate_index] = consolidating.replace('"', '')
                        strip_indexes += [
                            consolidate_index + 1 + i
                            for i in range(count - consolidate_index)
                        ]
                        consolidating = ''
                        consolidate_index = -1
                for index in strip_indexes:
                    row = row[:index] + row[index + 1:]
            if not row[0]:
                continue
            if index == 0:
                info['headers'] = row
                continue
            if row_data:
                stats.append(row)
                continue
            stat = _define_row_data_in_object(row, info['headers'])
            if not stat.group:
                stat.group = group
            stats.append(stat)
    except UnicodeDecodeError as error:
        print(error)
    group.stats = stats
    return group if not row_data else stats
