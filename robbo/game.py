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
from pygame.constants import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_f, K_q, KMOD_CTRL, KEYUP

from .defs import *

levels = None
images = None
status = None
board = None
robbo = None


from . import screen, background, area, clock
from .board import Board
from .images import Images
from .status import Status

# Register all sprites — do not remove the line below
from . import sprites

def play(level):
    """The game loop"""
    pygame.mouse.set_visible(0)
    clock_speed = 8

    background.fill((64,64,128), area)
    screen.blit(background,screen.get_rect())

    # Init global game objects
    global images, status, board
    images = Images()
    status = Status()
    board = Board()

    board.init(levels[level-1])
    status.update()

    scrolling = 0       # czy przesuwamy ekran
    scrolldir = 0       # kierunek przesuwania ekranu

    # Inicjujemy ekran gry
    screen.set_clip(area)

    # Rysujemy elementy statyczne
    board.sprites.draw(screen)

    global robbosprite
    robbosprite = pygame.sprite.RenderPlain(robbo)

    # Zmienne pomocnicze
    updatesprites = board.sprites_update

    while 1:

        # Obsługa zdarzeń użytkownika
        for event in pygame.event.get():
            # wyjście z programu
            if event.type == QUIT:
                return
            # naciśnięcie klawisza
            elif event.type == KEYDOWN:
                # Ruchy naszego robocika
                if event.key == K_UP:
                    robbo.moveKey(NORTH)
                elif event.key == K_DOWN:
                    robbo.moveKey(SOUTH)
                elif event.key == K_LEFT:
                    robbo.moveKey(WEST)
                elif event.key == K_RIGHT:
                    robbo.moveKey(EAST)
                # Klawisze systemowe
                elif event.key == K_f:
                     pygame.display.toggle_fullscreen()
                elif event.key == K_q:
                    if pygame.key.get_mods() & KMOD_CTRL: return
            elif event.type == KEYUP:
                if event.key == K_UP:
                    if robbo.walking == NORTH: robbo.moveKey(STOP)
                elif event.key == K_DOWN:
                    if robbo.walking == SOUTH: robbo.moveKey(STOP)
                elif event.key == K_LEFT:
                    if robbo.walking == WEST: robbo.moveKey(STOP)
                elif event.key == K_RIGHT:
                    if robbo.walking == EAST: robbo.moveKey(STOP)
                # Klawisze systemowe
        pygame.event.pump()

        # Sprawdzanie, czy nie trzeba przescrollować
        if robbo.rect.top < area.top+64 and board.scroll_offset[1] < 0:
            scrolling = 3; scrolldir = SCROLL_UP
        elif robbo.rect.bottom > area.bottom-64 and board.rect.bottom > area.height+32:
            scrolling = 3; scrolldir = SCROLL_DOWN
        elif scrolling:
            if board.scroll_offset[1] < 0 and \
               board.rect.bottom > area.height+32:
                scrolling -= 1
            else:
                scrolling = 0

        # Czyszczenie starych rzeczy
        screen.blit(background, robbo.rect, robbo.rect)
        for item in updatesprites.sprites():
            screen.blit(background, item.rect, item.rect)

        # Uaktualnianie spritów ruszających się
        robbosprite.update()
        board.sprites_update.update()

        # Przewijanie
        if scrolling:
            for n in range(4):
                for item in board.sprites.sprites():
                    screen.blit(background, item.rect, item.rect)
                    item.rect.move_ip(0,scrolldir)
                board.scroll_offset[1] += scrolldir    # ustalamy offset planszy
                board.rect.move_ip(0, scrolldir)
                board.sprites.draw(screen)
                pygame.display.flip()
                clock.tick(clock_speed*4)
        else:

            # Rysujemy sprity poruszające się
            #board.dynamicsprites.draw(screen)
            robbosprite.draw(screen)
            updatesprites.draw(screen)

            # Gotowe - pokazujemy obraz
            pygame.display.flip()

            # Ustalamy prędkość gry (8 ramek na sekundę)
            clock.tick(clock_speed)
    #[pętla gry]


