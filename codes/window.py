import math
import random

import pygame

from codes.ui import CLR_BODY, CLR_BORDER, CLR_CLOSE, CLR_DARK


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
                    self.game.close_window(self)
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

    def place_files(self):
        for file in self.files:
            file.owner_window = self
            file.child = True
            file.pos = (self.rect.x + file.ref_pos[0], self.rect.y + file.ref_pos[1])

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos): return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                self.game.close_directory_window(self)
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
        self.place_files()
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
        self.light = game.light
        super().__init__(file, game, size, self.current_text(game))

    def current_text(self, game):
        return game.asset['txt/Tx7y1' if game.light else 'txt/Tx7y1_']

    def sync_text(self):
        if self.light == self.game.light: return
        self.light = self.game.light
        self.text = self.current_text(self.game)

    def update(self, event):
        super().update(event)
        self.sync_text()

    def tick(self, dt):
        self.sync_text()

    def render(self):
        self.sync_text()
        super().render()

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
                self.game.close_window(self)
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
        self.image = self.img[self.index]

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos):
                return

        if self.file is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_rect.collidepoint(event.pos):
                    self.game.close_window(self)
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
class PhaseWindow(ImgWindow):
    def __init__(self, file, game, size, img):
        super().__init__(file, game, size, img)
        self.phase = 0
        self.phases = [0, 1, 2, 3, 4, 5, 0]
        self.dates = [
            '19.01.02',
            '19.01.06',
            '19.01.09',
            '19.01.15',
            '19.01.21',
            '19.01.26',
            '19.01.30',
        ]
        self.index = self.phases[self.phase]
        self.image = self.img[self.index]

    def update(self, event):
        super().update(event)

        width = self.game.screen.get_width()
        max_x = max(1, width - self.rect.w)
        x = max(0, min(self.rect.x, max_x))

        self.phase = round(x / max_x * (len(self.phases) - 1))
        self.index = self.phases[self.phase]
        self.image = self.img[self.index]

    def render(self):
        Window.render(self)
        self.game.screen.blit(self.image, self.rect)

        date = self.game.font2.render(self.dates[self.phase], False, CLR_BORDER)
        self.game.screen.blit(date, (self.rect.x + 5, self.rect.bottom - 12))

class ClockWindow(Window):
    def __init__(self, file, game, size=(150, 150)):
        super().__init__(file, game, size)
        self.hour = 0
        self.minute = 0

    def update(self, event):
        super().update(event)

        if self.file is None: return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self not in self.game.windows: return
            if not self.is_top(event.pos): return
            if not self.rect.collidepoint(event.pos): return

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

        pygame.draw.rect(self.game.screen, CLR_DARK, (self.rect.x, self.rect.y, self.rect.w, self.rect.h))

        for i in range(60):
            angle = math.radians(i * 6 - 90)
            outer_x = cx + math.cos(angle) * radius
            outer_y = cy + math.sin(angle) * radius

            if i % 5 == 0:
                inner = radius - 10
                width = 2
                color = CLR_DARK
            else:
                inner = radius - 5
                width = 1
                color = CLR_BORDER

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
            text = self.game.font2.render(num, True, CLR_BORDER)
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

        pygame.draw.line(self.game.screen, CLR_BORDER, (cx, cy), (hx, hy), 5)
        pygame.draw.line(self.game.screen, CLR_BORDER, (cx, cy), (mx, my), 3)
        pygame.draw.circle(self.game.screen, CLR_BORDER, (cx, cy), 5)

        time_text = '{:02d}:{:02d}'.format(self.hour if self.hour != 0 else 12, self.minute)
        surf = self.game.font.render(time_text, True, CLR_BORDER)
        self.game.screen.blit(
            surf,
            (cx - surf.get_width() // 2, self.rect.bottom - 12)
        )

class LockerWindow(Window):
    def __init__(self, file, game, size, password, _max, initpt, initsz, initpd):
        super().__init__(file, game, size)
        self.password = password
        self.length = len(self.password)
        self.nums = [0 for _ in range(self.length)]
        self.inputPW = ''
        self.initpt = initpt; self.initsz = initsz; self.initpd = initpd
        self.max = _max

    @property
    def slot_rect(self):
        ptx = self.initpt[0]; pty = self.initpt[1]
        szx = self.initsz[0]; szy = self.initsz[1]
        pd = self.initpd
        return [pygame.Rect(self.rect.x + ptx + i * (szx + pd), self.rect.y + pty, szx, szy) for i in range(self.length)]

    def fit_text(self, text, rect, color=(10, 15, 22), margin=4):
        surf = self.game.font3.render(text, True, color)

        max_w = rect.w - margin * 2
        max_h = rect.h - margin * 2

        scale = min(max_w / surf.get_width(), max_h / surf.get_height())
        new_size = (
            int(surf.get_width() * scale),
            int(surf.get_height() * scale)
        )

        return pygame.transform.smoothscale(surf, new_size)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos):
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                self.game.close_window(self)
                return
            if self.titlebar_rect.collidepoint(event.pos):
                self.dragging = True
                self._drag_off = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                if self in self.game.windows:
                    self.game.windows.remove(self)
                    self.game.windows.append(self)
            for i in range(self.length):
                if self.slot_rect[i].collidepoint(event.pos):
                    self.nums[i] = (self.nums[i] + 1) % self.max
                    self.game.asset['sfx/tick'].play()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] - self._drag_off[0]
            self.rect.y = event.pos[1] - self._drag_off[1]

        self.inputPW = ''.join(str(i) for i in self.nums)
        if self.inputPW == self.password: self.game.lockToOpen(self)

    def render(self):
        super().render()

        for i, rect in enumerate(self.slot_rect):
            pygame.draw.rect(self.game.screen, '#FFFFFF', rect)

            text = self.fit_text(str(self.nums[i]), rect)
            text_rect = text.get_rect(center=rect.center)

            self.game.screen.blit(text, text_rect)
class ImgLockerWindow(LockerWindow):
    def __init__(self, file, game, size, password, img, _max, initpt, initsz, initpd):
        super().__init__(file, game, size, password, _max, initpt, initsz, initpd)
        self.img = img

    def render(self):
        Window.render(self)
        self.game.screen.blit(self.img, self.rect)
        for i, rect in enumerate(self.slot_rect):
            text = self.fit_text(str(self.nums[i]), rect)
            text_rect = text.get_rect(center=rect.center)

            self.game.screen.blit(text, text_rect)

class LoaderWindow(Window):
    def __init__(self, file, game, spd=(0, 3), comment=None, size=(100, 60)):
        super().__init__(file, game, size)
        self.load = 0
        self.spd = spd
        self.comment = comment
        self.size = size

    def tick(self, dt):
        self.load += random.randrange(self.spd[0], self.spd[1])
        self.load = min(self.load, self.loader_rect.w)
        if self.load >= self.loader_rect.w:
            self.game.close_window(self)
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
            self.game.close_window(self)

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

        elif event.type == pygame.KEYDOWN and self.active and self.game.is_active_window(self):
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

class ConsoleWindow(Window):
    def __init__(self, file, game, size=(280, 160), max_lines=200):
        super().__init__(file, game, size)
        self.lines = []
        self.max_lines = max_lines
        self.line_h = game.font2.get_height() + 2
        self.scroll = 0

    def max_scroll(self):
        visible_rows = max(1, self.rect.h // self.line_h)
        return max(0, len(self.lines) - visible_rows)

    def clamp_scroll(self):
        self.scroll = max(0, min(self.scroll, self.max_scroll()))

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_top(event.pos):
                return

            if self.file is not None and event.button == 1:
                if self.close_rect.collidepoint(event.pos):
                    self.game.close_window(self)
                    return

                if self.titlebar_rect.collidepoint(event.pos):
                    self.dragging = True
                    self._drag_off = (
                        event.pos[0] - self.rect.x,
                        event.pos[1] - self.rect.y
                    )
                    if self in self.game.windows:
                        self.game.windows.remove(self)
                    self.game.windows.append(self)

        elif event.type == pygame.MOUSEWHEEL:
            pos = self.game.mouse_pos()
            if self.is_top(pos) and (self.rect.collidepoint(pos) or self.titlebar_rect.collidepoint(pos)):
                self.scroll += event.y
                self.clamp_scroll()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] - self._drag_off[0]
            self.rect.y = event.pos[1] - self._drag_off[1]

    def add_line(self, s: str):
        if s == '':
            self.lines.append('')
            if len(self.lines) > self.max_lines: self.lines = self.lines[len(self.lines) - self.max_lines:]
            self.clamp_scroll()
            return

        max_w = self.rect.w - 10
        words = s.split(' ')
        cur = ""

        for w in words:
            test = (cur + " " + w).strip()
            if self.game.font2.size(test)[0] <= max_w: cur = test
            else: self.lines.append(cur); cur = w

        if cur: self.lines.append(cur)

        if len(self.lines) > self.max_lines:
            over = len(self.lines) - self.max_lines
            self.lines = self.lines[over:]

        self.clamp_scroll()

    def render(self):
        super().render()
        self.clamp_scroll()

        visible_rows = max(1, self.rect.h // self.line_h)
        start = max(0, len(self.lines) - visible_rows - self.scroll)
        end = start + visible_rows

        for i, line in enumerate(self.lines[start:end]):
            surf = self.game.font2.render(line, True, (10, 15, 22))
            self.game.screen.blit(
                surf,
                (self.rect.x + 5, self.rect.y + 5 + i * self.line_h)
            )
class LogWindow(ConsoleWindow):
    def __init__(self, file, game):
        super().__init__(file, game, size=(360, 220), max_lines=240)
        self.script = [
            '[01/15 02:36] session restore started',
            '[01/15 02:37] mkdir .hidden',
            '[01/15 02:38] copy cmd.sys .hidden/cmd.sys',
            '[01/15 02:38] copy cmd_note.txt .hidden/cmd_note.txt',
            '[01/15 02:40] hidden directory created by user',
            '[01/15 02:40] set hidden=true',
            '[01/15 02:40] remove directory from visible index',
            '[01/15 02:41] bind visibility to directory creation point',
            '[01/15 02:41] user note: search by the moment it disappeared',
            '[01/15 02:43] unknown access request detected',
            '[01/15 02:43] request denied',
            '[01/15 02:43] request denied',
            '[01/15 02:44] request denied',
            '[01/15 02:44] request accepted',
            '[01/15 02:44] user note: i moved cmd before it could use it',
            '[01/15 02:45] system warning: hidden entry accessed by non-user process',
            '[01/15 02:46] system warning: process is still active'
        ]
        self.reset_log()

    def reset_log(self):
        self.lines.clear()
        self.scroll = 0
        self.state = 'prompt'
        self.index = 0
        self.elapsed = 0
        self.finished = False
        self.add_line('last session was not closed properly.')
        self.add_line('restore previous input? y/n')

    def update(self, event):
        super().update(event)
        if self not in self.game.windows or event.type != pygame.KEYDOWN or not self.game.is_active_window(self): return
        if self.state == 'prompt':
            if event.key == pygame.K_y:
                self.state = 'restore'
                self.add_line('')
                self.add_line('restoring session...')
                self.add_line('')
                self.game.asset['sfx/open'].play()
            elif event.key == pygame.K_n:
                self.state = 'done'
                self.add_line('restore aborted')
                self.add_line('press r to reload')
                self.game.asset['sfx/locked'].play()
        elif self.state == 'done' and event.key == pygame.K_r:
            self.reset_log()
            self.game.asset['sfx/tick'].play()

    def tick(self, dt):
        if self.state != 'restore': return
        self.elapsed += dt
        if self.elapsed < 280: return
        self.elapsed = 0
        if self.index < len(self.script):
            line = self.script[self.index]
            self.add_line(line)
            self.index += 1
            self.game.asset['sfx/tick'].play()
            return
        if not self.finished:
            self.finished = True
            self.state = 'done'
            self.add_line('')
            self.add_line('restore complete')
            self.add_line('press r to replay')
class CmdWindow(ConsoleWindow):
    def __init__(self, file, game):
        super().__init__(file, game, size=(360, 220), max_lines=240)
        self.input = ''
        self.booted = False
        self.commands = self.game.commands
        self.sig_dir = None
        self.key_dir = None
        self.ptr_dir = None
        self.access_elapsed = 0
        self.access_step = -1
        self.dont_elapsed = 0
        self.dont_tick = 0

    def boot(self):
        if self.booted: return
        self.booted = True
        self.add_line('.hidden/cmd')
        self.add_line('')
        self.add_line('session: restored')
        self.add_line('authority: partial')
        self.add_line('visible index: corrupted')
        self.add_line('hidden index: unavailable')
        self.add_line('')
        self.add_line('type "help"')

    def update(self, event):
        super().update(event)

        if self not in self.game.windows: return

        self.boot()

        if event.type != pygame.KEYDOWN or not self.game.is_active_window(self): return
        if self.access_step != -1: return
        if event.key == pygame.K_BACKSPACE: self.input = self.input[:-1]
        elif event.key == pygame.K_RETURN:
            command = self.input.strip()
            self.add_line('> ' + command)
            self.input = ''
            self.run_command(command)
        elif event.key == pygame.K_ESCAPE: self.input = ''
        elif event.unicode and event.unicode.isprintable(): self.input += event.unicode

    def tick(self, dt):
        if self.access_step == -1: return

        self.access_elapsed += dt

        if self.access_step == 0 and self.access_elapsed >= 850:
            self.add_line('ROOT channel opened.')
            self.add_line('authority: ROOT')
            self.add_line('session privilege escalated.')
            self.add_line('')
            self.game.asset['sfx/open'].play()
            self.access_step = 1
            self.access_elapsed = 0
            return

        if self.access_step == 1 and self.access_elapsed >= 1050:
            self.add_line('WARNING: non-user process attached.')
            self.add_line('WARNING: session authority unstable.')
            self.add_line('WARNING: root channel is not empty.')
            self.add_line('')
            self.game.asset['sfx/locked'].play()
            self.access_step = 2
            self.access_elapsed = 0
            return

        if self.access_step == 2 and self.access_elapsed >= 1200:
            self.game.light = False
            self.access_step = 3
            self.access_elapsed = 0
            return

        if self.access_step == 3 and self.access_elapsed >= 1700:
            self.add_line('REQUEST DETECTED')
            self.add_line('')
            self.game.asset['sfx/tick'].play()
            self.access_step = 4
            self.access_elapsed = 0
            return

        if self.access_step == 4 and self.access_elapsed >= 900:
            self.access_step = 5
            self.access_elapsed = 0
            self.dont_elapsed = 0
            self.dont_tick = 0
            return

        if self.access_step == 5:
            self.dont_elapsed += dt
            self.dont_tick += dt

            while self.dont_tick >= 70 and self.dont_elapsed <= 3000:
                self.dont_tick -= 70
                self.add_line('REQUEST DENIED')
                self.game.asset['sfx/tick'].play()

            if self.dont_elapsed >= 3000:
                self.access_step = 6
                self.access_elapsed = 0
                self.dont_elapsed = 0
                self.dont_tick = 0
                self.add_line('')
            return

        if self.access_step == 6 and self.access_elapsed >= 1200:
            self.add_line('REQUEST ACCEPTED')
            self.game.asset['sfx/locked'].play()
            self.add_line('')
            self.access_step = -1
            self.access_elapsed = 0
            self.dont_elapsed = 0
            self.dont_tick = 0

    def render(self):
        super().render()

        prompt = '> ' + self.input
        if pygame.time.get_ticks() // 400 % 2 == 0:
            prompt += '_'

        pygame.draw.rect(
            self.game.screen,
            CLR_BODY,
            (self.rect.x + 2, self.rect.bottom - self.line_h - 5, self.rect.w - 4, self.line_h + 4)
        )

        surf = self.game.font2.render(prompt, True, (10, 15, 22))
        self.game.screen.blit(surf, (self.rect.x + 5, self.rect.bottom - self.line_h - 3))

    def run_command(self, raw):
        if not raw: return

        parts = raw.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd not in self.commands:
            self.add_line('unknown command')
            self.game.asset['sfx/locked'].play()
            self.add_line('')
            return

        if not self.commands[cmd]:
            self.add_line(cmd + ': command locked')
            self.game.asset['sfx/locked'].play()
            self.add_line('')
            return

        {
            'help': self.cmd_help,
            'status': self.cmd_status,
            'scan': self.cmd_scan,
            'open': self.cmd_open,
            'decrypt': self.cmd_decrypt,
            'access': self.cmd_access
        }[cmd](args)

        self.add_line('')

    def cmd_open(self, args):
        if not args:
            self.add_line('usage: open [entry]')
            return

        if not self.cache_exists():
            self.add_line('cache missing')
            self.add_line('run scan first')
            return

        target = args[0].lower()

        if target == '.sig': self.open_sig_dir(); return
        elif target == '.key': self.open_key_dir(); return

        self.add_line(target + ': entry not found')

    def open_sig_dir(self):
        from codes.file import Directory, ImgLocker, Sys, Text

        if self.sig_dir is None:
            self.sig_dir = Directory(self.game, '.sig', (320, 240), [
                ImgLocker(self.game, 'sig_wire', (5, 0), '101', 2, (56, 47), (21, 30), 9, True),
                Directory(self.game, 'decrypt', (55, 0), [
                    Sys(self.game, 'decrypt', (5, 0), True, True),
                    Text(self.game, 'decrypt_note', (55, 0), True, True),
                ], False, True)
            ], True, True, (130, 70))

        self.open_virtual_dir(self.sig_dir)
        self.add_line('opening hidden directory: .sig')

    def open_key_dir(self):
        from codes.file import Directory, Text, Sys, ImgLocker

        if self.key_dir is None:
            self.key_dir = Directory(self.game, '.key', (320, 240), [
                Sys(self.game, 'AUTHKEY', (5, 0), False, True),
                Text(self.game, 'key_note', (55, 0), True, True),
                ImgLocker(self.game, 'key_wire', (105, 0), '10100', 2, (54, 47), (21, 30), 9, True, True),
            ], True, True, (130, 70))

        self.open_virtual_dir(self.key_dir)
        self.add_line('opening hidden directory: .key')

    def open_virtual_dir(self, directory):
        self.game.open_virtual_dir(directory)

    def cmd_help(self, args):
        self.add_line('help: show instructions for the commands')
        self.add_line('status: show current session state')
        self.add_line('scan: scan hidden cache entries')
        self.add_line('open [entry]: open readable hidden entry')
        self.add_line('decrypt [entry] [key]: restore encrypted entry')
        self.add_line('access [target] [pointer] [password]: access protected system target')

    def cmd_status(self, args):
        cache_found = self.cache_exists()
        self.add_line('authority: partial')
        self.add_line('visible index: corrupted')
        self.add_line('hidden index: {}'.format('loaded' if cache_found else 'unavailable'))
        self.add_line('cache: {}'.format('recovered' if cache_found else 'missing'))
        self.add_line('')

        self.add_line('available commands:')
        for name, opened in self.commands.items():
            if opened: self.add_line(name)

        self.add_line('')
        self.add_line('locked commands:')
        for name, opened in self.commands.items():
            if not opened: self.add_line(name)

    def cmd_scan(self, args):
        if self.cache_exists():
            self.add_line('scan complete.')
            self.add_line('cache already recovered.')
            self.game.asset['sfx/locked'].play()
            return

        hidden = self.hidden_dir()
        if not hidden:
            self.add_line('scan failed.')
            self.add_line('.hidden not mounted')
            self.game.asset['sfx/locked'].play()
            return

        from codes.file import Text

        cache = Text(self.game, '.cache', (105, 0), True, True)
        hidden.files.append(cache)
        hidden.refresh_layout()

        if cache not in self.game.texts:
            self.game.texts.append(cache)

        self.add_line('visible index damaged.')
        self.add_line('hidden cache recovered.')
        self.add_line('')
        self.add_line('new visible file:')
        self.add_line('.cache.txt')
        self.game.asset['sfx/open'].play()

    def cmd_decrypt(self, args):
        if not self.game.commands['decrypt']:
            self.add_line('decrypt module incomplete')
            return

        if len(args) < 2:
            self.add_line('usage: decrypt [entry] [key]')
            return

        target, key = (arg.lower() for arg in args[:2])

        if target != '.ptr':
            self.add_line('decrypt failed.')
            self.add_line('unencrypted file.')
            return

        if key != '.auth42.exe':
            self.add_line('decrypt failed.')
            self.add_line('wrong key.')
            return

        if not self.game.auth_key:
            self.add_line('decrypt failed.')
            self.add_line('key not verified.')
            return

        if self.game.ptr_decrypted:
            self.add_line('.ptr already decrypted.')
            self.add_line('pointer: ROOT')
            return

        self.game.ptr_decrypted = True
        self.add_line('decrypting .ptr with .auth42.exe...')
        self.add_line('.ptr decrypted.')
        self.add_line('pointer restored: ROOT')
        self.game.asset['sfx/open'].play()

    def cmd_access(self, args):
        if not self.game.commands['access']:
            self.add_line('access module incomplete')
            return

        if len(args) < 3:
            self.add_line('usage: access [target] [pointer] [auth password]')
            return

        target, pointer, password = (arg.lower() for arg in args[:3])

        if target != 'root':
            self.add_line('access failed.')
            self.add_line('unknown target.')
            return

        if pointer != '.ptr':
            self.add_line('access failed.')
            self.add_line('unknown pointer.')
            return

        if not self.game.ptr_decrypted:
            self.add_line('access failed.')
            self.add_line('pointer encrypted.')
            return

        if password != '468042':
            self.add_line('access failed.')
            self.add_line('wrong password.')
            return

        if self.access_step != -1:
            self.add_line('access sequence already running.')
            return

        self.add_line('access request accepted.')
        self.add_line('target: ROOT')
        self.add_line('pointer: .ptr')
        self.add_line('auth password verified.')
        self.add_line('opening protected channel...')
        self.access_elapsed = 0
        self.access_step = 0
        self.game.asset['sfx/tick'].play()

    def hidden_dir(self):
        return next((d for d in self.game.directories if d.name == '.hidden'), None)

    def cache_exists(self):
        hidden = self.hidden_dir()
        return bool(hidden and any(f.name == '.cache' for f in hidden.files))


