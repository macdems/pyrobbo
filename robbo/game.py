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
import sys

import pygame
from pygame.constants import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_f, K_q, K_x, \
    KEYUP, K_PLUS, K_EQUALS, K_MINUS, KMOD_SHIFT, KMOD_CTRL, KMOD_ALT, KMOD_META

from .defs import *

levels = None
images = None
status = None
board = None
robbo = None
capsule = None
chain = []

from . import screen, screen_rect, clock, clock_speed, sounds
from .board import Board
from .images import Images
from .status import Status

# Register all sprites — do not remove the line below
from .sprites import explode

class EndLevel(Exception):
    """
    End level exception
    """
    pass


def update_sprites():
    # Cleanup old stuff
    for sprite in board.sprites_blast.sprites():
        screen.blit(board.background, sprite.rect, sprite.rect)
    board.sprites_blast.update()
    for sprite in board.sprites_update.sprites():
        screen.blit(board.background, sprite.rect, sprite.rect)
    board.sprites_update.update()


def play_level(level):
    """The game loop"""
    pygame.mouse.set_visible(0)

    global clock_speed

    # Init global game objects
    global images, status, board
    images = Images()

    status = Status(level)
    board = Board()

    screen.set_clip(screen_rect)
    board.init(levels[level])
    status.update()

    scrolling = 0       # are we scrolling?
    scrolldir = 0       # scrolling direction

    # Draw static sprites
    board.sprites.draw(screen)

    # Init updatable sprites
    sprites_robbo = pygame.sprite.RenderPlain(robbo)

    while 1:
        # Check if robbo died and, if so, recreate board
        if not robbo.alive():
            # Wait
            for _ in range(6):
                update_sprites()
                clock.tick(clock_speed)
            # Cleanup board
            sounds.die.play()
            for sprite in board.sprites:
                explode(sprite)
            while board.sprites:
                update_sprites()
                board.sprites_update.draw(screen)
                pygame.display.flip()
                clock.tick(clock_speed)
            # Wait
            for _ in range(6):
                update_sprites()
                clock.tick(clock_speed)
            # Recreate board
            offset = board.scroll_offset[1]
            status.clear()
            board.init(levels[level])
            status.update()
            for sprite in board.sprites.sprites():
                sprite.rect.move_ip(0, offset)
            board.scroll_offset = [0, offset]
            board.rect.move_ip(0, offset)
            board.sprites.draw(screen)
            board.sprites.draw(screen)
            sprites_robbo.add(robbo)

        # Test for chained bombs and trigger them
        global chain
        _chain = chain
        chain = []
        for item in _chain:
            item.chain()

        screen.blit(board.background, robbo.rect, robbo.rect)
        update_sprites()

        # Process user events
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                # Robbo moves
                mods = pygame.key.get_mods()
                if event.key == K_UP:
                    if mods & KMOD_SHIFT:
                        robbo.fire(NORTH)
                    else:
                        robbo.move_key(NORTH)
                elif event.key == K_DOWN:
                    if mods & KMOD_SHIFT:
                        robbo.fire(SOUTH)
                    else:
                        robbo.move_key(SOUTH)
                elif event.key == K_LEFT:
                    if mods & KMOD_SHIFT:
                        robbo.fire(WEST)
                    else:
                        robbo.move_key(WEST)
                elif event.key == K_RIGHT:
                    if mods & KMOD_SHIFT:
                        robbo.fire(EAST)
                    else:
                        robbo.move_key(EAST)
                # system keys
                elif event.key == K_f:
                     pygame.display.toggle_fullscreen()
                elif event.key == K_PLUS or event.key == K_EQUALS:
                    clock_speed *= 1.2
                elif event.key == K_MINUS:
                    clock_speed /= 1.2
                elif event.key == K_x and mods & KMOD_CTRL and not mods & (KMOD_SHIFT | KMOD_ALT | KMOD_META):
                    robbo.die()
                elif event.key == K_q and mods & KMOD_CTRL and not mods & (KMOD_SHIFT | KMOD_ALT | KMOD_META):
                    sys.exit(0)
            elif event.type == KEYUP:
                if event.key == K_UP:
                    if robbo.walking == NORTH: robbo.move_key(STOP)
                elif event.key == K_DOWN:
                    if robbo.walking == SOUTH: robbo.move_key(STOP)
                elif event.key == K_LEFT:
                    if robbo.walking == WEST: robbo.move_key(STOP)
                elif event.key == K_RIGHT:
                    if robbo.walking == EAST: robbo.move_key(STOP)
        pygame.event.pump()

        # Check if scrolling is needed
        if robbo.rect.top < screen_rect.top+64 and board.scroll_offset[1] < 0:
            scrolling = 3; scrolldir = SCROLL_UP
        elif robbo.rect.bottom > screen_rect.bottom-64 and board.rect.bottom > screen_rect.height+32:
            scrolling = 3; scrolldir = SCROLL_DOWN
        elif scrolling:
            if board.scroll_offset[1] < 0 and board.rect.bottom > screen_rect.height+32:
                scrolling -= 1
            else:
                scrolling = 0

        try:
            sprites_robbo.update()
        except EndLevel:
            sounds.finish.play()
            w, h = screen.get_size()
            fade = pygame.Surface((w, h))
            fade.convert()
            fade.fill((0,0,0))
            robbo.kill()
            board.sprites.draw(screen)
            for i in range(w, -1, -1):
                screen.blit(fade, (i, 0))
                clock.tick(300)
                pygame.display.flip()
            return

        if scrolling:
            for n in range(4):
                for sprite in board.sprites.sprites():
                    screen.blit(board.background, sprite.rect, sprite.rect)
                    sprite.rect.move_ip(0, scrolldir)
                board.scroll_offset[1] += scrolldir    # decide current offset
                board.rect.move_ip(0, scrolldir)
                board.sprites.draw(screen)
                pygame.display.flip()
                clock.tick(clock_speed*4)
        else:
            # Draw moving sprites
            sprites_robbo.draw(screen)
            board.sprites_blast.draw(screen)
            board.sprites_update.draw(screen)
            pygame.display.flip()
            clock.tick(clock_speed)

