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

from .. import game, screen, background, screen_rect, images, sounds
from ..board import Board, rectcollide
from ..defs import *
from . import BlinkingSprite


class Mob(BlinkingSprite):
    GROUPS = 'mob', 'update'
    UPDATE_TIME = 3

    def __init__(self, pos, direction=0):
        super(Mob, self).__init__(pos)
        self.direction = direction

    def try_move(self):
        step = STEPS[self.direction]
        newrect = self.rect.move(step)
        if game.board.can_move(newrect):
            self.rect = newrect
            return True
        return False

    def move(self):
        pass

    def update(self):
        super(Mob, self).update()
        self.move()


@Board.sprite('^')
class Bird(Mob):
    IMAGES = images.BIRD1, images.BIRD2

    def __init__(self, pos, direction=0, shooting_dir=0, shooting=0):
        super(Bird, self).__init__(pos, SOUTH if direction else EAST)
        self.shooting = shooting
        self.shooting_dir = shooting_dir

    def move(self):
        if not self.try_move():
            self.direction = (self.direction + 2) % 4
            self.try_move()


@Board.sprite('@')
class Bear(Mob):
    IMAGES = images.BEAR1, images.BEAR2

    def move(self):
        self.direction = (self.direction - 1) % 4
        for _ in range(4):
            if self.try_move(): break
            self.direction = (self.direction + 1) % 4


@Board.sprite('*')
class Devil(Mob):
    IMAGES = images.DEVIL1, images.DEVIL2

    def move(self):
        self.direction = (self.direction + 1) % 4
        for _ in range(4):
            if self.try_move(): break
            self.direction = (self.direction - 1) % 4
