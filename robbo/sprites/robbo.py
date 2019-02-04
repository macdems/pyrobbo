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

from .. import game, screen, screen_rect, images, sounds
from ..board import Board, rectcollide
from ..defs import *

from . import Stars
from .guns import fire_blast

@Board.sprite('R')
class Robbo(pygame.sprite.Sprite):
    """Obiekt naszego robocika"""
    GROUPS = 'fragile',

    def __init__(self, pos):
        """Inicjuje wszystko co niezbędne dla naszego robocika"""
        super(Robbo, self).__init__()
        # Inicjujemy obrazki
        self.images = {
            NORTH: (game.images.get_icon(images.ROBBO_N1), game.images.get_icon(images.ROBBO_N2)),
            EAST: (game.images.get_icon(images.ROBBO_E1), game.images.get_icon(images.ROBBO_E2)),
            SOUTH: (game.images.get_icon(images.ROBBO_S1), game.images.get_icon(images.ROBBO_S2)),
            WEST: (game.images.get_icon(images.ROBBO_W1), game.images.get_icon(images.ROBBO_W2))
        }
        self._ci = 0
        self.image = self.images[SOUTH][self._ci]

        # Teleport and die _images
        self.spawn_images = (
            game.images.get_icon(images.ROBBO_S1),
            game.images.get_icon(images.STARS1), game.images.get_icon(images.STARS1),
            game.images.get_icon(images.STARS2), game.images.get_icon(images.STARS2),
            game.images.get_icon(images.STARS3), game.images.get_icon(images.STARS3)
        )

        # Initial position and movement
        self.pos = pos
        self.rect = pygame.Rect(32*pos[0], 32*pos[1], 32, 32).move(screen_rect.topleft)
        self.spawn()

        game.robbo = self

    def spawn(self):
        self.step = [0, 0]
        self.walking = STOP
        self._spawning = len(self.spawn_images)

    def update(self):
        """Uaktualnienie bieżącego stanu robocika"""

        if self._spawning:
            self._spawning -= 1
            self.image = self.spawn_images[self._spawning]
        else:
            newrect = self.rect.move(self.step)

            groups = 'static',
            if game.status.keys == 0:
                groups += 'door',

            if game.board.can_move(newrect, *groups):
                move = True

                # Are we pushing?
                pushed = rectcollide(newrect, game.board.sprites_push)
                if pushed:
                    # Capsule is pushable, so we may test it here
                    if game.capsule in pushed and game.capsule.active:
                        raise game.EndLevel()
                    if game.board.can_move(newrect.move(self.step)):
                        self.rect = newrect
                        for sprite in pushed:
                            if hasattr(sprite, 'push'):
                                sprite.push(self.step)
                            game.board.move_sprite(sprite, self.step)
                        sounds.push.play()
                    else:
                        move = False

                # Are we collecting?
                collected = rectcollide(newrect, game.board.sprites_collect)
                if collected:
                    for item in collected:
                        item.collect()
                        screen.blit(game.board.background, item.rect, item.rect)
                        item.kill()

                # Do we open the door?
                # (if we made here, we have at least one key)
                doors = rectcollide(newrect, game.board.sprites_door)
                if doors:
                    for door in doors:
                        door.open()
                        screen.blit(game.board.background, door.rect, door.rect)
                        door.kill()
                    move = False

                # Do we teleport?
                teleports = rectcollide(newrect, game.board.sprites_teleport)
                if teleports:
                    move = False
                    teleports[0].teleport(self.step)

                if move:
                    self.rect = newrect

            # Update image if Robbo is walking
            if self.walking != STOP and not self._spawning:
                self._ci = 1 - self._ci
                self.image = self.images[self.walking][self._ci]

            # Check if we are killed by the mobs
            for step in ((0,0),) + STEPS:
                test = self.rect.move(step)
                if rectcollide(test, game.board.sprites_mob):
                    self.die()

    def move_key(self, direct):
        self.step = [0, 0]
        self.walking = direct
        if direct != STOP:
            self.step = STEPS[direct]
        else:
            self.step = (0, 0)

    def fire(self, dir):
        if game.status.bullets > 0:
            sounds.shoot.play()
            fire_blast(self, dir)
            game.status.bullets -= 1
            game.status.update()

    def hit(self):
        self.die()

    def die(self):
        if self.alive():
            groups = self.groups()
            self.kill()
            game.robbo = DeadRobbo(self.rect)
            for g in groups:
                g.add(game.robbo)
            sounds.die.play()


class DeadRobbo(Stars):
    """
    Just stars but we mock Robbo attributes and methods
    """
    walking = None

    def move_key(self, direct):
        pass

    def fire(self, dir):
        pass

    def hit(self):
        pass

    def die(self):
        pass
