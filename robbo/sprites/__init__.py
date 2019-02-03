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


# Register all sprites
from . import static,  items, teleport, robbo