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
from . import Sprite, BlinkingSprite


@Board.sprite('#')
class Box(Sprite):
    IMAGE = images.BOX
    GROUPS = 'push',


@Board.sprite('b')
class Bomb(Sprite):
    IMAGE = images.BOMB
    GROUPS = 'push', 'shoot'


@Board.sprite('!')
class Capsule(BlinkingSprite):
    IMAGES = images.CAPSULE1, images.CAPSULE2
    UPDATE_TIME = 0
    GROUPS = 'push', 'update'
    
    def __init__(self, pos):
        super(Capsule, self).__init__(pos)
        game.capsule = self

    def activate(self):
        self.UPDATE_TIME = self.update_time = 3


@Board.sprite('T')
class Screw(Sprite):
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
            if game.capsule is not None:
                game.capsule.activate()


@Board.sprite("'")
class Bullet(Sprite):
    IMAGE = images.BULLET
    GROUPS = 'collect',

    def collect(self):
        game.status.bullets += 10
        game.status.update()
        sounds.bullet.play()


@Board.sprite('%')
class Key(Sprite):
    IMAGE = images.KEY
    GROUPS = 'collect',

    def collect(self):
        game.status.keys += 1
        game.status.update()
        sounds.key.play()


@Board.sprite('D')
class Door(Sprite):
    IMAGE = images.DOOR
    GROUPS = 'door',

    def open(self):
        game.status.keys -= 1
        game.status.update()
        sounds.door.play()
