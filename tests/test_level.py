# coding: utf8
# Copyright (C) 2026 Maciej Dems <maciej.dems@p.lodz.pl>
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
import tempfile
import unittest
from copy import deepcopy
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

from robbo import level_document as document
from robbo.levels import LevelSet
from robbo.levels import load_levels, read_level_source


class DocumentTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for module, key, value in ((document, 'USER_DATA_DIR', temp.name),
                                   (import_module('robbo.levels'), 'DATA_DIRS', [temp.name])):
            setting = patch.object(module, key, value)
            setting.start()
            self.addCleanup(setting.stop)

    def test_existing_packs_round_trip_with_object_parameters(self):
        for name in ('ala', 'forever', 'original', 'test'):
            with self.subTest(name=name):
                source = read_level_source(name)
                doc = LevelSet(name, source)
                self.assertEqual(doc.header + ''.join(level.render(i) for i, level in
                                 enumerate(doc.levels, 1)) + doc.tail, source)
                expected = load_levels(name)
                for level, board in zip(doc.levels, expected):
                    # Exercise both compact row arguments and explicit [additional] tables.
                    y, row = next((y, row) for y, row in enumerate(level.rows) if '.' in row)
                    x = row.index('.')
                    level.paint(x, y, '%', ())
                    board['data'] = '\n'.join(level.rows)
                self.assertEqual(doc.save(name), expected)
                self.assertEqual(load_levels(name), expected)

    def test_one_edit_preserves_neighbouring_board_and_notes(self):
        doc = LevelSet('original', read_level_source('original'))
        untouched = doc.levels[1].source
        header = doc.header
        doc.levels[0].paint(1, 1, 'T', ())
        doc.save('original')
        self.assertEqual(doc.header, header)
        self.assertEqual(doc.levels[1].source, untouched)

    def test_new_copy_resize_and_renumber(self):
        doc = LevelSet('my-tests')
        doc.levels.append(deepcopy(doc.levels[0]))
        level = doc.levels[1]
        level.resize(16, 19)
        level.paint(3, 15, 'M', (2,))
        level.paint(4, 12, '&', ('A',))
        level.paint(4, 13, '&', ('A',))
        level.paint(3, 2, 'R', ())
        self.assertEqual(level.tile(1, 1), '.')
        a, b = doc.save('my-tests')
        self.assertEqual((a['level'], b['level'], a['last_level']), ('1', '2', '2'))
        self.assertEqual(b['additional']['&'], {(4, 12): ('A', 0), (4, 13): ('A', 1)})
        doc.levels[1].resize(16, 13)
        doc.levels[1].paint(4, 12, '.', ())
        doc.levels.reverse()
        copy = doc.save('other-set')
        self.assertEqual([b['level'] for b in copy], ['1', '2'])
        self.assertFalse(copy[0]['additional'])
        self.assertEqual(load_levels('my-tests'), [a, b])

    def test_invalid_collision_and_failed_write_keep_original(self):
        doc = LevelSet('my-tests')
        for other in ('../outside', 'original'):
            with self.assertRaises(ValueError):
                doc.save(other)
        doc.save('my-tests')
        path = self.root/'levels'/'my-tests.dat'
        before = path.read_bytes()
        doc.levels[0].paint(1, 1, '.', ())
        with self.assertRaisesRegex(ValueError, 'Level 1'):
            doc.save('my-tests')
        doc.levels[0].paint(5, 3, 'R', ())
        with patch.object(document.os, 'replace', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                doc.save('my-tests')
        self.assertEqual(path.read_bytes(), before)
        path.write_text(path.read_text() + '\n# external edit\n')
        with self.assertRaisesRegex(ValueError, 'changed on disk'):
            doc.save('my-tests')
        doc.save('recovered')
        self.assertEqual(load_levels('recovered')[0]['data'].splitlines()[3][5], 'R')
