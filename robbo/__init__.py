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
import appdirs
import yaml
from pkg_resources import resource_listdir
import pygame
from pygame.constants import K_UP, K_DOWN, K_RETURN

from .defs import *
from .levels import load_levels


clock = None
clock_speed = None
screen = None
screen_rect = None
skin = 'default'

parser = argparse.ArgumentParser()
parser_screen = parser.add_mutually_exclusive_group()
parser_screen.add_argument('-f', '--fullscreen', help="start in fullscreen", action='store_true')
parser_screen.add_argument('-w', '--window', help="start in window", action='store_true')
parser.add_argument('-s', '--skin', help="selected skin set", type=str, default="default")
parser.add_argument("levelset", help="name of the level set to load", nargs='?')

config_file = os.path.join(appdirs.user_config_dir(), 'pyrobbo.yml')

level_sets = ['original']
levelset = 'default'

levels = {}


def quit():
    from . import game
    config = {
        'levelset': levelset,
        'levels': levels,
        'cleverbears': game.clever_bears,
        'fullscreen': bool(screen.get_flags() & pygame.FULLSCREEN)
    }
    yaml.dump(config, open(config_file, 'w'), default_flow_style=False)
    pygame.quit()
    sys.exit(0)


def select_levelset():
    screen.set_clip(screen.get_rect())
    X, Y, W, H = 64, 432, 512, 32
    rect = pygame.Rect(X, Y, W, H)

    font = pygame.font.Font(None, 48)

    level = level_sets.index(levelset)

    while True:
        text = font.render(level_sets[level].upper(), 0, (255, 255, 255))
        screen.fill((0, 0, 0), rect)
        w = text.get_width()
        screen.blit(text, (X + (W-w)//2, Y))
        pygame.display.flip()
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level = (level - 1) % len(level_sets)
            if event.key == pygame.K_DOWN:
                level = (level + 1) % len(level_sets)
            if event.key == K_RETURN:
                screen.fill((0, 0, 0), rect)
                return level_sets[level]
        pygame.event.pump()


def main():
    args = parser.parse_args()

    try:
        config = yaml.load(open(config_file, 'r'))
    except FileNotFoundError:
        config = {}

    if args.fullscreen:
        flags = pygame.FULLSCREEN
    elif args.window:
        flags = 0
    else:
        flags = pygame.FULLSCREEN if config.get('fullscreen', True) else 0


    pygame.init()
    pygame.display.set_caption('PyRobbo')
    pygame.key.set_repeat(0, 0)

    global skin, level_sets, levelset, clock, clock_speed, screen, screen_rect
    skin = args.skin
    clock = pygame.time.Clock()
    clock_speed = 8
    screen = pygame.display.set_mode((640, 480), flags)
    screen_rect = pygame.Rect((64, 32), (512, 384))

    from . import game

    level_sets = ['original'] + [dat[:-4] for dat in resource_listdir('robbo', 'levels')
                                 if dat.endswith('.dat') and dat != 'original.dat']
    level_sets += [dat for dat in os.listdir('.') if dat.endswith('.dat') and dat[:-4] not in level_sets]

    try:
        levelset = level_sets.index(args.levelset)
    except ValueError:
        if args.levelset is not None and args.levelset.endswith('.dat'):
            levelset = len(level_sets)
            level_sets.append(args.levelset)
        else:
            levelset = config.get('levelset', 'default')
    level = config.get('levels', {}).get(levelset, 0)
    game.clever_bears = config.get('cleverbears', False)

    load_levels(levelset)
    while level < len(game.levels):
        try:
            levels[levelset] = level
            game.play_level(level)
        except game.SelectLevel as selected:
            if selected.level < len(game.levels):
                level = selected.level
        except game.ChangeLevelSet:
            selected = select_levelset()
            if selected != levelset:
                levelset = selected
                load_levels(levelset)
                level = levels.get(levelset, 0)
        else:
            level += 1

