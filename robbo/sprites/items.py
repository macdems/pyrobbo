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

from .. import game, images, sounds
from ..board import Board
from . import Sprite


@Board.sprite('#')
class Box(Sprite):
    """Klasa zawierająca przesuwaną skrzynkę"""
    IMAGE = images.BOX
    GROUPS = 'push',


@Board.sprite('b')
class Bomb(Sprite):
    """Klasa zawierająca bombę"""
    IMAGE = images.BOMB
    GROUPS = 'push',


@Board.sprite('T')
class Screw(Sprite):
    """Klasa zawierająca śrubkę"""
    IMAGE = images.SCREW
    GROUPS = 'collect',

    def __init__(self, pos):
        """Inicjuje sprite i dodaje do listy w board"""
        super(Screw, self).__init__(pos)
        game.status.parts += 1

    def collect(self):
        """Funkcja wywoływana przy zebraniu klucza"""
        game.status.parts -= 1
        game.status.update()
        # Gramy dźwięk
        sounds.screw.play()
        if game.status.parts == 0:
            sounds.lastscrew.play()


@Board.sprite('%')
class Key(Sprite):
    """Klasa zawierająca klucz do drzwi"""
    IMAGE = images.KEY
    GROUPS = 'collect',

    def collect(self):
        """Funkcja wywoływana przy zebraniu klucza"""
        game.status.keys += 1
        game.status.update()
        # Gramy dźwięk
        sounds.key.play()


@Board.sprite('D')
class Door(Sprite):
    """Klasa zawierająca drzwi"""
    IMAGE = images.DOOR
    GROUPS = 'door',

    def open(self):
        """Funkcja wywoływana przy użyciu klucza"""
        game.status.keys -= 1
        game.status.update()
        # Gramy dźwięk
        sounds.door.play()