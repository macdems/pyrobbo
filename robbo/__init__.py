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
import shutil
import argparse
import yaml
import pygame

from .defs import *
from .images import available_skins
from .levels import load_level_sets

FLAGS_FULLSCREEN = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
FLAGS_WINDOW = pygame.SCALED | pygame.RESIZABLE

clock = None
clock_speed = None
screen = None
screen_rect = None
skin = 'default'

parser = argparse.ArgumentParser()
parser_screen = parser.add_mutually_exclusive_group()
parser_screen.add_argument('-f', '--fullscreen', help="start in fullscreen", action='store_true')
parser_screen.add_argument('-w', '--window', help="start in window", action='store_true')
parser.add_argument('-s', '--skin', help="selected skin set", type=str)
parser.add_argument("levelset", help="name of the level set to install", nargs='*')


levelset = 'original'

levels = {}


def save():
    from . import game, sounds
    config = {
        'levelset': levelset,
        'levels': levels,
        'cleverbears': game.clever_bears,
        'fullscreen': bool(screen.get_flags() & pygame.FULLSCREEN),
        'skin': skin,
        'mute': sounds.mute,
    }
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as config_file:
        yaml.dump(config, config_file, default_flow_style=False)


def quit():
    save()
    pygame.quit()
    sys.exit(0)


def main():
    args = parser.parse_args()

    try:
        with open(CONFIG_FILE) as config_file:
            config = yaml.safe_load(config_file) or {}
    except FileNotFoundError:
        config = {}

    global skin, levelset, levels, clock, clock_speed, screen, screen_rect
    skins = available_skins()
    if not skins:
        parser.exit(1, "No themes found.\n")
    if args.skin is not None and args.skin not in skins:
        parser.error("unknown skin '{}', choose from {}".format(args.skin, ', '.join(skins)))
    skin = args.skin if args.skin is not None else config.get('skin', 'default')
    if skin not in skins:
        skin = 'default' if 'default' in skins else skins[0]

    if args.fullscreen:
        flags = FLAGS_FULLSCREEN
    elif args.window:
        flags = FLAGS_WINDOW
    else:
        flags = FLAGS_FULLSCREEN if config.get('fullscreen', True) else FLAGS_WINDOW

    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.display.set_caption('PyRobbo')
    pygame.key.set_repeat(0,0)

    clock = pygame.time.Clock()
    clock_speed = 8
    screen = pygame.display.set_mode((640, 480), flags)
    screen_rect = pygame.Rect((64, 32), (512, 384))

    if args.levelset:
        install = [arg for arg in args.levelset if arg.endswith('.dat') and os.path.isfile(arg)]
        if install:
            try:
                user_levels_dir = os.path.join(USER_DATA_DIR, 'levels')
                os.makedirs(user_levels_dir, exist_ok=True)
            except OSError:
                pass
            else:
                for i in install:
                    try:
                        shutil.copy(i, user_levels_dir)
                    except (OSError, IOError):
                        pass
                    else:
                        config['levelset'] = os.path.basename(i)[:-4]

    levels = config.get('levels', {})
    packs = load_level_sets()
    if not packs:
        pygame.quit()
        parser.exit(1, "No playable level sets found.\n")
    levelset = config.get('levelset', levelset)
    if levelset not in packs:
        levelset = 'original' if 'original' in packs else next(iter(packs))

    from . import game, sounds
    from .menu import select_level
    game.clever_bears = config.get('cleverbears', False)
    sounds.mute = config.get('mute', sounds.mute)

    while True:
        levelset, level = select_level(screen, skins, packs, levelset, levels)
        names = sorted(packs)
        while True:
            game.levels = packs[levelset]
            levels[levelset] = level
            save()
            try:
                game.play_level(level)
            except game.SelectLevel as selected:
                if 0 <= selected.level < len(game.levels):
                    level = selected.level
            except game.ChangeLevelSet:
                break
            else:
                level += 1
                if level == len(game.levels):
                    levelset = names[(names.index(levelset) + 1) % len(names)]
                    level = 0
