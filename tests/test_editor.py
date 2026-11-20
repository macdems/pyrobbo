import os
import unittest
from unittest.mock import patch

import pygame

import robbo
from robbo.editor import CANVAS, CELL, LevelEditor
from robbo.levels import load_levels


class EditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env = patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
        env.start()
        cls.addClassCleanup(env.stop)
        pygame.init()
        cls.addClassCleanup(pygame.quit)
        screen = patch.object(robbo, 'screen', pygame.display.set_mode((1000, 600)))
        screen.start()
        cls.addClassCleanup(screen.stop)

    def setUp(self):
        self.ui = LevelEditor(robbo.screen, {'original': load_levels('original')}, 'original', 0)

    def click(self, pos, button=1):
        rect = self.ui.viewport
        point = (rect.x + round(pos[0]*rect.w/640), rect.y + round(pos[1]*rect.h/480))
        for kind in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.ui.handle(pygame.event.Event(kind, pos=point, button=button))

    def key(self, key, mod=0):
        self.ui.handle(pygame.event.Event(pygame.KEYDOWN, key=key, mod=mod))

    def type_text(self, value):
        self.ui.handle(pygame.event.Event(pygame.TEXTINPUT, text=value))

    def test_scaled_paint_tile_options_pick_erase_undo(self):
        ui = self.ui
        self.click(ui.swatches['}'].center)
        ui.tile_options()
        self.key(pygame.K_RIGHT)  # face south
        self.key(pygame.K_RETURN)
        self.assertEqual(ui.args, (1, 0, 0, 0, 0, 0))
        ui.pan(0, 6)
        pos = (CANVAS.x+CELL+8, CANVAS.y+CELL+8)
        self.click(pos)
        self.assertEqual(ui.level.tile(1, 7), '}')
        self.assertEqual(ui.level.extra['}'][1, 7], ui.args)
        self.click(ui.swatches['O'].center)
        self.click(pos, 2)
        self.assertEqual((ui.brush, ui.args[0]), ('}', 1))
        self.click(pos, 3)
        self.assertEqual(ui.level.tile(1, 7), '.')
        self.key(pygame.K_z, pygame.KMOD_CTRL)
        self.assertEqual(ui.level.tile(1, 7), '}')
        ui.draw()

    def test_reorder_resize_and_cancel_discard(self):
        ui = self.ui
        ui.add(False)
        ui.settings()
        self.type_text('1')  # move the new level ahead of the original first board
        self.key(pygame.K_TAB)
        self.type_text('15')
        self.key(pygame.K_TAB)
        self.type_text('24')
        self.key(pygame.K_RETURN)
        self.assertEqual((ui.index, ui.level.size), (0, (15, 24)))
        ui.done()
        self.key(pygame.K_ESCAPE)
        self.assertFalse(ui.finished)
        ui.undo()
        self.assertEqual((ui.index, ui.level.size), (1, (16, 12)))
        ui.undo()
        self.assertEqual((len(ui.doc.levels), ui.dirty), (58, False))
        ui.done()
        self.assertTrue(ui.finished)
