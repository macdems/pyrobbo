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

from .. import game, screen, background, screen_rect, images, sounds
from ..board import Board, rectcollide
from ..defs import *


@Board.sprite('R')
class Robbo(pygame.sprite.Sprite):
    """Obiekt naszego robocika"""
    GROUPS = ()

    def __init__(self, pos):
        """Inicjuje wszystko co niezbędne dla naszego robocika"""
        super(Robbo, self).__init__()
        # Inicjujemy obrazki
        self.images = {
            NORTH: (game.images.get_icon(images.ROBBO_N1), game.images.get_icon(images.ROBBO_N2)),
            EAST: (game.images.get_icon(images.ROBBO_E1), game.images.get_icon(images.ROBBO_E2)),
            SOUTH: (game.images.get_icon(images.ROBBO_S1), game.images.get_icon(images.ROBBO_S2)),
            WEST: (game.images.get_icon(images.ROBBO_W1), game.images.get_icon(images.ROBBO_W2))
        }
        self.cur_image = 0
        self.image = self.images[SOUTH][self.cur_image]
        # Obrazki teleportacji
        self.teleportimages =  (game.images.get_icon(images.ROBBO_S1), \
                                game.images.get_icon(images.STARS1), game.images.get_icon(images.STARS1), \
                                game.images.get_icon(images.STARS2), game.images.get_icon(images.STARS2), \
                                game.images.get_icon(images.STARS3), game.images.get_icon(images.STARS3))
        self.stopimages = self.teleportimages

        # Ustalamy pozycję
        self.pos = pos
        self.rect = pygame.Rect(32*pos[0], 32*pos[1], 32, 32).move(screen_rect.topleft)

        # Na początek stoimy
        self.movepos = [0, 0]
        self.walking = STOP

        # Czy nie możemy się ruszać przez ileś rund
        self.stop = 0

        game.robbo = self

    def update(self):
        """Uaktualnienie bieżącego stanu robocika"""

        if self.stop:
            self.stop -= 1
            self.image = self.stopimages[self.stop]
        else:
            newrect = self.rect.move(self.movepos)
            if game.board.canmove(newrect, self.movepos):
                self.rect = newrect

            # zmieniamy obrazek jeżeli Robbo chodzi
            if self.walking != STOP and not self.stop:
                self.cur_image = 1 - self.cur_image
                self.image = self.images[self.walking][self.cur_image]

    def moveKey(self, direct):
        """Obsługa klawiszy ruszania się"""
        self.movepos = [0, 0]
        self.walking = direct
        if direct != STOP: self.movepos = STEPS[direct]
        else: self.movepos = (0,0)