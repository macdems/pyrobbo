# coding: utf8
# Copyright (C) 2019 Maciej Dems <maciej.dems@p.lodz.pl>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of GNU General Public License as published by the
# Free Software Foundation; imageseither version 3 of the license, or (at your
# opinion) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import pygame

pygame.init()
pygame.display.set_caption('PyRobbo')

pygame.key.set_repeat(0, 0)

clock = pygame.time.Clock()

screen = pygame.display.set_mode((640, 480))
background = pygame.Surface(screen.get_size())
background = background.convert()

screen_rect = pygame.Rect((64, 32), (512, 384))


from . import game
from .defs import *
from .levels import load_levels


def main():
    load_levels()
    game.play(6)

    print(clock.get_fps())