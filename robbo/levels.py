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
import tempfile
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path, PureWindowsPath
from pkg_resources import resource_exists, resource_listdir, resource_string

from .defs import DATA_DIRS, USER_DATA_DIR

file_section_re = re.compile(r'\[(\w+)\]\s*')

# List of symbols with descriptions
RICH = '&@*^}LlM=,'

_TRANS = {'E': 0, 'S': 1, 'W': 2, 'N': 3, '*': 1, '.': 0}

END = re.compile(r'^\[end\][^\n]*(?:\n|$)', re.M)
FIRST_BOARD_TAG = re.compile(r'^\[(?:level|offset|size|data|colour|author|level_notes|screws|additional)\]', re.M)


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
                                    for n, val in enumerate(info):
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


def set_section(text, key, value):
    block = '[{}]\n{}\n'.format(key, value) if value is not None else ''
    pattern = re.compile(r'^\[' + key + r'\][^\n]*\n.*?(?=^\[\w+\]|\Z)', re.M | re.S)
    if pattern.search(text):
        return pattern.sub(lambda m: block, text, count=1)
    end = END.search(text)
    pos = end.start() if end else len(text)
    return text[:pos] + block + text[pos:]


def check_name(name):
    if (not re.fullmatch(r'[\w-][\w .-]*', name) or name.endswith(('.', ' ')) or PureWindowsPath(name + '.dat').is_reserved()):
        raise ValueError('Use a filename with letters, numbers, spaces, dashes or underscores.')


@contextmanager
def save_lock(directory):
    """Serialise the source check and replace. Closing the handle releases the lock."""
    with (directory / '.editor.lock').open('a+b') as lock:
        if os.name == 'nt':
            import msvcrt
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


class Level:

    def __init__(self, source):
        self.source = source
        try:
            self.original = parse_levels(source)[0]
        except (KeyError, IndexError) as err:
            raise ValueError('Incomplete level data.') from err
        self.rows = self.original['data'].splitlines()
        self.extra = deepcopy(self.original['additional'])
        self.colour = self.original.get('colour', '404080')
        self.author = self.original.get('author', '')
        self.screws = self.original.get('screws')

    @classmethod
    def new(cls):
        rows = ['O' * 16, 'OR' + '.' * 13 + 'O'] + ['O' + '.' * 14 + 'O'] * 8
        rows += ['O' + '.' * 12 + 'T!O', 'O' * 16]
        return cls('[level]\n1\n[data]\n' + '\n'.join(rows) + '\n[end]\n')

    @property
    def size(self):
        return max(map(len, self.rows)), len(self.rows)

    def resize(self, width, height):
        self.rows = [row[:width].ljust(width, '.') for row in self.rows[:height]]
        self.rows += ['.' * width] * (height - len(self.rows))
        for coords in self.extra.values():
            for x, y in list(coords):
                if x >= width or y >= height:
                    del coords[x, y]

    def tile(self, x, y):
        return self.rows[y][x] if x < len(self.rows[y]) else '.'

    def paint(self, x, y, symbol, args):
        previous = self.tile(x, y)
        old_args = self.extra.get(previous, {}).get((x, y), ())
        if symbol == '&':
            group, = args
            if previous == '&' and old_args and group == old_args[0]:
                return False
            used = {index for g, index in self.extra.get('&', {}).values() if g == group}
            index = 0
            while index in used:
                index += 1
            args = (group, index)
        if previous == symbol and old_args == args:
            return False
        if symbol == 'R':
            self.rows = [row.replace('R', '.') for row in self.rows]
        self.extra.get(previous, {}).pop((x, y), None)
        if args:
            self.extra.setdefault(symbol, {})[x, y] = args
        row = self.rows[y].ljust(x + 1, '.')
        self.rows[y] = row[:x] + symbol + row[x + 1:]
        return True

    def render(self, number):
        source = self.source
        data = '\n'.join(self.rows)
        if data.count('R') != 1 or '!' not in data:
            raise ValueError('Level {} needs one Robbo and at least one capsule.'.format(number))
        if data != self.original['data'] or self.extra != self.original['additional']:
            records = [
                '.'.join(map(str, (x, y, symbol, *args))) for symbol, coords in self.extra.items()
                for (x, y), args in coords.items()
            ]
            source = set_section(source, 'data', data)
            source = set_section(source, 'additional', '\n'.join([str(len(records))] + records))
            if 'size' in self.original:
                source = set_section(source, 'size', '{}.{}'.format(*self.size))
        for key, value, fallback in (('level', str(number), None), ('colour', self.colour, '404080'), ('author', self.author, ''),
                                     ('screws', self.screws, None)):
            if value != self.original.get(key, fallback):
                source = set_section(source, key, value)
        return source


class LevelSet:

    def __init__(self, name, source=None):
        self.name = name
        self.original = source
        self.header = ''
        self.tail = ''
        self.levels = []
        if source is None:
            self.levels.append(Level.new())
        else:
            start = FIRST_BOARD_TAG.search(source)
            if not start:
                raise ValueError('No level data found.')
            pos = start.start()
            self.header = source[:pos]
            for end in END.finditer(source, pos):
                self.levels.append(Level(source[pos:end.end()]))
                pos = end.end()
            if not self.levels:
                raise ValueError('The set has no complete levels.')
            self.tail = source[pos:]

    def save(self, name):
        new_file = self.original is None or name != self.name
        if new_file:
            check_name(name)
        header = self.header
        if new_file:
            header = set_section(header, 'name', name)
        if new_file or len(self.levels) != len(END.findall(self.original or '')):
            header = set_section(header, 'last_level', len(self.levels))
        chunks = [level.render(i) for i, level in enumerate(self.levels, 1)]
        source = header + ''.join(chunk if chunk.endswith('\n') else chunk + '\n' for chunk in chunks) + self.tail
        boards = parse_levels(source)
        directory = Path(USER_DATA_DIR) / 'levels'
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / (name + '.dat')
        with save_lock(directory):
            try:
                current = read_level_source(name)
            except FileNotFoundError:
                current = None
            if new_file and current is not None:
                raise ValueError('A set with that name already exists.')
            if not new_file and current != self.original:
                raise ValueError('Set changed on disk. Use Save as to keep your edits.')
            tmp = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=directory, delete=False) as f:
                    tmp = Path(f.name)
                    f.write(source)
                os.replace(tmp, target)
            finally:
                if tmp is not None and tmp.exists():
                    tmp.unlink()
        # Rebase future edits on the exact file just written.
        self.__init__(name, source)
        return boards
