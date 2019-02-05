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
from . import BlinkingSprite

from .guns import fire_blast


class Mob(BlinkingSprite):
    GROUPS = 'mob', 'update', 'fragile'
    UPDATE_TIME = 3

    def __init__(self, pos, dir=0):
        super(Mob, self).__init__(pos)
        self.dir = dir

    def try_step(self, step):
        newrect = self.rect.move(step)
        if rectcollide(newrect, game.board.sprites_blast):
            return True
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

    SHOOT_FREQUENCY = 6

    def __init__(self, pos, dir=0, shooting_dir=0, shooting=0):
        super(Bird, self).__init__(pos, SOUTH if dir else WEST)
        self.shooting = shooting
        self.shooting_dir = shooting_dir

    def move(self):
        if not self.try_step(STEPS[self.dir]):
            self.dir = (self.dir + 2) % 4
            self.try_step(STEPS[self.dir])
        if self.shooting:
            if random.randrange(self.SHOOT_FREQUENCY) == 0:
                fire_blast(self, self.shooting_dir)


@Board.sprite('@')
class Bear(Mob):
    IMAGES = images.BEAR1, images.BEAR2

    def move(self):
        self.dir = (self.dir - 1) % 4
        for _ in range(4):
            if self.try_step(STEPS[self.dir]): break
            self.dir = (self.dir + 1) % 4


@Board.sprite('*')
class Devil(Mob):
    IMAGES = images.DEVIL1, images.DEVIL2

    def move(self):
        self.dir = (self.dir + 1) % 4
        for _ in range(4):
            if self.try_step(STEPS[self.dir]): break
            self.dir = (self.dir - 1) % 4


@Board.sprite('V')
class Eyes(Mob):
    IMAGES = images.BUTTERFLY1, images.BUTTERFLY2

    HUNT_PROBABILITY = 0.8

    def move(self):
        if random.random() < self.HUNT_PROBABILITY:
            # Head for the Robbo
            x0, y0 = self. rect.topleft
            x1, y1 = game.robbo.rect.topleft
            dx, dy = x1 - x0, y1 - y0
            i = 0 if abs(dx) > abs(dy) else 1
            dx = -32 if dx < 0 else 32 if dx > 0 else 0
            dy = -32 if dy < 0 else 32 if dy > 0 else 0
            steps = ((0, dy), (dx, 0)) if i else ((dx, 0), (0, dy))
            if random.randrange(3) == 0:
                steps = reversed(steps)
        else:
            # Random move
            steps = [STEPS[n] for n in (NORTH, SOUTH, EAST, WEST)] + [None]
            random.shuffle(steps)
        for step in steps:
            if step is None or self.try_step(step):
                break

