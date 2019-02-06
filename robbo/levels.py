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
import re
from pkg_resources import resource_string


file_section_re = re.compile('\[(\w+)\]\s*')


def load_levels(name='original'):
    from . import game
    game.levels = []
    source = resource_string('robbo', 'levels/'+name+'.dat').decode('utf8')
    level = {}
    section = None
    data = ''
    for line in source.splitlines():
        if not line.strip(): continue
        m = file_section_re.match(line)
        if m is not None:
            s = m.group(1)
            if section is not None:
                level[section] = data.rstrip()
            data = ''
            if s == 'end':
                level['size'] = tuple(int(n) for n in level['size'].split('.'))
                if 'screws' in level:
                    level['screws'] = int(level['screws'])
                game.levels.append(level)
                level = {}
                section = None
            else:
                section = s
        else:
            data += line + '\n'
