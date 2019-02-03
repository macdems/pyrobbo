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
from copy import copy

import pygame

from . import game, images as img
from . import screen, background


class Status(object):
    """Klasa zawiera informacje o stanie posiadania naszego Robbo
       (ilość żyć, brakujące śrubki, ilość kluczy itp.)
       Ponadto klasa uaktualnia dane na dole ekranu"""
    def __init__(self):
        self.keys = 0
        self.parts = 0
        self.level = 1
        self.bullets = 0
        self.digits = game.images.get_digits()
        # Wczytujemy obrazki
        self.images = {
            'parts': game.images.get_icon(img.S_PARTS),
            'keys':  game.images.get_icon(img.S_KEYS),
        }
        self.top = 432
        screen.blit(self.images['parts'], pygame.Rect(162,self.top, 32,32))
        screen.blit(self.images['keys'], pygame.Rect(368,self.top, 32,32))

    def printnum(self, num, pos, dig):
        nr = copy(num)
        for i in range(dig-1,-1,-1):
            n = nr % (10**i)
            nr = nr // (10**i)
            rect = pygame.Rect(pos, (16,32)).move((i*16,0))
            screen.blit(background, rect, rect)
            screen.blit(self.digits[n], rect)

    def update(self):
        """Funkcja uaktualnia dane na dole ekranu"""
        scrclip = screen.get_clip()
        screen.set_clip(screen.get_rect())
        self.printnum(self.parts, (194,self.top), 2)
        self.printnum(self.keys, (400,self.top), 2)
        screen.set_clip(scrclip)