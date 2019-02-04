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
import pygame

from .. import game, screen, screen_rect, images, sounds
from ..board import Board, rectcollide
from ..defs import *

from . import Sprite, Stars


def hit(rect):
    hits = rectcollide(rect, game.board.sprites)
    if hits:
        for hit in hits:
            if game.board.sprites_hit in hit.groups():
                if hasattr(hit, 'hit'):
                    hit.hit()
                else:
                    sounds.blaster.play()
                    hit.kill()
                    screen.blit(game.board.background, hit.rect, hit.rect)
                    stars = Stars(hit.rect)
                    game.board.sprites.add(stars)
                    game.board.sprites_update.add(stars)
        return True
    else:
        return False


class Blast(pygame.sprite.Sprite):
    """
    Short blast shot by Robbo and guns
    """
    GROUPS = 'update'
    UPDATE_TIME = 1

    def __init__(self, rect, dir):
        super(Blast, self).__init__()
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
    pos = source.rect.move(STEPS[dir])
    if game.board.rect.contains(pos) and not hit(pos):
        blast = Blast(pos, dir)
        game.board.sprites.add(blast)
        game.board.sprites_update.add(blast)
