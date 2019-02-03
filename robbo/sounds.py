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
from zipfile import ZipFile
from io import BytesIO
import pygame

with ZipFile("sounds.dat", 'r') as zipf:
    screw = pygame.mixer.Sound(BytesIO(zipf.read("screw.wav")))
    lastscrew = pygame.mixer.Sound(BytesIO(zipf.read("lastscrew.wav")))
    push = pygame.mixer.Sound(BytesIO(zipf.read("push.wav")))
    door = pygame.mixer.Sound(BytesIO(zipf.read("door.wav")))
    key = pygame.mixer.Sound(BytesIO(zipf.read("key.wav")))
    teleport = pygame.mixer.Sound(BytesIO(zipf.read("teleport.wav")))
