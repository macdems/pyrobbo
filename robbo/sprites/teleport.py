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

from .. import game, screen, images, sounds
from ..board import Board, rectcollide
from ..defs import *
from . import BlinkingSprite, Stars


@Board.sprite('&')
class Teleport(BlinkingSprite):
    """
    Teleport sprite
    """
    IMAGES = images.TELEPORT1, images.TELEPORT2
    GROUPS = 'teleport', 'update'
    UPDATE_TIME = 3

    def __init__(self, pos, group=None, no=None):
        super(Teleport, self).__init__(pos)
        if group is not None:
            self.group = group-1
            self.no = no
            game.board.teleports[self.group][no] = self
        else:
            self.group = None

    def teleport(self, step):
        """Move Robbo to the target teleport"""

        # Check possible destination
        direct = STEPS.index(step)
        moved = 0
        if self.group is not None:
            target = game.board.teleports[self.group][(self.no+1) % len(game.board.teleports[self.group])]
        else:
            target = None
        for dest in target, self:
            if dest is None:
                warn('Target does not exist. This is probably an error in the level file.')
                continue
            for k in range(4):
                step = STEPS[direct]
                newrect = dest.rect.move(step)
                if game.board.can_move(newrect):
                    moved = 1
                    break
                direct ^= (((k + 1) % 2) + 2)
            if moved: break

        # Create disappear stars
        if moved:
            game.board.add_sprite(Stars(game.robbo.rect))
        # Or make Robbo reappear in the same place
        else:
            step = [0,0]
            dest = game.robbo

        # Move Robbo
        screen.blit(game.board.background, game.robbo.rect, game.robbo.rect)
        game.robbo.rect = dest.rect.move(step)

        # Make appear stars
        game.robbo.spawn()

        # Play sound
        sounds.teleport.play()


