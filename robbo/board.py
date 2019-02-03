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

from . import sounds
from . import game, screen_rect, background, screen


class Board(object):
    """
    Game board

    Holds all static and moving sprites.
    """

    symbols = {}

    class sprite(object):
        """Sprite decorator for automatic symbol registering"""
        def __init__(self, symbols):
            self.symbols = symbols
        def __call__(self, cls):
            for symbol in self.symbols:
                Board.symbols[symbol] = cls
            return cls

    def __init__(self):
        self.sprites = pygame.sprite.RenderPlain()          # all sprites
        self.sprites_static = pygame.sprite.Group()         # walls
        self.sprites_update = pygame.sprite.RenderPlain()   # elements that move or blink
        self.sprites_push = pygame.sprite.Group()           # elements that can be pushed
        self.sprites_collect = pygame.sprite.Group()        # collectibles
        self.sprites_door = pygame.sprite.Group()           # doors (can be open with keys)
        self.sprites_teleport = pygame.sprite.Group()       # teleports
        self.sprites_mob = pygame.sprite.Group()            # mobs
        self.teleports = []
        self.scroll_offset = [0, 0]

    def init(self, level):
        """
        Load and init level data
        """
        self.size = [int(n) for n in level['size'].split('.')]
        self.rect = pygame.Rect(screen_rect.topleft, (32 * self.size[0], 32 * self.size[1]))

        additional = {}

        for item in level['additional'].splitlines()[1:]:
            data = item.split('.')
            p = tuple(int(n) for n in data[:2])
            t = data[2]
            data = [int(n) for n in data[3:]]
            additional.setdefault(t, {})[p] = data

        tgs = {}
        for g, n in additional.get('&', {}).values():
            tgs[g-1] = max(n+1, tgs.get(g-1, 0))
        self.teleports = [[None] * tgs[g] for g in range(len(tgs))]

        for y, row in enumerate(level['data'].splitlines()):
            for x, c in enumerate(row):
                p = x, y
                data = additional.get(c, {}).get(p, ())
                Sprite = self.symbols.get(c)
                if Sprite is not None:
                    sprite = Sprite(p, *data)
                    self.sprites.add(sprite)
                    for group in sprite.GROUPS:
                        try:
                            getattr(self, 'sprites_'+group).add(sprite)
                        except AttributeError:
                            pass

    def move_sprite(self, sprite, step):
        """Przesuwa sprite o dany krok"""
        screen.blit(background, sprite.rect, sprite.rect)
        sprite.rect.move_ip(step)
        screen.blit(sprite.image, sprite.rect)

    def can_move(self, rect, *groups):
        """Check if a sprite can be moved to rect and does not collide with any sprite from the group"""

        # Check we we exit the game area
        if not self.rect.contains(rect):
            return False

        # Check if any sprite from the group blocks us
        if groups:
            for group in groups:
                if rectcollide(rect, getattr(self, 'sprites_'+group)):
                    return False
            return True
        else:
            return not rectcollide(rect, self.sprites)


def rectcollide(rect, group, dokill=0):
    """Check if specified rectangle collides with a group of sprites"""
    crashed = []
    spritecollide = rect.colliderect
    if dokill:
        for s in group.sprites():
            if spritecollide(s.rect):
                s.kill()
                crashed.append(s)
    else:
        for s in group.sprites():
            if spritecollide(s.rect):
                crashed.append(s)
    return crashed
