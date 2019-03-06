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
import argparse
import pygame

from .defs import *
from .levels import load_levels


clock = None
clock_speed = None
screen = None
screen_rect = None


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fullscreen', help="start in fullscreen", action='store_true')
parser.add_argument('-s', '--skin', help="selected skin set", type=str, default="default")
parser.add_argument('-b', '--bears', help="prevent bears from stupidly circling around", action='store_true')
parser.add_argument("levelset", help="name of the level set to load", nargs='?', default="original")
args = parser.parse_args()

skin = args.skin
levels = args.levelset

flags = pygame.FULLSCREEN if args.fullscreen else 0


def main():
    pygame.init()
    pygame.display.set_caption('PyRobbo')

    pygame.key.set_repeat(0, 0)

    global clock, clock_speed, screen, screen_rect
    clock = pygame.time.Clock()
    clock_speed = 8
    screen = pygame.display.set_mode((640, 480), flags)
    screen_rect = pygame.Rect((64, 32), (512, 384))

    from . import game

    game.clever_bears = args.bears

    load_levels(levels)
    level = 0
    try:
        while level < len(game.levels):
            try:
                game.play_level(level)
            except game.SelectLevel as selected:
                if selected.level < len(game.levels):
                    level = selected.level
            else:
                level += 1
    except SystemExit:
        pygame.quit()

