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
from warnings import warn
import pygame

from .. import game, screen, background, screen_rect, images, sounds
from ..board import Board, rectcollide
from ..defs import *
from . import BlinkingSprite


@Board.sprite('&')
class Teleport(BlinkingSprite):
    """
    Teleport sprite
    """
    IMAGES = images.TELEPORT1, images.TELEPORT2
    GROUPS = 'teleport', 'update'
    UPDATE_TIME = 3

    def __init__(self, pos, group, no):
        super(Teleport, self).__init__(pos)
        self.group = group-1
        self.no = no
        game.board.teleports[self.group][no] = self

    def teleport(self, step):
        """Move Robbo to the target teleport"""

        # Check possible destination
        direct = STEPS.index(step)
        moved = 0
        target = game.board.teleports[self.group][(self.no+1) % len(game.board.teleports[self.group])]
        for dest in target, self:
            if dest is None:
                warn('Target does not exist. This is probably an error in the level file.')
                continue
            for n in range(4):
                step = STEPS[direct]
                new = dest.rect.move(step)
                if game.board.rect.contains(new) and not rectcollide(new, game.board.sprites):
                    moved = 1
                    break
                direct = (direct - 1) % 4
            if moved: break

        # Create disappear stars
        if moved:
            stars = Stars(game.robbo.rect)
            game.board.sprites.add(stars)
            game.board.sprites_update.add(stars)
        # Or make Robbo reappear in the same place
        else:
            step = [0,0]
            dest = game.robbo

        # Move Robbo
        screen.blit(background, game.robbo.rect, game.robbo.rect)
        game.robbo.rect = dest.rect.move(step)

        # Make appear stars
        game.robbo.spawn()

        # Play sound
        sounds.teleport.play()


class Stars(pygame.sprite.Sprite):
    """
    Teleport and die stars
    """
    GROUPS = 'update',
    UPDATE_TIME = 1

    def __init__(self, pos):
        super(Stars, self).__init__()
        self.images = (
            game.images.get_icon(images.STARS3),
            game.images.get_icon(images.STARS2),
            game.images.get_icon(images.STARS1))
        self.rect = pos
        self._todie = len(self.images) * self.UPDATE_TIME
        self.image = self.images[-1]

    def update(self):
        self._todie -= 1
        if self._todie % self.UPDATE_TIME == 0:
            if self._todie:
                self.image = self.images[self._todie//self.UPDATE_TIME-1]
            else:
                self.kill()
