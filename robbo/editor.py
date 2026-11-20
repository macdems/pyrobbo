"""Mouse-driven level editor using the game's logical display and current skin."""
from collections import deque
from copy import deepcopy
import re

import pygame

import robbo as main
from . import images
from .level_document import Level, LevelSet, check_name
from .levels import read_level_source
from .menu import BACKGROUND, EDGE, GOLD, MUTED, PANEL, TEXT, preview_tiles

CELL = 24
CANVAS = pygame.Rect(14, 120, 16 * CELL, 12 * CELL)
PALETTE = {
    '.': 'Empty', 'O': 'Stone wall', 'Q': 'Brick wall', '-': 'Void', 'H': 'Grass', 'R': 'Robbo',
    '!': 'Capsule', 'T': 'Screw', '%': 'Key', 'D': 'Door', "'": 'Ammunition', '#': 'Box',
    '~': 'Sliding box', 'b': 'Bomb', '?': 'Surprise', '&': 'Teleport', 'M': 'Magnet', '}': 'Gun',
    '@': 'Bear', '*': 'Black bear', '^': 'Bird', 'V': 'Butterfly', '=': 'Force field',
    'L': 'Horizontal blast', 'l': 'Vertical blast',
}
DIRECTIONS = ('East', 'South', 'West', 'North')
HORIZONTAL = ('East', 'West')
VERTICAL = ('South', 'North')
SWITCH = ('Off', 'On')
OPTIONS = {
    '@': [('Facing', DIRECTIONS)], '*': [('Facing', DIRECTIONS)],
    '^': [('Movement', DIRECTIONS), ('Fire direction', DIRECTIONS), ('Fires', SWITCH)],
    '}': [('Facing', DIRECTIONS), ('Movement', DIRECTIONS), ('Shot', ('Bullet', 'Laser', 'Blaster')),
          ('Moves', SWITCH), ('Rotates', SWITCH), ('Random rotation', SWITCH)],
    'M': [('Facing', HORIZONTAL)], '=': [('Movement', HORIZONTAL)],
    'L': [('Movement', HORIZONTAL)], 'l': [('Movement', VERTICAL)], '&': [('Link group', ())],
}


def field(label, value, choices=()):
    return (label, str(value), choices)


class Dialog:
    """A small form. Choice fields cycle, text fields accept pygame text input."""
    def __init__(self, title, fields, submit, accept, hint=''):
        self.title, self.fields, self.submit, self.accept = title, fields, submit, accept
        self.values = [value for _, value, _ in fields]
        self.hint = hint
        self.focus(0)
        self.error = ''
        height = 138 + 41 * len(fields)
        self.box = pygame.Rect(66, (480 - height) // 2, 508, height)
        self.inputs = [pygame.Rect(292, self.box.y + 52 + 41 * i, 262, 32) for i in range(len(fields))]
        self.ok = pygame.Rect(428, self.box.bottom - 42, 126, 30)
        self.cancel = self.ok.move(-136, 0)

    def focus(self, index):
        self.active = index
        self.cursor = len(self.values[index]) if self.values else 0
        self.replace = True

    def draw(self, ui):
        overlay = pygame.Surface(ui.page.get_size(), pygame.SRCALPHA)
        overlay.fill((5, 9, 15, 205))
        ui.page.blit(overlay, (0, 0))
        pygame.draw.rect(ui.page, PANEL, self.box)
        pygame.draw.rect(ui.page, EDGE, self.box, 1)
        ui.text(self.title, (self.box.x + 18, self.box.y + 12), font=ui.heading)
        for i, (label, _, choices) in enumerate(self.fields):
            rect = self.inputs[i]
            ui.text(label, (self.box.x + 18, rect.y + 7), limit=201)
            value = self.values[i]
            if choices:
                ui.button(rect, '<   ' + value + '   >', active=i == self.active)
            else:
                pygame.draw.rect(ui.page, BACKGROUND, rect)
                pygame.draw.rect(ui.page, GOLD if i == self.active else EDGE, rect, 1)
                cursor = self.cursor if i == self.active else len(value)
                prefix = value[:cursor]
                while prefix and ui.font.size(prefix)[0] > rect.w - 18:
                    prefix = prefix[1:]
                value = prefix + value[cursor:]
                width = min(rect.w - 16, ui.font.size(value)[0])
                if i == self.active:
                    if self.replace:
                        pygame.draw.rect(ui.page, EDGE, (rect.x + 7, rect.y + 5, width, rect.h - 10))
                    else:
                        x = rect.x + 8 + ui.font.size(prefix)[0]
                        pygame.draw.line(ui.page, GOLD, (x, rect.y + 6), (x, rect.bottom - 6))
                ui.text(value, (rect.x + 7, rect.y + 8), limit=rect.w-14)
        ui.text(self.error or self.hint, (self.box.x + 18, self.box.bottom - 69),
                GOLD if self.error else MUTED, limit=self.box.width - 36)
        ui.button(self.cancel, 'Cancel')
        ui.button(self.ok, self.accept, active=True)

    def cycle(self, step):
        choices = self.fields[self.active][2]
        value = self.values[self.active]
        self.values[self.active] = choices[(choices.index(value) + step) % len(choices)]

    def handle(self, ui, event, pos):
        accept = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.cancel.collidepoint(pos):
                ui.close_dialog()
            elif self.ok.collidepoint(pos):
                accept = True
            for i, rect in enumerate(self.inputs):
                if rect.collidepoint(pos):
                    self.focus(i)
                    if self.fields[i][2]:
                        self.cycle(-1 if pos[0] < rect.centerx else 1)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                ui.close_dialog()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                accept = True
            elif self.fields:
                choices = self.fields[self.active][2]
                if event.key == pygame.K_TAB:
                    step = -1 if event.mod & pygame.KMOD_SHIFT else 1
                    self.focus((self.active + step) % len(self.fields))
                elif choices and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self.cycle(1 if event.key == pygame.K_RIGHT else -1)
                elif event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                    self.replace = True
                elif not choices:
                    value = self.values[self.active]
                    if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                        start = max(0, self.cursor - int(event.key == pygame.K_BACKSPACE))
                        end = self.cursor + int(event.key == pygame.K_DELETE)
                        self.values[self.active] = '' if self.replace else value[:start] + value[end:]
                        self.cursor = 0 if self.replace else start
                    elif event.key == pygame.K_HOME:
                        self.cursor = 0
                    elif event.key == pygame.K_END:
                        self.cursor = len(value)
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        step = 1 if event.key == pygame.K_RIGHT else -1
                        self.cursor = max(0, min(len(value), self.cursor + step))
                    else:
                        return
                    self.replace = False
        elif event.type == pygame.TEXTINPUT and self.fields and not self.fields[self.active][2]:
            value = '' if self.replace else self.values[self.active]
            cursor = 0 if self.replace else self.cursor
            self.values[self.active] = value[:cursor] + event.text + value[cursor:]
            self.cursor = cursor + len(event.text)
            self.replace = False
        if accept:
            try:
                self.submit(*self.values)
            except (ValueError, OSError) as err:
                self.error = str(err)
            else:
                if ui.dialog is self:
                    ui.close_dialog()


class LevelEditor:
    def __init__(self, screen, packs, name, index):
        self.screen = screen
        self.page = pygame.Surface((640, 480)).convert()
        self.viewport = self.page.get_rect().fit(screen.get_rect())
        self.font = pygame.font.Font(None, 21)
        self.heading = pygame.font.Font(None, 32)
        self.packs = packs
        self.last_saved = name, index
        self.history = deque(maxlen=40)
        self.dialog = None
        self.finished = False
        self.brush, self.args = 'O', ()
        skin = images.Images(main.skin)
        self.icons = preview_tiles(skin, CELL)
        self.guns = [pygame.transform.scale(skin.get_icon(i), (CELL, CELL))
                     for i in (images.GUN_E, images.GUN_S, images.GUN_W, images.GUN_N)]
        self.left_magnet = pygame.transform.scale(skin.get_icon(images.MAGNET_L), (CELL, CELL))
        self.swatches = {s: pygame.Rect(414 + i % 6 * 35, 143 + i // 6 * 32, 32, 30)
                         for i, s in enumerate(PALETTE)}
        self.buttons = [
            ((262, 12, 84, 32), 'New set', self.new_set),
            ((352, 12, 84, 32), 'Save as', self.save_as),
            ((442, 12, 82, 32), 'Save', self.save),
            ((530, 12, 96, 32), 'Done', self.done),
            ((14, 69, 185, 32), '', self.open_set),
            ((215, 69, 32, 32), '<', lambda: self.navigate(-1)),
            ((348, 69, 32, 32), '>', lambda: self.navigate(1)),
            ((398, 69, 76, 32), '+ Level', lambda: self.add(False)),
            ((480, 69, 63, 32), 'Copy', lambda: self.add(True)),
            ((549, 69, 77, 32), 'Remove', self.remove),
            ((414, 333, 212, 28), 'Tile options', self.tile_options),
            ((414, 371, 212, 30), 'Board settings', self.settings),
            ((414, 410, 212, 28), 'Undo', self.undo),
        ]
        for i, (label, delta) in enumerate((('<', (-1, 0)), ('>', (1, 0)), ('Up', (0, -2)), ('Down', (0, 2)))):
            self.buttons.append(((14 + i * 50, 414, 48, 26), label, lambda d=delta: self.pan(*d)))
        self.load(LevelSet(name, read_level_source(name)), index)

    def load(self, doc, index):
        self.doc, self.index = doc, min(index, len(doc.levels) - 1)
        self.history.clear()
        self.dirty = doc.original is None
        self.offset = [0, 0]
        self.stroke = None
        self.hover = None
        self.message = ''

    @property
    def level(self):
        return self.doc.levels[self.index]

    def text(self, value, pos, color=TEXT, font=None, limit=None):
        font = font or self.font
        if limit and font.size(value)[0] > limit:
            while value and font.size(value + '…')[0] > limit:
                value = value[:-1]
            value += '…'
        self.page.blit(font.render(value, True, color), pos)

    def button(self, rect, label, active=False, enabled=True):
        rect = pygame.Rect(rect)
        pygame.draw.rect(self.page, PANEL, rect)
        pygame.draw.rect(self.page, GOLD if active else EDGE, rect, 2 if active else 1)
        if self.font.size(label)[0] > rect.width - 8:
            while label and self.font.size(label + '…')[0] > rect.width - 8:
                label = label[:-1]
            label += '…'
        text = self.font.render(label, True, (GOLD if active else TEXT) if enabled else EDGE)
        self.page.blit(text, text.get_rect(center=rect.center))

    def icon(self, symbol, args, rect):
        tile = self.icons.get(symbol)
        if symbol == '}' and args and args[0] in range(4):
            tile = self.guns[args[0]]
        elif symbol == 'M' and args and args[0] == 2:
            tile = self.left_magnet
        if tile:
            self.page.blit(tile, tile.get_rect(center=rect.center))
        elif symbol != '.':
            self.text(symbol, rect.topleft)

    def draw(self):
        self.page.fill(BACKGROUND)
        self.text('Level editor', (14, 14), font=self.heading)
        self.text('LEVEL SET' + ('   * unsaved' if self.dirty else ''), (14, 51), GOLD if self.dirty else MUTED)
        self.text('LEVEL', (255, 51), MUTED)
        number = '{} / {}'.format(self.index + 1, len(self.doc.levels))
        image = self.font.render(number, True, TEXT)
        self.page.blit(image, image.get_rect(center=(297, 85)))
        pygame.draw.line(self.page, EDGE, (14, 110), (626, 110))
        for rect, label, _ in self.buttons:
            enabled = not ((label == 'Tile options' and self.brush not in OPTIONS)
                           or (label == 'Undo' and not self.history)
                           or (label == 'Remove' and len(self.doc.levels) == 1))
            self.button(rect, label or self.doc.name + '  >', label == 'Save' and self.dirty, enabled)
        board = self.level
        width, height = board.size
        ox, oy = self.offset
        try:
            color = pygame.Color('#' + board.colour)
        except ValueError:
            color = pygame.Color('#404080')
        pygame.draw.rect(self.page, PANEL, CANVAS)
        for y in range(oy, min(height, oy + CANVAS.h // CELL)):
            for x in range(ox, min(width, ox + CANVAS.w // CELL)):
                rect = pygame.Rect(CANVAS.x + (x-ox)*CELL, CANVAS.y + (y-oy)*CELL, CELL, CELL)
                pygame.draw.rect(self.page, color, rect)
                symbol = board.tile(x, y)
                self.icon(symbol, board.extra.get(symbol, {}).get((x, y), ()), rect)
                pygame.draw.rect(self.page, PANEL, rect, 1)
                if self.hover == (x, y):
                    pygame.draw.rect(self.page, GOLD, rect, 2)
        self.text('Rows {}–{} of {}'.format(oy+1, min(height, oy+CANVAS.h//CELL), height), (220, 420), MUTED)
        self.text('TILES', (414, 119), MUTED)
        for symbol, rect in self.swatches.items():
            pygame.draw.rect(self.page, (53, 63, 74), rect)
            self.icon(symbol, self.args if symbol == self.brush else (), rect)
            if symbol == '.':
                pygame.draw.line(self.page, MUTED, rect.bottomleft + pygame.Vector2(6, -6),
                                 rect.topright + pygame.Vector2(-6, 6), 1)
            pygame.draw.rect(self.page, GOLD if symbol == self.brush else EDGE, rect, 2 if symbol == self.brush else 1)
        self.text(PALETTE.get(self.brush, self.brush), (414, 309), GOLD)
        pygame.draw.line(self.page, EDGE, (14, 449), (626, 449))
        self.text(self.message or 'Left drag to paint    Right drag to erase    Middle click to pick a tile',
                  (14, 458), GOLD if self.message else MUTED, limit=612)
        if self.dialog:
            self.dialog.draw(self)
        self.screen.fill(BACKGROUND)
        self.screen.blit(pygame.transform.scale(self.page, self.viewport.size), self.viewport)
        pygame.display.flip()

    def form(self, title, fields, submit, accept='Apply', hint=''):
        self.stroke = None
        self.dialog = Dialog(title, fields, submit, accept, hint)
        pygame.key.start_text_input()

    def close_dialog(self):
        self.dialog = None
        pygame.key.stop_text_input()

    def guard(self, action):
        if self.dirty:
            self.form('Discard unsaved changes?', [], action, 'Discard', 'Cancel to return to your work.')
        else:
            action()

    def done(self):
        def finish():
            self.finished = True
        self.guard(finish)

    def new_set(self):
        def create(name):
            name = name.strip()
            check_name(name)
            if name in self.packs:
                raise ValueError('A set with that name already exists.')
            self.load(LevelSet(name), 0)
        self.guard(lambda: self.form('New level set', [field('Set name', '')], create, 'Create'))

    def open_set(self):
        names = sorted(self.packs)
        def select(name):
            self.load(LevelSet(name, read_level_source(name)), 0)
            self.last_saved = name, 0
        name = self.doc.name if self.doc.name in names else names[0]
        self.guard(lambda: self.form('Open level set', [field('Set', name, names)], select, 'Open'))

    def save_as(self):
        def save_new(name):
            name = name.strip()
            if name in self.packs:
                raise ValueError('Choose a new set name.')
            self.save(name)
        self.form('Save set as', [field('New set name', self.doc.name + '-copy')], save_new, 'Save copy')

    def save(self, name=None):
        name = self.doc.name if name is None else name
        self.packs[name] = self.doc.save(name)
        self.last_saved = name, self.index
        self.history.clear()
        self.dirty = False
        self.message = 'Saved {}.dat'.format(name)

    def remember(self):
        self.history.append((self.doc.levels.copy(), self.index, self.dirty))
        self.dirty = True
        self.message = ''

    def undo(self):
        if self.history:
            self.doc.levels, self.index, self.dirty = self.history.pop()
            self.pan(0, 0)
            self.message = 'Undid the last edit.'

    def navigate(self, step):
        self.index = (self.index + step) % len(self.doc.levels)
        self.offset = [0, 0]
        self.message = ''

    def add(self, duplicate):
        self.remember()
        level = deepcopy(self.level) if duplicate else Level.new()
        self.index += 1
        self.doc.levels.insert(self.index, level)
        self.offset = [0, 0]

    def remove(self):
        if len(self.doc.levels) > 1:
            def delete():
                self.remember()
                del self.doc.levels[self.index]
                self.index = min(self.index, len(self.doc.levels) - 1)
                self.offset = [0, 0]
            self.form('Remove level {}?'.format(self.index + 1), [], delete, 'Remove', 'Undo restores this board.')

    def settings(self):
        board = self.level
        width, height = board.size
        def apply(position, w, h, colour, author, screws):
            position, w, h = int(position), int(w), int(h)
            if not 1 <= position <= len(self.doc.levels):
                raise ValueError('Enter a level number within this set.')
            if min(w, h) < 1 or w*h > max(65536, width*height):
                raise ValueError('Use positive dimensions up to 65,536 tiles.')
            colour = colour.strip().lstrip('#')
            if not re.fullmatch('[a-fA-F0-9]{6}', colour):
                raise ValueError('Enter a six-digit hex colour.')
            if screws and not screws.isdecimal():
                raise ValueError('Enter a screw count or leave it blank.')
            if author.startswith(('[', '#')) or '\n' in author or '\r' in author:
                raise ValueError('Use a single line for the author. Avoid initial [ or #.')
            self.remember()
            board = deepcopy(self.level)
            if (w, h) != (width, height):
                board.resize(w, h)
            board.colour, board.author = colour, author
            board.screws = int(screws) if screws else None
            del self.doc.levels[self.index]
            self.index = position - 1
            self.doc.levels.insert(self.index, board)
            self.pan(0, 0)
        self.form('Board settings', [field('Position in set', self.index + 1), field('Width', width), field('Height', height), field('Colour (RGB hex)', board.colour),
                  field('Author', board.author), field('Screws (blank = all)', board.screws if board.screws is not None else '')],
                  apply, hint='The game shows 16 columns. Smaller sizes crop the board.')

    def select_brush(self, symbol, args=None):
        self.brush = symbol
        if args is None:
            args = tuple(DIRECTIONS.index(options[0]) if options in (VERTICAL, HORIZONTAL) else 0
                         for _, options in OPTIONS.get(symbol, ()))
            if symbol == '&':
                args = (1,)
        self.args = args
        self.message = ''

    def tile_options(self):
        options = OPTIONS.get(self.brush)
        if not options:
            return
        fields = []
        for i, (label, values) in enumerate(options):
            value = self.args[i] if i < len(self.args) else int(self.brush == '^' and i == 2 and len(self.args) == 2)
            if values in (DIRECTIONS, HORIZONTAL, VERTICAL):
                value = DIRECTIONS[value]
            elif values:
                value = values[value]
            fields.append(field(label, value, values))
        def apply(*values):
            args = []
            for value, (_, options) in zip(values, OPTIONS[self.brush]):
                if options in (DIRECTIONS, HORIZONTAL, VERTICAL):
                    args.append(DIRECTIONS.index(value))
                elif options:
                    args.append(options.index(value))
                elif re.fullmatch(r'[A-Za-z]|[0-9]+', value):
                    args.append(int(value) if value.isdecimal() else value)
                else:
                    raise ValueError('Use a letter or a number for the link group.')
            self.args = tuple(args)
        self.form(PALETTE[self.brush] + ' options', fields, apply, hint='Paint to apply these settings to a tile.')

    def pan(self, dx, dy):
        for i, (step, size, visible) in enumerate(zip((dx, dy), self.level.size, (CANVAS.w//CELL, CANVAS.h//CELL))):
            self.offset[i] = max(0, min(self.offset[i] + step, size - visible))

    def cell(self, pos):
        if CANVAS.collidepoint(pos):
            x = (pos[0] - CANVAS.x)//CELL + self.offset[0]
            y = (pos[1] - CANVAS.y)//CELL + self.offset[1]
            w, h = self.level.size
            if x < w and y < h:
                return x, y

    def paint(self, point):
        previous, button, changed = self.stroke
        if point is not None:
            x, y = previous or point
            dx, dy = point[0]-x, point[1]-y
            steps = max(abs(dx), abs(dy), 1)
            board = self.level if changed else deepcopy(self.level)
            symbol, args = ('.', ()) if button == 3 else (self.brush, self.args)
            painted = False
            for i in range(1, steps + 1):
                if board.paint(x + round(dx*i/steps), y + round(dy*i/steps), symbol, args):
                    painted = True
            if painted and not changed:
                self.remember()
                self.doc.levels[self.index] = board
                changed = True
        self.stroke = point, button, changed

    def handle(self, event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEWHEEL, pygame.WINDOWFOCUSLOST):
            self.stroke = None
        if event.type == pygame.QUIT:
            self.guard(main.quit)
            return
        pos = (0, 0)
        if hasattr(event, 'pos'):
            pos = ((event.pos[0]-self.viewport.x)*640//self.viewport.w,
                   (event.pos[1]-self.viewport.y)*480//self.viewport.h)
        if self.dialog:
            self.dialog.handle(self, event, pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            point = self.cell(pos)
            if point is not None:
                if event.button in (1, 3):
                    self.stroke = None, event.button, False
                    self.paint(point)
                elif event.button == 2:
                    symbol = self.level.tile(*point)
                    args = self.level.extra.get(symbol, {}).get(point, ())
                    self.select_brush(symbol, args[:1] if symbol == '&' else args)
            elif event.button == 1:
                for rect, _, callback in self.buttons:
                    if pygame.Rect(rect).collidepoint(pos):
                        callback()
                        return
                for symbol, rect in self.swatches.items():
                    if rect.collidepoint(pos):
                        self.select_brush(symbol)
                        return
        elif event.type == pygame.MOUSEBUTTONUP:
            self.stroke = None
        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.cell(pos)
            if self.stroke:
                self.paint(self.hover)
        elif event.type == pygame.MOUSEWHEEL:
            self.pan(-event.x, -event.y*3)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done()
            elif event.mod & pygame.KMOD_CTRL and event.key == pygame.K_s:
                self.save()
            elif event.mod & pygame.KMOD_CTRL and event.key == pygame.K_z:
                self.undo()
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                self.pan(int(event.key == pygame.K_RIGHT) - int(event.key == pygame.K_LEFT),
                         int(event.key == pygame.K_DOWN) - int(event.key == pygame.K_UP))
        elif event.type != pygame.WINDOWEXPOSED:
            return False

    def run(self):
        self.draw()
        while not self.finished:
            try:
                redraw = self.handle(pygame.event.wait())
            except (ValueError, OSError) as err:
                self.message = str(err)
                redraw = True
            if redraw is not False:
                self.draw()
        self.close_dialog()
        if self.doc.name in self.packs:
            return self.doc.name, min(self.index, len(self.packs[self.doc.name])-1)
        return self.last_saved
