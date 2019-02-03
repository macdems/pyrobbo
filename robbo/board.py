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

    fields = {}

    class sprite(object):
        def __init__(self, symbols):
            self.symbols = symbols
        def __call__(self, cls):
            for symbol in self.symbols:
                Board.fields[symbol] = cls
            return cls

    def __init__(self):
        """Inicjuje planszę i rozmieszcza sprity"""

        # Przygotowujemy miejsce na sprity i elementy
        self.sprites = pygame.sprite.RenderPlain()          # all sprites
        self.sprites_static = pygame.sprite.Group()         # walls
        self.sprites_update = pygame.sprite.RenderPlain()   # elements that move or blink
        self.sprites_push = pygame.sprite.Group()           # elements that can be pushed
        self.sprites_collect = pygame.sprite.Group()        # collectibles
        self.sprites_door = pygame.sprite.Group()           # doors (can be open with keys)
        self.sprites_teleport = pygame.sprite.Group()       # teleports

        # Teleporty
        self.teleports = []

        # Przesunięcie obszaru gry
        self.scroll_offset = [0, 0]

    def init(self, level):
        # Tutaj inicjujemy obszar.
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
                Sprite = self.fields.get(c)
                if Sprite is not None:
                    sprite = Sprite(p, *data)
                    self.sprites.add(sprite)
                    for group in sprite.GROUPS:
                        try:
                            getattr(self, 'sprites_'+group).add(sprite)
                        except AttributeError:
                            pass

    def movesprite(self, sprite, step):
        """Przesuwa sprite o dany krok"""
        screen.blit(background, sprite.rect, sprite.rect)
        sprite.rect.move_ip(step)
        screen.blit(sprite.image, sprite.rect)

    def canmove(self, rect, step):
        """Sprawdza czy da się przejść na daną pozycję
           jednocześnie przesuwa obiekty popychane i teleportuje Robbo"""
        global screen, background

        # Czy nie wypadamy za krawędzie
        if not self.rect.contains(rect):
            return 0
        # Czy nie blokuje nas coś nieruchomego
        if rectcollide(rect, self.sprites_static):
            return 0
        # Czy coś może popchniemy
        thelist = rectcollide(rect, self.sprites_push)
        if thelist:
            if rectcollide(rect.move(step), self.sprites): return 0
            else:
                for sprite in thelist:
                    self.movesprite(sprite, step)
                sounds.push.play()
                return 1
        # Czy coś bierzemy
        thelist = rectcollide(rect, self.sprites_collect)
        if thelist:
            for item in thelist:
                item.collect()
                screen.blit(background, item.rect, item.rect)
                item.kill()
            return 1
        # Czy trafiliśmy na drzwi
        thelist = rectcollide(rect, self.sprites_door)
        if thelist:
            if game.status.keys > 0:
                for door in thelist:
                    door.open()
                    screen.blit(background, door.rect, door.rect)
                    door.kill()
                return 0
            else:
                return 0
        # Do we teleport?
        thelist = rectcollide(rect, self.sprites_teleport)
        if thelist:
            thelist[0].teleport(step)
            return 0

        return 1


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
