"""Front menu for choosing a level set, starting board and visual theme."""
import pygame

import robbo as main
from . import images, quit

BACKGROUND = (18, 23, 31)
PANEL = (30, 38, 49)
EDGE = (66, 79, 91)
TEXT = (241, 238, 223)
MUTED = (169, 183, 190)
GOLD = (255, 199, 87)

ROWS = tuple(pygame.Rect(36, y, 300, 40) for y in (144, 217, 290))
START = pygame.Rect(36, 348, 164, 44)
EDIT = pygame.Rect(208, 348, 128, 44)
PREVIEW = pygame.Rect(366, 118, 238, 274)


def preview_tiles(skin, size=8):
    """Use the registered sprites' still images without spawning any game objects."""
    from .game import Board

    icons = {'R': images.ROBBO_S1, 'M': images.MAGNET_R,
             'L': images.BLAST_H1, 'l': images.BLAST_V1}
    for symbol, sprite in Board.symbols.items():
        frames = getattr(sprite, 'IMAGES', None)
        icon = frames[0] if frames else getattr(sprite, 'IMAGE', None)
        if icon is not None:
            icons[symbol] = icon
    return {symbol: pygame.transform.smoothscale(skin.get_icon(icon), (size, size))
            for symbol, icon in icons.items()}


def draw_preview(screen, board, tiles):
    rows = board['data'].splitlines()
    surface = pygame.Surface((8 * max(map(len, rows)), 8 * len(rows)))
    try:
        surface.fill(bytes.fromhex(board.get('colour', '404080')))
    except (TypeError, ValueError):
        surface.fill((64, 64, 128))
    for y, row in enumerate(rows):
        for x, symbol in enumerate(row):
            if symbol in tiles:
                surface.blit(tiles[symbol], (8 * x, 8 * y))
    area = PREVIEW.inflate(-24, -24)
    area.top += 26
    area.height -= 26
    rect = surface.get_rect().fit(area)
    screen.blit(pygame.transform.scale(surface, rect.size), rect)


class LevelMenu:
    def __init__(self, screen, skins, packs, name, saved):
        self.screen = screen
        self.page = pygame.Surface((640, 480)).convert()
        self.viewport = self.page.get_rect().fit(screen.get_rect())
        self.packs = packs
        self.names = sorted(packs)
        self.name = name
        self.positions = {}
        for name, boards in packs.items():
            index = saved.get(name, 0)
            if not isinstance(index, int):
                index = 0
            self.positions[name] = max(0, min(index, len(boards) - 1))
        self.row = 0
        self.notice = None
        self.skins = skins
        self.small = pygame.font.Font(None, 22)
        self.large = pygame.font.Font(None, 36)
        self.title = pygame.font.Font(None, 84).render('PyRobbo', True, TEXT)
        self.set_skin(main.skin)

    def set_skin(self, skin):
        skin_images = images.Images(skin)
        self.robot = pygame.transform.scale(skin_images.get_icon(images.ROBBO_S1), (64, 64))
        self.tiles = preview_tiles(skin_images)
        main.skin = skin

    def move(self, step):
        self.row = (self.row + step) % len(ROWS)

    def change(self, step):
        self.notice = None
        if self.row == 0:
            self.name = self.names[(self.names.index(self.name) + step) % len(self.names)]
        elif self.row == 1:
            self.positions[self.name] = (self.positions[self.name] + step) % len(self.packs[self.name])
        else:
            self.set_skin(self.skins[(self.skins.index(main.skin) + step) % len(self.skins)])

    def draw(self):
        screen = self.page
        screen.fill(BACKGROUND)
        screen.blit(self.robot, (32, 27))
        screen.blit(self.title, (113, 28))
        pygame.draw.line(screen, EDGE, (36, 103), (604, 103))
        level = self.positions[self.name]
        count = len(self.packs[self.name])
        fields = (
            ('LEVEL SET', self.name, len(self.names)),
            ('LEVEL', '{} / {}'.format(level + 1, count), count),
            ('THEME', main.skin, len(self.skins)),
        )
        for i, (label, value, choices) in enumerate(fields):
            rect = ROWS[i]
            active = i == self.row
            screen.blit(self.small.render(label, True, GOLD if active else MUTED),
                        (rect.x, rect.y - 24))
            pygame.draw.rect(screen, PANEL, rect)
            pygame.draw.rect(screen, GOLD if active else EDGE, rect, 2 if active else 1)
            color = TEXT if choices > 1 else EDGE
            for direction, x in ((-1, rect.left + 22), (1, rect.right - 22)):
                y = rect.centery
                pygame.draw.polygon(screen, color, [(x + direction * 4, y),
                                                    (x - direction * 3, y - 6),
                                                    (x - direction * 3, y + 6)])
            if self.large.size(value)[0] > rect.width - 80:
                while self.large.size(value + '…')[0] > rect.width - 80:
                    value = value[:-1]
                value += '…'
            text = self.large.render(value, True, TEXT)
            screen.blit(text, text.get_rect(center=rect.center))

        pygame.draw.rect(screen, PANEL, PREVIEW)
        pygame.draw.rect(screen, EDGE, PREVIEW, 1)
        screen.blit(self.small.render('LEVEL PREVIEW', True, MUTED), (PREVIEW.x + 12, PREVIEW.y + 10))
        draw_preview(screen, self.packs[self.name][level], self.tiles)
        pygame.draw.rect(screen, GOLD, START)
        text = self.large.render('Start Level', True, BACKGROUND)
        screen.blit(text, text.get_rect(center=START.center))
        pygame.draw.rect(screen, PANEL, EDIT)
        pygame.draw.rect(screen, EDGE, EDIT, 1)
        text = self.small.render('Level editor  [E]', True, TEXT)
        screen.blit(text, text.get_rect(center=EDIT.center))
        pygame.draw.line(screen, EDGE, (36, 420), (604, 420))
        if self.notice:
            screen.blit(self.small.render(self.notice, True, GOLD), (36, 441))
        else:
            for x, key, action in ((36, 'UP/DOWN', 'Select'), (184, 'LEFT/RIGHT', 'Change'),
                                   (361, 'ENTER', 'Start'), (495, 'ESC', 'Quit')):
                key_text = self.small.render(key, True, TEXT)
                screen.blit(key_text, (x, 441))
                screen.blit(self.small.render(action, True, MUTED), (x + key_text.get_width() + 6, 441))
        self.screen.fill(BACKGROUND)
        page = self.page
        if page.get_size() != self.viewport.size:
            page = pygame.transform.scale(page, self.viewport.size)
        self.screen.blit(page, self.viewport)
        pygame.display.flip()

    def edit(self):
        from .editor import LevelEditor
        try:
            editor = LevelEditor(self.screen, self.packs, self.name, self.positions[self.name])
        except (OSError, ValueError, IndexError, KeyError) as err:
            self.notice = 'Cannot open set: {}'.format(err)
            return
        self.notice = None
        self.name, index = editor.run()
        self.positions[self.name] = index
        self.names = sorted(self.packs)
        for name in self.names:
            self.positions[name] = min(self.positions.get(name, 0), len(self.packs[name]) - 1)

    def click(self, pos):
        x, y = pos
        pos = ((x - self.viewport.x) * self.page.get_width() // self.viewport.width,
               (y - self.viewport.y) * self.page.get_height() // self.viewport.height)
        if START.collidepoint(pos):
            return True
        if EDIT.collidepoint(pos):
            self.edit()
            return False
        for i, rect in enumerate(ROWS):
            if rect.collidepoint(pos):
                self.row = i
                if pos[0] < rect.left + 40:
                    self.change(-1)
                elif pos[0] >= rect.right - 40:
                    self.change(1)
                break
        return False


def select_level(screen, skins, packs, name, saved):
    menu = LevelMenu(screen, skins, packs, name, saved)
    screen.set_clip(None)
    pygame.mouse.set_visible(True)
    # Keep the device open so SDL delivers axis, hat and button events.
    joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() else None
    axes = [0, 0]
    repeat = pygame.key.get_repeat()
    pygame.key.set_repeat(350, 85)
    menu.draw()
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or (event.key == pygame.K_q and event.mod & pygame.KMOD_CTRL):
                quit()
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                break
            if event.key in (pygame.K_UP, pygame.K_w):
                menu.move(-1)
            elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_TAB):
                menu.move(1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                menu.change(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                menu.change(1)
            elif event.key == pygame.K_e:
                menu.edit()
            elif event.key == pygame.K_f:
                flags = main.FLAGS_WINDOW if screen.get_flags() & pygame.FULLSCREEN else main.FLAGS_FULLSCREEN
                main.screen = screen = pygame.display.set_mode((640, 480), flags)
                menu.screen = screen
                menu.viewport = menu.page.get_rect().fit(screen.get_rect())
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if menu.click(event.pos):
                break
        elif event.type == pygame.JOYBUTTONDOWN and event.button == 0:
            break
        elif event.type == pygame.JOYHATMOTION:
            dx, dy = event.value
            if dy:
                menu.move(-dy)
            elif dx:
                menu.change(dx)
            else:
                continue
        elif event.type == pygame.JOYAXISMOTION and event.axis in (0, 1):
            axis = event.axis
            if abs(event.value) < 0.45:
                axes[axis] = 0
                continue
            direction = 1 if event.value > 0 else -1
            if abs(event.value) < 0.55 or direction == axes[axis]:
                continue
            axes[axis] = direction
            if axis == 0:
                menu.change(direction)
            else:
                menu.move(direction)
        elif event.type != pygame.WINDOWEXPOSED:
            continue
        menu.draw()

    pygame.key.set_repeat(*repeat)
    screen.fill((0, 0, 0))
    pygame.mouse.set_visible(False)
    return menu.name, menu.positions[menu.name]
