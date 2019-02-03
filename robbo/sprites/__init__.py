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

from .. import game, screen_rect


class Sprite(pygame.sprite.Sprite):
    IMAGE = None

    def __init__(self, pos):
        super(Sprite, self).__init__()
        if self.IMAGE is not None:
            self.image = game.images.get_icon(self.IMAGE)
        self.rect = pygame.Rect(32*pos[0], 32*pos[1], 32, 32).move(screen_rect.topleft)


class BlinkingSprite(Sprite):
    """
    Sprite with multiple images
    """
    GROUPS = 'update',
    IMAGES = None

    UPDATE_TIME = 1  # update frequency

    def __init__(self, pos):
        super(BlinkingSprite, self).__init__(pos)
        if self.IMAGES is not None:
            self._images = tuple(game.images.get_icon(icon) for icon in self.IMAGES)
            self._imageno = 0
            self.image = self._images[0]
            self.update_time = self.UPDATE_TIME

    def update(self):
        """
        Update image state

        Return value can be used by subclasses to do their own update.
        """
        if self.UPDATE_TIME:
            self.update_time -= 1
            if not self.update_time:
                self.update_time = self.UPDATE_TIME
                self._imageno = (self._imageno + 1) % len(self.IMAGES)
                self.image = self._images[self._imageno]
                return True
            return False


# Register all sprites
from . import static,  items, mobs, teleport, robbo