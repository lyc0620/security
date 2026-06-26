import pygame
import random
from codes.util import loadText
import math

CLR_BODY   = pygame.Color("#a6b5d6")
CLR_BORDER = pygame.Color("#7e8dae")
CLR_CLOSE  = pygame.Color("#667596")

ICON_SIZE = 32
LABEL_MAX_W = 42
LABEL_LINE_GAP = 1
FILE_CELL_W = 58
FILE_CELL_H = 62
DIR_PAD_X = 25
DIR_PAD_Y = 16

EXT_BY_TYPE = {
    'image': '.png',
    'txt': '.txt',
    'locker': '.lock',
    'sys': '.exe',
    'command': '.exe',
    'lock': '.lock',
    '': '.lock',
}


def display_name(name, obj_type):
    ext = EXT_BY_TYPE.get(obj_type, '')
    return name if not ext or name.endswith(ext) else name + ext


def truncate_to_width(font, text, max_w):
    if font.size(text)[0] <= max_w:
        return text
    ellipsis = '...'
    while text and font.size(text + ellipsis)[0] > max_w:
        text = text[:-1]
    return text + ellipsis if text else ellipsis


def wrap_label(font, text, max_w=LABEL_MAX_W, max_lines=2):
    if font.size(text)[0] <= max_w:
        return [text]

    parts = text.split('.')
    candidates = []
    if len(parts) > 1:
        candidates.append((text[:-(len(parts[-1]) + 1)], '.' + parts[-1]))

    for i in range(1, len(text)):
        candidates.append((text[:i], text[i:]))

    best = None
    best_score = None
    for left, right in candidates:
        if not left or not right:
            continue
        lw = font.size(left)[0]
        rw = font.size(right)[0]
        overflow = max(0, lw - max_w) + max(0, rw - max_w)
        balance = abs(lw - rw)
        score = (overflow, balance)
        if best_score is None or score < best_score:
            best = (left, right)
            best_score = score
            if overflow == 0 and balance <= 6:
                break

    if best is None:
        return [truncate_to_width(font, text, max_w)]

    lines = [truncate_to_width(font, best[0], max_w), truncate_to_width(font, best[1], max_w)]
    return lines[:max_lines]


def directory_auto_size(files, min_size=(100, 70)):
    if not files: return min_size
    max_x = max(f.ref_pos[0] + FILE_CELL_W for f in files) + DIR_PAD_X
    max_y = max(f.ref_pos[1] + FILE_CELL_H for f in files) + DIR_PAD_Y
    return max(min_size[0], max_x), max(min_size[1], max_y)


class Window:
    def __init__(self, file, game, size):
        self.game = game
        self.file = file
        self.size = size
        if file is not None: x, y = file.pos[0] - 10, file.pos[1] - 10
        else: x, y = 450 - self.size[0] // 2, 325 - self.size[1] // 2
        self.rect = pygame.Rect(x, y, size[0], size[1])
        self.dragging = False
        self._drag_off = (0, 0)

    def tick(self, dt): pass

    def is_top(self, pos):
        for w in reversed(self.game.windows):
            if w.rect.collidepoint(pos): return w is self
            if w.titlebar_rect.collidepoint(pos): return w is self
        return True

    @property
    def titlebar_rect(self):
        return pygame.Rect(self.rect.x - 2, self.rect.y - 10, self.rect.w + 4, 10)

    @property
    def close_rect(self):
        return pygame.Rect(self.rect.right - 8, self.rect.y - 10, 10, 10)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos):
                return

        if self.file is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_rect.collidepoint(event.pos):
                    self.file.open = False
                    if self in self.game.windows:
                        self.game.windows.remove(self)
                    return
                if self.titlebar_rect.collidepoint(event.pos):
                    self.dragging = True
                    self._drag_off = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                    if self in self.game.windows:
                        self.game.windows.remove(self)
                        self.game.windows.append(self)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.rect.x = event.pos[0] - self._drag_off[0]
                self.rect.y = event.pos[1] - self._drag_off[1]

    def render(self):
        pygame.draw.rect(self.game.screen, CLR_BODY, self.rect)
        pygame.draw.rect(self.game.screen, CLR_BORDER, (self.rect.x - 2, self.rect.y - 10, self.rect.w + 4, self.rect.h + 12), 2)
        pygame.draw.rect(self.game.screen, CLR_BORDER, self.titlebar_rect)
        pygame.draw.rect(self.game.screen, CLR_CLOSE, self.close_rect)

class DirWindow(Window):
    def __init__(self, file, game, size, files):
        super().__init__(file, game, size)
        self.files = files

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos): return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                self.file.open = False
                if self in self.game.windows:
                    self.game.windows.remove(self)
                    for file in self.files:
                        if file.objType == 'directory': self.game.directories.remove(file)
                        elif file.objType == 'image': self.game.images.remove(file)
                        elif file.objType == 'txt': self.game.texts.remove(file)
                        else: self.game.etcs.remove(file)
                return
            if self.titlebar_rect.collidepoint(event.pos):
                self.dragging = True
                self._drag_off = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                if self in self.game.windows:
                    self.game.windows.remove(self)
                    self.game.windows.append(self)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] - self._drag_off[0]
            self.rect.y = event.pos[1] - self._drag_off[1]

    def render(self):
        super().render()
        for file in self.files: file.render((10, 15, 22))

class TextWindow(Window):
    def __init__(self, file, game, size, text):
        super().__init__(file, game, size)
        self.text = text

    def render(self):
        super().render()
        text = []
        for t in self.text:
            text.append(self.game.font2.render(t, False, (10, 15, 22)))
        h = self.size[1] / len(text)
        for i in range(len(text)):
            self.game.screen.blit(text[i], (self.rect.x, self.rect.y + i * h))
class TxWindow(TextWindow):
    def __init__(self, file, game, size):
        self.game = game
        self.text = loadText('Tx7y1.txt') if self.game.light else loadText('Tx7y1_.txt')
        super().__init__(file, self.game, size, self.text)

    def update(self, event):
        super().update(event)
        self.text = loadText('Tx7y1.txt') if self.game.light else loadText('Tx7y1_.txt')

class ImgWindow(Window):
    def __init__(self, file, game, size, img):
        super().__init__(file, game, size)
        self.img = img

    def render(self):
        super().render()
        self.game.screen.blit(self.img, self.rect)
class TranImgWindow(ImgWindow):
    def render(self):
        pygame.draw.rect(self.game.screen, CLR_BORDER, (self.rect.x - 2, self.rect.y - 10, self.rect.w + 4, self.rect.h + 12), 2)
        pygame.draw.rect(self.game.screen, CLR_BORDER, self.titlebar_rect)
        pygame.draw.rect(self.game.screen, CLR_CLOSE, self.close_rect)
        self.game.screen.blit(self.img, self.rect)
class LockWindow(ImgWindow):
    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos):
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                self.file.open = False
                if self in self.game.windows:
                    self.game.windows.remove(self)
                return
            if self.titlebar_rect.collidepoint(event.pos):
                self.dragging = True
                self._drag_off = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                if self in self.game.windows:
                    self.game.windows.remove(self)
                    self.game.windows.append(self)
            if self.rect.collidepoint(event.pos):
                self.game.lockToOpen()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] - self._drag_off[0]
            self.rect.y = event.pos[1] - self._drag_off[1]
class InteractiveImgWindow(ImgWindow):
    def __init__(self, file, game, size, img):
        super().__init__(file, game, size, img)
        self.index = 0
        self.image = self.img[self.index]

    def update(self, event):
        self.image = self.image = self.img[self.index]

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos):
                return

        if self.file is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_rect.collidepoint(event.pos):
                    self.file.open = False
                    if self in self.game.windows:
                        self.game.windows.remove(self)
                    return
                if self.titlebar_rect.collidepoint(event.pos):
                    self.dragging = True
                    self._drag_off = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                    if self in self.game.windows:
                        self.game.windows.remove(self)
                        self.game.windows.append(self)
                if self.rect.collidepoint(event.pos):
                    self.index = (self.index + 1) % len(self.img)
                    self.game.asset['sfx/tick'].play()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.rect.x = event.pos[0] - self._drag_off[0]
                self.rect.y = event.pos[1] - self._drag_off[1]

    def render(self):
        Window.render(self)
        self.game.screen.blit(self.image, self.rect)

class ClockWindow(Window):
    def __init__(self, file, game, size=(150, 150)):
        super().__init__(file, game, size)
        self.hour = 0
        self.minute = 0

    def update(self, event):
        super().update(event)

        if self.file is None:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self not in self.game.windows:
                return

            if not self.is_top(event.pos):
                return

            if not self.rect.collidepoint(event.pos):
                return

            if event.button == 1:
                self.hour = (self.hour + 1) % 12
                self.game.asset['sfx/tick'].play()

            elif event.button == 3:
                self.minute += 5
                if self.minute >= 60:
                    self.minute %= 60
                    self.hour = (self.hour + 1) % 12
                self.game.asset['sfx/tick'].play()

    def render(self):
        super().render()

        cx = self.rect.x + self.rect.w // 2
        cy = self.rect.y + self.rect.h // 2
        radius = min(self.rect.w, self.rect.h) // 2 - 14

        dark = (10, 15, 22)
        light = (80, 95, 125)

        pygame.draw.rect(self.game.screen, dark, (self.rect.x, self.rect.y, self.rect.w, self.rect.h))

        for i in range(60):
            angle = math.radians(i * 6 - 90)
            outer_x = cx + math.cos(angle) * radius
            outer_y = cy + math.sin(angle) * radius

            if i % 5 == 0:
                inner = radius - 10
                width = 2
                color = dark
            else:
                inner = radius - 5
                width = 1
                color = light

            inner_x = cx + math.cos(angle) * inner
            inner_y = cy + math.sin(angle) * inner

            pygame.draw.line(
                self.game.screen,
                color,
                (inner_x, inner_y),
                (outer_x, outer_y),
                width
            )

        for num, pos in [('12', 0), ('3', 3), ('6', 6), ('9', 9)]:
            angle = math.radians(pos * 30 - 90)
            text = self.game.font2.render(num, True, dark)
            tx = cx + math.cos(angle) * (radius - 24) - text.get_width() // 2
            ty = cy + math.sin(angle) * (radius - 24) - text.get_height() // 2
            self.game.screen.blit(text, (tx, ty))

        minute_angle = math.radians(self.minute * 6 - 90)
        hour_angle = math.radians(((self.hour % 12) + self.minute / 60) * 30 - 90)

        hour_len = radius * 0.45
        minute_len = radius * 0.68

        hx = cx + math.cos(hour_angle) * hour_len
        hy = cy + math.sin(hour_angle) * hour_len
        mx = cx + math.cos(minute_angle) * minute_len
        my = cy + math.sin(minute_angle) * minute_len

        pygame.draw.line(self.game.screen, light, (cx, cy), (hx, hy), 5)
        pygame.draw.line(self.game.screen, light, (cx, cy), (mx, my), 3)
        pygame.draw.circle(self.game.screen, light, (cx, cy), 5)

        time_text = '{:02d}:{:02d}'.format(self.hour if self.hour != 0 else 12, self.minute)
        surf = self.game.font.render(time_text, True, light)
        self.game.screen.blit(
            surf,
            (cx - surf.get_width() // 2, self.rect.bottom - 12)
        )

class LockerWindow(Window):
    def __init__(self, file, game, size, password):
        super().__init__(file, game, size)
        self.password = password
        self.length = len(self.password)
        self.nums = [0 for _ in range(self.length)]
        self.inputPW = ''

    @property
    def slot_rect(self):
        return [pygame.Rect(self.rect.x + 20 + i * 52, self.rect.y + 20, 32, 64) for i in range(self.length)]

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos):
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                self.file.open = False
                if self in self.game.windows:
                    self.game.windows.remove(self)
                return
            if self.titlebar_rect.collidepoint(event.pos):
                self.dragging = True
                self._drag_off = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                if self in self.game.windows:
                    self.game.windows.remove(self)
                    self.game.windows.append(self)
            for i in range(self.length):
                if self.slot_rect[i].collidepoint(event.pos):
                    self.nums[i] = (self.nums[i] + 1) % 10
                    self.game.asset['sfx/tick'].play()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] - self._drag_off[0]
            self.rect.y = event.pos[1] - self._drag_off[1]

        for i in self.nums:
            self.inputPW += str(i)

        if self.inputPW == self.password: self.game.lockToOpen()
        self.inputPW = ''

    def render(self):
        pygame.draw.rect(self.game.screen, CLR_BODY, self.rect)
        pygame.draw.rect(self.game.screen, CLR_BORDER, (self.rect.x - 2, self.rect.y - 10, self.rect.w + 4, self.rect.h + 12), 2)
        pygame.draw.rect(self.game.screen, CLR_BORDER, self.titlebar_rect)
        pygame.draw.rect(self.game.screen, CLR_CLOSE, self.close_rect)
        for i in range(self.length):
            pygame.draw.rect(self.game.screen, '#FFFFFF', self.slot_rect[i])
            self.game.screen.blit(self.game.font3.render(str(self.nums[i]), True, (10, 15, 22)), (self.slot_rect[i].x + 1, self.slot_rect[i].y + 3))

class LoaderWindow(Window):
    def __init__(self, file, game, spd=(0, 3), comment=None, size=(100, 60)):
        if comment: super().__init__(file, game, size)
        else: super().__init__(file, game, size)
        self.load = 0
        self.spd = spd
        self.comment = comment
        self.size = size

    def tick(self, dt):
        self.load += random.randrange(self.spd[0], self.spd[1])
        self.load = min(self.load, self.loader_rect.w)
        if self.load >= self.loader_rect.w:
            if self in self.game.windows: self.game.windows.remove(self)
            self.game.download(self.file)

    @property
    def loader_rect(self):
        if self.comment: return pygame.Rect(self.rect.x + 20, self.rect.y + 30, self.size[0] - 40, 20)
        else: return pygame.Rect(self.rect.x + 20, self.rect.y + 10, self.size[0] - 40, 20)

    def render(self):
        super().render()
        pygame.draw.rect(self.game.screen, (170, 170, 185), self.loader_rect)
        pygame.draw.rect(self.game.screen, CLR_BORDER, (self.loader_rect.x, self.loader_rect.y, self.load, 20))
        if self.comment:
            text = self.game.font.render(self.comment, True, (10, 15, 22))
            self.game.screen.blit(text, (self.loader_rect.x, self.loader_rect.y - 20))

class SystemRebootWindow(Window):
    def __init__(self, file, game, size=(360, 170), interval_ms=360, end_delay_ms=900, blackout_ms=13500):
        super().__init__(file, game, size)
        self.rect.topleft = (270, 240)
        self.interval_ms = interval_ms
        self.end_delay_ms = end_delay_ms
        self.blackout_ms = blackout_ms
        self.elapsed = 0
        self.blackout_elapsed = 0
        self.phase = 'console'
        self.lines = []
        self.all_lines = [
            '$ sysctl reboot --safe',
            '[sys] closing active windows...',
            '[sys] flushing visual layer...',
            '[sys] display driver: stopped',
            '[sys] auth cache: sealed',
            '[sys] kernel handoff: ok',
            '[sys] system rebooting...',
        ]
        self.game.bgm_playing = False
        self.game.suppress_bgm = False

    def tick(self, dt):
        if self.phase == 'console':
            self.elapsed += dt
            target_count = min(len(self.all_lines), self.elapsed // self.interval_ms + 1)
            while len(self.lines) < target_count:
                self.lines.append(self.all_lines[len(self.lines)])
                self.game.asset['sfx/tick'].play()

            if self.elapsed >= len(self.all_lines) * self.interval_ms + self.end_delay_ms:
                self.phase = 'blackout'
                self.game.suppress_bgm = False
                self.game.bgm_playing = True
                self.blackout_elapsed = 0
                self.game.asset['sfx/ominous'].play()

        elif self.phase == 'blackout':
            self.blackout_elapsed += dt
            if self.blackout_ms - 3500 >= self.blackout_elapsed >= self.blackout_ms - 6500:
                pygame.mixer.stop()
                self.game.asset['sfx/reboot'].play()
                self.game.light = True
            if self.blackout_elapsed >= self.blackout_ms:
                self.game.suppress_bgm = False
                self.game.bgm_playing = False
                self.game.map = 1
                if self in self.game.windows:
                    self.game.windows.remove(self)

    def render(self):
        if self.phase == 'blackout':
            self.game.screen.fill((8, 12, 18))
            return

        self.game.screen.fill((0, 0, 0))
        pygame.draw.rect(self.game.screen, (8, 12, 18), self.rect)
        pygame.draw.rect(self.game.screen, CLR_BORDER, (self.rect.x - 2, self.rect.y - 10, self.rect.w + 4, self.rect.h + 12), 2)
        pygame.draw.rect(self.game.screen, CLR_BORDER, self.titlebar_rect)
        pygame.draw.rect(self.game.screen, CLR_CLOSE, self.close_rect)
        for i, line in enumerate(self.lines):
            surf = self.game.font2.render(line, True, (210, 235, 240))
            self.game.screen.blit(surf, (self.rect.x + 10, self.rect.y + 10 + i * (self.game.font2.get_height() + 7)))

class PadLockWindow(Window):
    def __init__(self, file, game, target_on):
        self.rows = len(target_on)
        self.cols = len(target_on[0])
        self.on = [[False for _ in range(self.cols)] for __ in range(self.rows)]
        self.target_on = [[bool(v) for v in row] for row in target_on]
        w = 28 + self.cols * 36 + (self.cols - 1) * 8
        h = 28 + self.rows * 36 + (self.rows - 1) * 8
        super().__init__(file, game, (w, h))

    def _rect_at(self, r, c):
        x = self.rect.x + 14 + c*(36 + 8)
        y = self.rect.y + 14 + r*(36 + 8)
        return pygame.Rect(x, y, 36, 36)

    def check(self):
        if self.on == self.target_on:
            self.game.asset['sfx/open'].play()
            self.game.padLockClear()
            self.file.open = False
            if self in self.game.windows: self.game.windows.remove(self)

    def update(self, event):
        super().update(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.dragging:
            if self.close_rect.collidepoint(event.pos) or self.titlebar_rect.collidepoint(event.pos): return
            if not self.is_top(event.pos): return
            for r in range(self.rows):
                for c in range(self.cols):
                    if self._rect_at(r, c).collidepoint(event.pos):
                        self.on[r][c] = not self.on[r][c]
                        self.game.asset['sfx/tick'].play()
                        self.check()
                        return

    def render(self):
        super().render()
        for r in range(self.rows):
            for c in range(self.cols):
                rect = self._rect_at(r, c)
                base = '#DFFFFF' if self.on[r][c] else '#CFCFCF'
                pygame.draw.rect(self.game.screen, base, rect, border_radius=6)
                pygame.draw.rect(self.game.screen, CLR_BORDER, rect, 2, border_radius=6)

class RotorWindow(Window):
    def __init__(self, file, game):
        super().__init__(file, game, (300, 190))
        self.left = 0
        self.right = 0
        self.cipher = ''
        self.output = ''
        self.active = True
        self.max_len = 8
        self.history = []

    @property
    def left_rotor_rect(self): return pygame.Rect(self.rect.x + 65, self.rect.y + 46, 46, 38)

    @property
    def right_rotor_rect(self): return pygame.Rect(self.rect.x + 190, self.rect.y + 46, 46, 38)

    @property
    def input_rect(self): return pygame.Rect(self.rect.x + 34, self.rect.y + 112, 232, 24)

    @property
    def output_rect(self): return pygame.Rect(self.rect.x + 34, self.rect.y + 152, 232, 24)

    def advance(self):
        self.right = (self.right + 1) % 10
        if self.right == 0: self.left = (self.left + 1) % 10

    def decode_digit(self, ch):
        prev_left = self.left
        prev_right = self.right

        c = int(ch)
        p = (c - self.left - self.right) % 10

        self.cipher += ch; self.output += str(p)
        self.history.append((prev_left, prev_right, ch, str(p)))

        self.advance()

    def backspace(self):
        if not self.history: return

        prev_left, prev_right, ch, p = self.history.pop()
        self.left = prev_left
        self.right = prev_right
        self.cipher = self.cipher[:-1]
        self.output = self.output[:-1]

    def clear(self):
        self.cipher = ''; self.output = ''
        self.history.clear()

    def update_rotor_by_click(self, rect, attr, event):
        if not rect.collidepoint(event.pos): return False

        if event.button == 1:
            setattr(self, attr, (getattr(self, attr) + 1) % 10)
            self.game.asset['sfx/tick'].play()
            return True

        if event.button == 3:
            setattr(self, attr, (getattr(self, attr) - 1) % 10)
            self.game.asset['sfx/tick'].play()
            return True

        return False

    def update(self, event):
        super().update(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos): return
            if self.close_rect.collidepoint(event.pos) or self.titlebar_rect.collidepoint(event.pos): return
            if self.update_rotor_by_click(self.left_rotor_rect, 'left', event): return
            if self.update_rotor_by_click(self.right_rotor_rect, 'right', event): return

            if event.button == 1:
                self.active = self.input_rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.backspace()
                self.game.asset['sfx/tick'].play()

            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_DELETE:
                self.clear()
                self.game.asset['sfx/tick'].play()

            elif event.unicode.isdigit() and len(self.cipher) < self.max_len:
                self.decode_digit(event.unicode)
                self.game.asset['sfx/tick'].play()

    def draw_digit_box(self, rect, value, label):
        bg = (230, 235, 245)
        fg = (10, 15, 22)

        label_surf = self.game.font.render(label, True, fg)
        self.game.screen.blit(
            label_surf,
            (
                rect.centerx - label_surf.get_width() // 2,
                rect.y - 13
            )
        )

        pygame.draw.rect(self.game.screen, bg, rect)
        pygame.draw.rect(self.game.screen, CLR_BORDER, rect, 2)

        value_surf = self.game.font3.render(str(value), True, fg)
        self.game.screen.blit(
            value_surf,
            (
                rect.centerx - value_surf.get_width() // 2,
                rect.centery - value_surf.get_height() // 2 - 1
            )
        )

    def draw_text_field(self, rect, label, text, active=False):
        fg = (10, 15, 22)

        label_surf = self.game.font.render(label, True, fg)
        self.game.screen.blit(label_surf, (rect.x, rect.y - 12))

        pygame.draw.rect(self.game.screen, (230, 235, 245), rect)
        pygame.draw.rect(self.game.screen, CLR_BORDER, rect, 2)

        shown = text
        if active and pygame.time.get_ticks() // 400 % 2 == 0:
            shown += '_'

        surf = self.game.font2.render(shown, True, fg)
        self.game.screen.blit(surf, (rect.x + 6, rect.y + 6))

    def render(self):
        super().render()

        fg = (10, 15, 22)

        title = self.game.font2.render('AUTH ROTOR', True, fg)
        self.game.screen.blit(title, (self.rect.x + 10, self.rect.y + 8))

        self.draw_digit_box(self.left_rotor_rect, self.left, 'L rotor')
        self.draw_digit_box(self.right_rotor_rect, self.right, 'R rotor')

        arrow = self.game.font2.render(':::', True, fg)
        self.game.screen.blit(
            arrow,
            (
                self.rect.centerx - arrow.get_width() // 2,
                self.left_rotor_rect.centery - arrow.get_height() // 2
            )
        )

        self.draw_text_field(self.input_rect, 'cipher input', self.cipher, self.active)
        self.draw_text_field(self.output_rect, 'live output', self.output, False)

class CommandWindow(Window):
    def __init__(self, file, game):
        super().__init__(file, game, (200, 140))
        self.commands = {'log': self.game.log,
                         'ping': self.game.ping,
                         'msg': self.game.msg}
        self.command = 0
        self.cmd = list(self.commands.values())[self.command]
        self.targets = ['root', 'L□■■f□r', 'Edward']
        self.target = 0

    @property
    def commandRect(self):
        return [pygame.Rect(self.rect.x + 15, self.rect.y + 15 + 30 * i, 70, 20) for i in range(3)]

    @property
    def buttonRect(self):
        return pygame.Rect(self.rect.x + 65, self.rect.y + self.rect.h - 35, 70, 20)

    @property
    def targetRect(self):
        return [pygame.Rect(self.rect.x + 115, self.rect.y + 15 + 30 * i, 70, 20) for i in range(3)]

    def update(self, event):
        self.cmd = list(self.commands.values())[self.command]

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos):
                return

        if self.file is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_rect.collidepoint(event.pos):
                    self.file.open = False
                    if self in self.game.windows:
                        self.game.windows.remove(self)
                    return
                if self.titlebar_rect.collidepoint(event.pos):
                    self.dragging = True
                    self._drag_off = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                    if self in self.game.windows:
                        self.game.windows.remove(self)
                        self.game.windows.append(self)
                for i in range(len(self.commandRect)):
                    if self.commandRect[i].collidepoint(event.pos): self.command = i; self.game.asset['sfx/tick'].play()
                for i in range(len(self.targetRect)):
                    if self.targetRect[i].collidepoint(event.pos): self.target = i; self.game.asset['sfx/tick'].play()
                if self.buttonRect.collidepoint(event.pos): self.cmd(self.targets[self.target]); self.game.asset['sfx/tick'].play()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.rect.x = event.pos[0] - self._drag_off[0]
                self.rect.y = event.pos[1] - self._drag_off[1]

    def render(self):
        super().render()
        for i in range(len(self.commandRect)):
            if i == self.command: pygame.draw.rect(self.game.screen, CLR_CLOSE, self.commandRect[i])
            else: pygame.draw.rect(self.game.screen, CLR_BORDER, self.commandRect[i])
            text = self.game.font4.render(list(self.commands.keys())[i], False, (10, 15, 22))
            x = self.commandRect[i].x + (self.commandRect[i].w - self.game.font4.size(list(self.commands.keys())[i])[0]) // 2
            y = self.commandRect[i].y + (self.commandRect[i].h - self.game.font4.size(list(self.commands.keys())[i])[1]) // 2
            self.game.screen.blit(text, (x, y))
        for i in range(len(self.targetRect)):
            if i == self.target: pygame.draw.rect(self.game.screen, CLR_CLOSE, self.targetRect[i])
            else: pygame.draw.rect(self.game.screen, CLR_BORDER, self.targetRect[i])
            text = self.game.font4.render(self.targets[i], False, (10, 15, 22))
            x = self.targetRect[i].x + (self.targetRect[i].w - self.game.font4.size(self.targets[i])[0]) // 2
            y = self.targetRect[i].y + (self.targetRect[i].h - self.game.font4.size(self.targets[i])[1]) // 2
            self.game.screen.blit(text, (x, y))
        pygame.draw.rect(self.game.screen, CLR_CLOSE, self.buttonRect)
        text = self.game.font4.render('run', False, (10, 15, 22))
        x = self.buttonRect.x + (self.buttonRect.w - self.game.font4.size('run')[0]) // 2
        y = self.buttonRect.y + (self.buttonRect.h - self.game.font4.size('run')[1]) // 2
        self.game.screen.blit(text, (x, y))

class ConsoleWindow(Window):
    def __init__(self, file, game, size=(280, 160), max_lines=200):
        super().__init__(file, game, size)
        self.lines = []
        self.max_lines = max_lines
        self.line_h = game.font2.get_height() + 2
        self.scroll = 0

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos):
                return

        if self.file is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_rect.collidepoint(event.pos):
                    self.file.open = False
                    if self in self.game.windows:
                        self.game.windows.remove(self)
                    return
                if self.titlebar_rect.collidepoint(event.pos):
                    self.dragging = True
                    self._drag_off = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                    if self in self.game.windows:
                        self.game.windows.remove(self)
                        self.game.windows.append(self)

            elif event.type == pygame.MOUSEWHEEL:
                self.scroll += event.y

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.rect.x = event.pos[0] - self._drag_off[0]
                self.rect.y = event.pos[1] - self._drag_off[1]

    def add_line(self, s: str):
        max_w = self.rect.w - 10
        words = s.split(' ')
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if self.game.font2.size(test)[0] <= max_w:
                cur = test
            else:
                self.lines.append(cur)
                cur = w
        if cur:
            self.lines.append(cur)
        if len(self.lines) > self.max_lines:
            over = len(self.lines) - self.max_lines
            self.lines = self.lines[over:]

    def render(self):
        super().render()
        visible_rows = self.rect.h // self.line_h
        start = max(0, len(self.lines) - visible_rows - self.scroll)
        end   = start + visible_rows
        for i, line in enumerate(self.lines[start:end]):
            surf = self.game.font2.render(line, True, (10,15,22))
            self.game.screen.blit(surf, (self.rect.x + 5, self.rect.y + 5 + i*self.line_h))



class File:
    def __init__(self, game, name, pos, objType, interaction, size=(100, 100), child = False):
        self.game = game
        self.name = name
        self.ref_pos = pos
        self.pos = pos
        self.objType = objType
        self.display_name = display_name(self.name, self.objType)
        self.size = size
        if self.objType in ['directory', 'image', 'txt']: self.icon = self.game.asset['icon/' + self.objType]
        else: self.icon = self.game.asset['icon/etc']
        self.open = False
        self.interaction = interaction
        self.child = child
        self.window = Window(self, self.game, self.size)
        self.owner_window = None

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], 32, 32)

    def update(self, dc_pos):
        if self.owner_window:
            self.pos = (self.owner_window.rect.x + self.ref_pos[0], self.owner_window.rect.y + self.ref_pos[1])
        if not self.child: self.render()

        top_win = None
        if dc_pos:
            for w in self.game.windows:
                if w.rect.collidepoint(dc_pos): top_win = w

        if top_win is not None and top_win is not self.owner_window: return

        if dc_pos and self.game.dc.pos and self.rect().collidepoint(dc_pos):
            if self.interaction:
                self.open = True
                self.game.dc.reset()
                self.window.rect.topleft = (self.pos[0] - 10, self.pos[1] - 10)
                if self.window not in self.game.windows:
                    self.game.windows.append(self.window)
            else: self.game.asset['sfx/locked'].play()

    def render(self, clr='#FFFFFF'):
        self.game.screen.blit(self.icon, self.pos)
        lines = wrap_label(self.game.font, self.display_name)
        line_h = self.game.font.get_height() + LABEL_LINE_GAP
        for i, line in enumerate(lines):
            text = self.game.font.render(line, False, clr)
            w = self.game.font.size(line)[0]
            x = self.pos[0] + ICON_SIZE // 2 - w // 2
            y = self.pos[1] + ICON_SIZE - 2 + i * line_h
            self.game.screen.blit(text, (x, y))
        if not self.interaction: self.game.screen.blit(self.game.asset['lock'], self.pos)

class Directory(File):
    def __init__(self, game, name, pos, files, interaction, child = False, size=(100, 100)):
        self.files = files
        self.size = directory_auto_size(self.files, size)
        super().__init__(game, name, pos, 'directory', interaction, self.size, child)
        self.window = DirWindow(self, self.game, self.size, files)
        self.refresh_layout()

    def refresh_layout(self):
        self.size = directory_auto_size(self.files, self.size)
        self.window.size = self.size
        self.window.rect.size = self.size
        self.window.files = self.files
        for f in self.files:
            f.owner_window = self.window
            f.child = True

    def update(self, dc_pos):
        if self.owner_window:
            self.pos = (self.owner_window.rect.x + self.ref_pos[0], self.owner_window.rect.y + self.ref_pos[1])
        if not self.child: self.render()

        top_win = None
        if dc_pos:
            for w in self.game.windows:
                if w.rect.collidepoint(dc_pos): top_win = w

        if top_win is not None and top_win is not self.owner_window: return
        if dc_pos and self.game.dc.pos and self.rect().collidepoint(dc_pos):
            if self.interaction:
                self.open = True
                self.game.dc.reset()
                self.refresh_layout()
                self.window.rect.topleft = (self.pos[0] - 10, self.pos[1] - 10)
                if self.window not in self.game.windows:
                    self.game.windows.append(self.window)
                for file in self.files:
                    if file.objType == 'directory' and file not in self.game.directories:
                        self.game.directories.append(file)
                    elif file.objType == 'image' and file not in self.game.images:
                        self.game.images.append(file)
                    elif file.objType == 'txt' and file not in self.game.texts:
                        self.game.texts.append(file)
                    elif file not in self.game.etcs:
                        self.game.etcs.append(file)
            else:
                self.game.asset['sfx/locked'].play()

class Text(File):
    def __init__(self, game, name, pos, interaction, child = False):
        self.game = game
        self.name = name
        self.text = self.game.asset['txt/' + self.name]
        longest = max(self.text, key=len)
        w = self.game.font2.size(longest)[0]
        h = len(self.text) * self.game.font2.size(self.text[0])[1]
        self.size = (w, h)
        super().__init__(game, name, pos, 'txt', interaction, self.size, child)
        self.window = TextWindow(self, self.game, self.size, self.text)
class Tx7y1(Text):
    def __init__(self, game, name, pos, interaction, child = False):
        super().__init__(game, name, pos, interaction, child)
        self.window = TxWindow(self, self.game, self.size)

class Image(File):
    def __init__(self, game, name, pos, interaction, child = False):
        self.game = game
        self.name = name
        self.image = self.game.asset['image/' + self.name]
        try: size = self.image.get_size()
        except AttributeError: size = self.image[0].get_size()
        super().__init__(game, name, pos, 'image', interaction, size, child)
        self.window = ImgWindow(self, self.game, size, self.image)
class TransparentImg(Image):
    def __init__(self, game, name, pos, interaction, child = False):
        super().__init__(game, name, pos, interaction, child)
        self.window = TranImgWindow(self, self.game, self.image.get_size(), self.image)
class LockImg(Image):
    def __init__(self, game, name, pos, interaction, child = False):
        super().__init__(game, name, pos, interaction, child)
        self.window = LockWindow(self, self.game, self.image.get_size(), self.image)
        self.objType = 'lock'
        self.display_name = display_name(self.name, self.objType)
        self.icon = self.game.asset['icon/etc']
class InteractiveImg(Image):
    def __init__(self, game, name, pos, interaction, child = False):
        super().__init__(game, name, pos, interaction, child)
        if self.name == 'clock': self.window = ClockWindow(self, self.game, self.size)
        else: self.window = InteractiveImgWindow(self, self.game, self.size, self.image)

class Locker(File):
    def __init__(self, game, name, pos, password, interaction, child=False):
        self.game = game
        self.name = name
        self.password = password
        self.length = len(self.password)
        self.size = (52 * self.length + 20, 104)
        super().__init__(game, name, pos, 'locker', interaction, self.size, child)
        self.window = LockerWindow(self, self.game, self.size, self.password)

class Sys(File):
    def __init__(self, game, name, pos, interaction, child = False):
        super().__init__(game, name, pos, 'sys', interaction, child=child)
        self.window = LoaderWindow(self, self.game)

class PadLock(File):
    def __init__(self, game, name, pos, interaction, target, child = False):
        super().__init__(game, name, pos, '', interaction, (100, 100), child)
        self.window = PadLockWindow(self, self.game, target)

class Rotor(File):
    def __init__(self, game, name, pos, interaction, child=False):
        super().__init__(game, name, pos, 'sys', interaction, child=child)
        self.window = RotorWindow(self, self.game)

class Command(File):
    def __init__(self, game, name, pos, interaction, child = False):
        super().__init__(game, name, pos, 'command', interaction, child=child)
        self.window = CommandWindow(self, self.game)