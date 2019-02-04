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

    def __init__(self, rect, dir):
        super(ShortBlast, self).__init__()
        self.dir = dir
        if dir == EAST or dir == WEST:
            self._images = (
                game.images.get_icon(images.BLAST_H1),
                game.images.get_icon(images.BLAST_H2)
            )
        else:
            self._images = (
                game.images.get_icon(images.BLAST_V1),
                game.images.get_icon(images.BLAST_V2)
            )
        self.rect = rect
        self._ci = 0
        self.image = self._images[0]

    def update(self):
        newrect = self.rect.move(STEPS[self.dir])
        if not game.board.rect.contains(newrect) or hit(newrect):
            self.kill()
            return
        self.rect = newrect
        self._ci = 1 - self._ci
        self.image = self._images[self._ci]


def fire_blast(source, dir):
    sounds.shoot.play()
    rect = source.rect.move(STEPS[dir])
    if game.board.rect.contains(rect) and not hit(rect):
        blast = ShortBlast(rect, dir)
        game.board.add_sprite(blast)


@Board.sprite('}')
class Gun(Sprite):
    GROUPS = 'update',
    IMAGES = images.GUN_E, images.GUN_S, images.GUN_W, images.GUN_N

    SHOOT_FREQUENCY = 12

    def __init__(self, pos, facing=None, moving=0, shot_type=0, moves=0, rotates=0, random_rotates=0):
        if facing is None:
            facing = random.randrange(4)
            rotates = 1
            random_rotates = 1
            shot_type = 2
        self.IMAGE = self.IMAGES[facing]
        super(Gun, self).__init__(pos)
        self.facing = facing
        self.shot_type = shot_type
        #TODO: all proper gun types

    def update(self):
        if random.randrange(self.SHOOT_FREQUENCY) == 0:
            fire_blast(self, self.facing)
