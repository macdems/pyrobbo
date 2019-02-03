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

from . import game, images
from . import screen, background


class Status(object):
    """
    Status data and display
    """
    def __init__(self, level):
        self.level = level
        self.digits = game.images.get_digits()
        # Wczytujemy obrazki
        self.images = {
            'parts':   game.images.get_icon(images.S_PARTS),
            'keys':    game.images.get_icon(images.S_KEYS),
            'bullets': game.images.get_icon(images.S_BULLETS),
            'level': game.images.get_icon(images.S_LEVEL)
        }
        self.top = 432
        screen.blit(self.images['parts'], pygame.Rect(96,self.top, 32,32))
        screen.blit(self.images['keys'], pygame.Rect(224,self.top, 32,32))
        screen.blit(self.images['bullets'], pygame.Rect(352,self.top, 32,32))
        screen.blit(self.images['level'], pygame.Rect(476,self.top, 32,32))
        self.clear()

    def clear(self):
        self.keys = 0
        self.parts = 0
        self.bullets = 0

    def printnum(self, num, pos, dig):
        for i in range(dig-1,-1,-1):
            n = num % 10
            num = num // 10
            rect = pygame.Rect(pos, (16,32)).move((i*16,0))
            screen.blit(background, rect, rect)
            screen.blit(self.digits[n], rect)

    def update(self):
        """Funkcja uaktualnia dane na dole ekranu"""
        scrclip = screen.get_clip()
        screen.set_clip(screen.get_rect())
        self.printnum(self.parts, (128,self.top), 2)
        self.printnum(self.keys, (256,self.top), 2)
        self.printnum(self.bullets, (384,self.top), 2)
        self.printnum(self.level, (512,self.top), 2)
        screen.set_clip(scrclip)