# coding: utf8
# Copyright (C) 2019 Maciej Dems <maciej.dems@p.lodz.pl>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of GNU General Public License as published by the
# Free Software Foundation; either version 3 of the license, or (at your
# opinion) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
import os
import re
import sys
from pkg_resources import resource_exists, resource_listdir, resource_string

from .defs import DATA_DIRS

file_section_re = re.compile(r'\[(\w+)\]\s*')


# List of symbols with descriptions
RICH = '&@*^}LlM=,'

_TRANS = {'E': 0, 'S': 1, 'W': 2, 'N': 3, '*': 1, '.': 0}


def trans(i):
    try:
        return _TRANS[i]
    except KeyError:
        try:
            return int(i)
        except ValueError:
            return i


def read_local_source(path):
    try:
        with open(path, encoding='utf-8-sig') as infile:
            return infile.read()
    except UnicodeDecodeError:
        # Older local packs may be in the platform's default encoding.
        with open(path) as infile:
            return infile.read()


def read_level_source(name):
    for data_dir in DATA_DIRS:
        try:
            return read_local_source(os.path.join(data_dir, 'levels', name + '.dat'))
        except FileNotFoundError:
            continue
    resource = 'levels/' + name + '.dat'
    if resource_exists('robbo', resource):
        return resource_string('robbo', resource).decode('utf8')
    return read_local_source(name + '.dat')


def load_levels(name='original'):
    return parse_levels(read_level_source(name))


def parse_levels(source):
    levels = []
    level = {}
    section = None
    data = ''
    for lineno, line in enumerate(source.splitlines()):
        try:
            if not line.strip() or (line.startswith('#') and section != 'data'): continue
            m = file_section_re.match(line)
            if m is not None:
                s = m.group(1)
                if section is not None:
                    level[section] = data.rstrip()
                data = ''
                if s == 'end':
                    if 'screws' in level:
                        level['screws'] = int(level['screws'])
                    additional = {}
                    if 'additional' in level:
                        for item in level['additional'].splitlines()[1:]:
                            data = item.split('.')
                            p = tuple(int(n) for n in data[:2])
                            t = data[2]
                            args = data[3:]
                            # Compact packs can use letters for teleport groups.
                            if t == '&' and args and args[0].isalpha():
                                data = (args[0], *(int(n) for n in args[1:]))
                            else:
                                data = tuple(int(n) for n in args)
                            additional.setdefault(t, {})[p] = data
                    else:
                        rows = []
                        for y, row in enumerate(level['data'].splitlines()):
                            row, *info = row.split()
                            rows.append(row)
                            for x, c in enumerate(row):
                                if c in RICH:
                                    p = x, y
                                    for n,val in enumerate(info):
                                        if val.startswith(c): break
                                    else:
                                        raise ValueError("No info for {} in row {}".format(c, y))
                                    data = tuple(trans(i) for i in info.pop(n)[1:])
                                    additional.setdefault(c, {})[p] = data
                        level['data'] = '\n'.join(rows)
                    level['additional'] = additional
                    levels.append(level)
                    level = {}
                    section = None
                else:
                    section = s
            else:
                data += line + '\n'
        except Exception as err:
            raise type(err)("line {}: {}".format(lineno, str(err)))
    return levels


def load_level_sets():
    """Collect playable sets in the order used by the menu and by level progression."""
    files = set(resource_listdir('robbo', 'levels'))
    for directory in [os.path.join(root, 'levels') for root in DATA_DIRS] + ['.']:
        try:
            files.update(os.listdir(directory))
        except FileNotFoundError:
            continue

    sets = {}
    for name in sorted(filename[:-4] for filename in files if filename.endswith('.dat')):
        try:
            boards = load_levels(name)
            if not boards or any(not board.get('data') for board in boards):
                raise ValueError('missing level data')
        except (OSError, ValueError, KeyError, IndexError) as err:
            print("Skipping level set {}: {}".format(name, err), file=sys.stderr)
        else:
            sets[name] = boards
    return sets
