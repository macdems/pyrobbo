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
import os
import pygame


MAGNET_R = 0
MAGNET_L = 1
WALL_GRAY = 2
WALL_RED = 3
SCREW = 4
BULLET = 5
BOX = 6
KEY = 7
BOMB = 8
DOOR = 9
QUESTION = 10
BEAR1 = 11
BEAR2 = 12
BIRD1 = 13
BIRD2 = 14
CAPSULE1 = 15
CAPSULE2 = 16
VOID = 17
BOX_SLIDE = 18
LIFE = 20
STARS1 = 21
STARS2 = 22
STARS3 = 23
GRASS = 24
WALL_GREEN = 25
DEVIL1 = 26
DEVIL2 = 27
BLAST_H1 = 30
BLAST_H2 = 31
BLAST_V1 = 32
BLAST_V2 = 33
S_PARTS = 34
S_LIFES = 35
S_KEYS = 36
S_BULLETS = 37
S_LEVEL = 38
TELEPORT1 = 40
TELEPORT2 = 41
ROBBO_E1 = 50
ROBBO_E2 = 51
ROBBO_S1 = 52
ROBBO_S2 = 53
ROBBO_W1 = 54
ROBBO_W2 = 55
ROBBO_N1 = 56
ROBBO_N2 = 57

# 0 - magnes prawo, 1 - magnes lewo, 2 - szara i 3 - czerwona ściana,
# 4 - śrubka, 5 - nabój, 6 - krata, 7 - klucz, 8 - bomba, 9 - drzwi,
# 10 - ?, 11,12 - miś, 13,14 - ptak, 15,16 - kapsuła, 17 - pustka,
# 18 - krata ślizowa, 20 - życie, 21,22,23 - zniknięcie, 24 - trawa,
# 25 - zielona ściana, 26,27 - diabełek, 28,29 - oczy,
# 30,31 - strzał poziomy i 32,33 - pionowy, 34 - śrubek, 35 - życia,
# 36 - kluczy, 37 - strzałów, 38 - poziom, 39 - bariera1,
# 40,41 - teleport, 42,43,44 - gruby strzał, 45,46,47,48 - działko,
# 49 - bariera, 50,51 - Robbo E, 52,53 - Robbo S, 54,55 - Robbo W,
# 56,57 - Robbo N
# 18 - krata ślizowa, 20 - życie, 21,22,23 - zniknięcie, 24 - trawa,
# 25 - zielona ściana, 26,27 - diabełek, 28,29 - oczy,
# 30,31 - strzał poziomy i 32,33 - pionowy, 39 - bariera1,
# 40,41 - teleport, 42,43,44 - gruby strzał, 45,46,47,48 - działko,
# 49 - bariera2,


class Images(object):
    """
    Class responsible for visuals managements

    Unlike sounds this is kept in class, so multiple skin pack can be selected.
    """

    def __init__(self, skin='default'):
        self.image = pygame.image.load(os.path.join('skins', skin, 'icons.png')).convert_alpha()
        self.digits = pygame.image.load(os.path.join('skins', skin, 'digits.png')).convert_alpha()

    def _get_icon_rect(self, n):
        """
        Get icon location in the skin image
        """
        return pygame.Rect(34*(n%10)+2, 34*(n//10)+2, 32, 32)

    def get_icon(self, n):
        """Funkcja zwraca obrazek o danym numerze"""
        rect = pygame.Rect(0,0, 32,32)
        img = pygame.Surface((32,32)).convert_alpha()
        img.fill((0,0,0,0))
        img.blit(self.image, rect, self._get_icon_rect(n))
        return img

    def _get_digit_rect(self, n):
        """Funkcja zwraca rect danej cyfry"""
        return pygame.Rect(18*n,0,16,32)

    def get_digits(self):
        """Funkcja zwraca tablicę zawierającą dane cyfry"""
        digits = []
        rect = pygame.Rect(0,0, 16,32)
        for n in range(10):
            img = pygame.Surface((16,32)).convert_alpha()
            img.fill((0,0,0,0))
            img.blit(self.digits, rect, self._get_digit_rect(n))
            digits.append(img)
        return digits
