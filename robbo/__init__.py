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
import sys
import os
import argparse
from pkg_resources import resource_listdir
import pygame

from .defs import *
from .levels import load_levels


clock = None
clock_speed = None
screen = None
screen_rect = None
skin = 'default'

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fullscreen', help="start in fullscreen", action='store_true')
parser.add_argument('-s', '--skin', help="selected skin set", type=str, default="default")
parser.add_argument('-b', '--bears', help="prevent bears from stupidly circling around", action='store_true')
parser.add_argument("levelset", help="name of the level set to load", nargs='?')


def quit():
    pygame.quit()
    sys.exit(0)


def main():
    args = parser.parse_args()
    flags = pygame.FULLSCREEN if args.fullscreen else 0

    pygame.init()
    pygame.display.set_caption('PyRobbo')
    pygame.key.set_repeat(0, 0)

    global skin, clock, clock_speed, screen, screen_rect
    skin = args.skin
    clock = pygame.time.Clock()
    clock_speed = 8
    screen = pygame.display.set_mode((640, 480), flags)
    screen_rect = pygame.Rect((64, 32), (512, 384))

    from . import game

    game.level_sets = ['original'] + [dat[:-4] for dat in resource_listdir('robbo', 'levels')
                                      if dat.endswith('.dat') and dat != 'original.dat']

    game.level_sets += [dat for dat in os.listdir('.') if dat.endswith('.dat') and dat[:-4] not in game.level_sets]

    try:
        game.levelset = game.level_sets.index(args.levelset)
    except ValueError:
        if args.levelset is not None and args.levelset.endswith('.dat'):
            game.levelset = len(game.level_sets)
            game.level_sets.append(args.levelset)

    game.clever_bears = args.bears

    load_levels(game.level_sets[game.levelset])
    level = 0
    try:
        while level < len(game.levels):
            try:
                game.play_level(level)
            except game.SelectLevel as selected:
                if selected.level < len(game.levels):
                    level = selected.level
            except game.LoadLevelSet as selected:
                game.levelset = selected.index
                load_levels(game.level_sets[game.levelset])
                level = 0
            else:
                level += 1
    except SystemExit:
        quit()

