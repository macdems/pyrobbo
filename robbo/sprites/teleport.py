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
from . import Sprite


@Board.sprite('&')
class Teleport(Sprite):
    """Klasa zawierająca teleport"""
    GROUPS = 'teleport', 'update'

    UPDATE_TIME = 3  # update frequency

    def __init__(self, pos, group, no):
        """Inicjuje sprite i dodaje do listy w board"""
        super(Teleport, self).__init__(pos)
        self.images = (game.images.get_icon(images.TELEPORT1), game.images.get_icon(images.TELEPORT2))
        self._cur_image = 0
        self.image = self.images[0]
        self.rect = pygame.Rect(32*pos[0], 32*pos[1], 32, 32).move(screen_rect.topleft)
        self._toupdate = self.UPDATE_TIME    # Czas do zmiany obrazka
        self.group = group-1                # Grupa teleportów
        self.no = no                        # Numer teleportu
        game.board.teleports[self.group][no] = self

    def update(self):
        """Funkcja uaktualnia stan teleportu (czyli zmienia obrazek)"""
        self._toupdate -= 1
        if not self._toupdate:
            self._toupdate = self.UPDATE_TIME
            self._cur_image = 1 - self._cur_image
            self.image = self.images[self._cur_image]

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
                direct = (direct + 1) % 4
            if moved: break
        # Tworzymy gwiazdki znikające
        if moved:
            stars = Stars(game.robbo.rect)
            game.board.sprites.add(stars)
            game.board.sprites_update.add(stars)
        # Albo ustalamy, że Robbo się pojawia w tym samym miejscu
        else:
            step = [0,0]
            dest = game.robbo
        # Przenosimy obrazek
        screen.blit(background, game.robbo.rect, game.robbo.rect)
        game.robbo.rect = dest.rect.move(step)

        # Ustalamy gwiazdki pojawiania się
        game.robbo.stopimages = game.robbo.teleportimages
        game.robbo.stop = 6
        game.robbo.image = game.robbo.stopimages[6]

        # Gramy dźwięk
        sounds.teleport.play()


class Stars(pygame.sprite.Sprite):
    """Klasa gwiazdki gdy się robbo teleportuje"""
    GROUPS = 'update',

    def __init__(self, pos):
        """Inicjuje sprite i dodaje do listy w board"""

        super(Stars, self).__init__()

        self.images = (
            game.images.get_icon(images.STARS3), game.images.get_icon(images.STARS3),
            game.images.get_icon(images.STARS2), game.images.get_icon(images.STARS2),
            game.images.get_icon(images.STARS1), game.images.get_icon(images.STARS1))
        self.rect = pos
        self._todie = 6
        self.image = self.images[self._todie - 1]

    def update(self):
        """Funkcja wywoływana cyklicznie"""
        self._todie -= 1
        if self._todie:
            self.image = self.images[self._todie]
        else:
            self.kill()
