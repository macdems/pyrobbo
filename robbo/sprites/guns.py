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
import random
import pygame

from .. import game, screen, screen_rect, images, sounds
from ..board import Board, rectcollide
from ..defs import *

from . import Sprite, Stars


def hit(rect):
    hits = rectcollide(rect, game.board.sprites)
    if hits:
        for hit in hits:
            if game.board.sprites_fragile in hit.groups():
                if hasattr(hit, 'hit'):
                    hit.hit()
                else:
                    sounds.blaster.play()
                    hit.kill()
                    screen.blit(game.board.background, hit.rect, hit.rect)
                    game.board.add_sprite(Stars(hit.rect))
        return True
    else:
        return False


class ShortBlast(pygame.sprite.Sprite):
    """
    Short blast shot by Robbo and guns
    """
    GROUPS = 'blast',
    UPDATE_TIME = 1

    def __init__(self, rect, dir, icon=None):
        super(ShortBlast, self).__init__()
        self.dir = dir
        if icon is None:
            if dir == EAST or dir == WEST:
                self._images = game.images.get_icon(images.BLAST_H1), game.images.get_icon(images.BLAST_H2)
            else:
                self._images = game.images.get_icon(images.BLAST_V1), game.images.get_icon(images.BLAST_V2)
            self._ci = 0
            self.image = self._images[0]
        else:
            self._images = None
            self.image = game.images.get_icon(icon)
        self.rect = rect

    def update(self):
        newrect = self.rect.move(STEPS[self.dir])
        if not game.board.rect.contains(newrect) or hit(newrect):
            self.kill()
            return
        self.rect = newrect
        if self._images is not None:
            self._ci = 1 - self._ci
            self.image = self._images[self._ci]


def fire_blast(source, dir, icon=None):
    rect = source.rect.move(STEPS[dir])
    if game.board.rect.contains(rect) and not hit(rect):
        blast = ShortBlast(rect, dir, icon)
        game.board.add_sprite(blast)


class LongBlast(pygame.sprite.Sprite):
    """
    Short blast shot by Robbo and guns
    """
    GROUPS = 'blast',

    END_IMAGES = images.STARS1, images.STARS3, images.STARS1

    def __init__(self, rect, dir, prev):
        super(LongBlast, self).__init__()
        self.dir = dir
        if dir == EAST or dir == WEST:
            self._images = game.images.get_icon(images.BLAST_H1), game.images.get_icon(images.BLAST_H2)
        else:
            self._images = game.images.get_icon(images.BLAST_V1), game.images.get_icon(images.BLAST_V2)
        if isinstance(prev, LongBlast):
            self.ci = prev.ci
        else:
            self.ci = 0
        self.image = self._images[0]
        self.rect = rect
        self._prev = prev
        self._head = True
        self._end = None

    def update(self):
        self.ci = (self.ci + 1) % len(self._images)
        self.image = self._images[self.ci]
        if self._head:
            self._head = False
            game.board.sprites_static.add(self)     # Robbo cannot enter
            newrect = self.rect.move(STEPS[self.dir])
            if not game.board.rect.contains(newrect) or hit(newrect):
                game.chain.append(self)
            else:
                next = LongBlast(newrect, self.dir, self)
                game.board.add_sprite(next)
        elif self._end is not None:
            if self._end == 0:
                self.kill()
                screen.blit(game.board.background, self.rect, self.rect)
                self._prev.blasting = False
            self._end -= 1

    def chain(self):
        if isinstance(self._prev, LongBlast):
            self.kill()
            screen.blit(game.board.background, self.rect, self.rect)
            game.chain.append(self._prev)
        elif isinstance(self._prev, Gun):
            self._images = tuple(game.images.get_icon(i) for i in self.END_IMAGES)
            self.ci = -1
            self._end = len(self.END_IMAGES)


@Board.sprite('}')
class Gun(Sprite):
    GROUPS = 'update',
    IMAGES = images.GUN_E, images.GUN_S, images.GUN_W, images.GUN_N

    SHOOT_FREQUENCY = 12
    ROTATE_FREQUENCY = 12

    BIG_BLAST_ICONS = images.STARS1, images.STARS2, images.STARS3, images.STARS2, images.STARS1

    def __init__(self, pos, facing=None, moving=0, shot_type=0, moves=0, rotates=0, rotates_random=0):
        if facing is None:
            facing = random.randrange(4)
            rotates = 1
            rotates_random = 1
            shot_type = 0
        self.IMAGE = self.IMAGES[facing]
        super(Gun, self).__init__(pos)
        self.facing = facing
        self.shot_type = shot_type
        self.rotates_random = rotates_random
        self.rotates = rotates
        self._to_rotate = self.ROTATE_FREQUENCY
        #TODO: moving gun
        if moves:
            self.GROUPS = Gun.GROUPS + ('push',)
        else:
            self.GROUPS = Gun.GROUPS + ('static',)
        self.blasting = False

    def update(self):
        if self.rotates and not self.blasting:
            if self.rotates_random:
                self._to_rotate = random.randrange(self.ROTATE_FREQUENCY)
            else:
                self._to_rotate -= 1
            if self._to_rotate == 0:
                self._to_rotate = self.ROTATE_FREQUENCY
                twist = -1
                if self.rotates_random and random.randrange(2): twist = 1
                self.facing = (self.facing + twist) % 4
                self.image = game.images.get_icon(self.IMAGES[self.facing])
        if self.shot_type == 2:
            if self.blasting:
                fire_blast(self, self.facing, self.BIG_BLAST_ICONS[self.blasting])
                self.blasting -= 1
            else:
                if random.randrange(self.SHOOT_FREQUENCY) == 0:
                    fire_blast(self, self.facing, self.BIG_BLAST_ICONS[-1])
                    self.blasting = len(self.BIG_BLAST_ICONS) - 1
        if self.shot_type == 1:
            if not self.blasting and random.randrange(self.SHOOT_FREQUENCY) == 0:
                rect = self.rect.move(STEPS[self.facing])
                if game.board.rect.contains(rect) and not hit(rect):
                    game.board.add_sprite(LongBlast(rect, self.facing, self))
                    self.blasting = True
        elif random.randrange(self.SHOOT_FREQUENCY) == 0:
            fire_blast(self, self.facing)
