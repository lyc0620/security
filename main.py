import sys

import pygame

from codes.assets import load_assets, load_fonts
from codes.file import (
    Cmd,
    Dummy,
    ImgLocker,
    Directory,
    Image,
    InteractiveImg,
    LockImg,
    Locker,
    Log,
    PadLock,
    PhaseImg,
    Rotor,
    Sys,
    Text,
    TransparentImg,
    Tx7y1,
)
from codes.util import DoubleClick, LayeredLooper, alphaRect, detectCover, loadImg
from codes.window import SystemRebootWindow


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(64)

        self.BASE_SIZE = (900, 650)
        self.display = pygame.display.set_mode(self.BASE_SIZE, pygame.RESIZABLE)
        self.screen = pygame.Surface(self.BASE_SIZE)
        self.view_rect = pygame.Rect(0, 0, *self.BASE_SIZE)
        self.update_view_rect()
        self.FPSCLOCK = pygame.time.Clock()
        pygame.display.set_caption('Security')
        self.dc = DoubleClick()

        self.asset = load_assets()
        fonts = load_fonts()
        self.font = fonts['font']
        self.font2 = fonts['font2']
        self.font3 = fonts['font3']
        self.font4 = fonts['font4']

        self.crack_channels = [pygame.mixer.Channel(i) for i in range(2, 17)]
        self.crack_loop = LayeredLooper(self.asset['sfx/crack'], self.crack_channels, interval_ms=1500, fade_ms=150)
        self.c_channels = [pygame.mixer.Channel(i) for i in range(17, 41)]
        self.c_loop = LayeredLooper(self.asset['sfx/c'], self.c_channels, interval_ms=13)
        self.bgm_channel = pygame.mixer.Channel(1)
        self.bgm_playing = False
        self.suppress_bgm = False
        # self.commands = {
        #     'help': True,
        #     'status': True,
        #     'scan': True,
        #     'open': True,
        #     'decrypt': False,
        #     'access': False
        # }
        #
        # self.auth_key = False
        # self.ptr_decrypted = False

        self.commands = {
            'help': True,
            'status': True,
            'scan': True,
            'open': True,
            'decrypt': True,
            'access': True
        }

        self.auth_key = True
        self.ptr_decrypted = True

        self.directories = []
        self.images = []
        self.texts = []
        self.etcs = []
        self.windows = []

        self.map = 1
        self.loaded_map = None
        self.light = True
        self.console = None

        pygame.mouse.set_visible(False)

    def reset_files(self):
        self.directories = []
        self.images = []
        self.texts = []
        self.etcs = []
        self.windows = []

    def file_group(self, file):
        if file.objType == 'directory': return self.directories
        if file.objType in ('image', 'lock'): return self.images
        if file.objType == 'txt': return self.texts
        return self.etcs

    def register_file(self, file):
        group = self.file_group(file)
        if file not in group: group.append(file)

    def unregister_file(self, file):
        if file.objType == 'directory':
            for child in file.files[:]: self.unregister_file(child)
        if getattr(file, 'window', None): self.close_window(file.window)
        for group in (self.directories, self.images, self.texts, self.etcs):
            if file in group: group.remove(file)

    def open_file(self, file):
        if file.objType == 'directory':
            self.open_directory(file)
            return
        file.open = True
        file.window.rect.topleft = (file.pos[0] - 10, file.pos[1] - 10)
        if file.window not in self.windows: self.windows.append(file.window)

    def open_directory(self, directory, window_pos=None):
        directory.open = True
        directory.refresh_layout()
        directory.window.rect.topleft = window_pos or (directory.pos[0] - 10, directory.pos[1] - 10)
        if directory.window not in self.windows: self.windows.append(directory.window)
        for file in directory.files: self.register_file(file)

    def open_virtual_dir(self, directory):
        directory.refresh_layout()
        directory.window.rect.topleft = (directory.pos[0] - 10, directory.pos[1] - 10)
        if directory.window not in self.windows: self.windows.append(directory.window)
        for file in directory.files: self.register_file(file)

    def close_window(self, window):
        if window.file is not None: window.file.open = False
        if window in self.windows: self.windows.remove(window)

    def close_directory_window(self, window):
        if window.file is not None: window.file.open = False
        for file in window.files[:]: self.unregister_file(file)
        if window in self.windows: self.windows.remove(window)

    def is_active_window(self, window):
        return bool(self.windows and self.windows[-1] is window)

    def focus_window_at(self, pos):
        window = next((
            w for w in reversed(self.windows)
            if w.rect.collidepoint(pos) or w.titlebar_rect.collidepoint(pos)
        ), None)

        if window and window in self.windows:
            self.windows.remove(window)
            self.windows.append(window)

    def mouse_pos(self):
        return self.to_game_pos(pygame.mouse.get_pos())

    def loadmap(self):
        self.reset_files()
        if self.map == 0:
            self.directories = [Directory(self, 'DRIVE', (200, 200), [
                Directory(self, 'sys', (5, 0), [
                    Sys(self, 'sysDownload', (5, 0), True, True)
                ], False, True, (100, 70)),
                Tx7y1(self, 'Tx7y1', (55, 0), True, True),
                Directory(self, 'empty', (105, 0), [
                    Text(self, 'empty', (5, 0), True, True),
                    Directory(self, 'empty', (55, 0), [
                        Text(self, 'em?ty', (5, 0), True, True),
                        Directory(self, 'empty', (55, 0), [
                            Text(self, 'em?t\'/', (5, 0), True, True),
                            Directory(self, 'empty', (55, 0), [
                                Text(self, 'empty.', (5, 0), True, True),
                                Image(self, 'y6c20', (55, 0), True, True)
                            ], True, True, (155, 70))
                        ], True, True, (150, 70))
                    ], True, True, (150, 70))
                ], True, True, (150, 70)),
                Directory(self, '2n1', (5, 60), [
                    Image(self, 'y30o1', (5, 0), True, True),
                    Image(self, 'o771a', (55, 0), True, True),
                    Image(self, 'fyw1', (105, 0), True, True),
                    Image(self, 's131p', (5, 60), True, True),
                    Image(self, 'ka31go', (55, 60), True, True),
                    Image(self, 'z1p81', (105, 60), True, True),
                ], True, True, (200, 120)),
                Locker(self, 'LTS', (55, 60), '640', True, True)
            ], False, size=(200, 120)),
            Directory(self, 'a1nd2', (700, 100), [
                Image(self, '3qy4', (5, 0), True, True),
                Image(self, '1aaad4', (55, 0), True, True),
                Image(self, 'kf3s', (105, 0), True, True),
                Image(self, '33256', (5, 60), True, True),
                Text(self, 'L3I1l7', (55, 60), True, True),
                TransparentImg(self, 'enyl1', (105, 60), True, True)
            ], True, size=(200, 120))]
            self.texts = [Text(self, 'readme', (500, 420), True)]
            self.images = [LockImg(self, 'lock', (300, 400), True)]
            self.etcs = []

        elif self.map == 1:
            self.directories = [Directory(self, 'dir', (500, 350), [
                PadLock(self, 'AuthN', (5, 0), True, [[1, 0, 0], [0, 0, 1], [1, 1, 0]], True),
                Directory(self, 'Auth', (55, 0), [
                    Rotor(self, 'rotor', (5, 0), True, True),
                    Text(self, 'align', (55, 0), True, True),
                    Text(self, 'encoded', (105, 0), True, True),
                    Image(self, 'calib', (155, 0), True, True)
                ], True, True),
            ], True, False, (200, 70))]
            self.texts = []
            self.images = [
                InteractiveImg(self, 'clock', (620, 200), True),
                Image(self, 'num', (170, 440), True),
                InteractiveImg(self, 'moon', (105, 140), True),
                PhaseImg(self, 'phase', (160, 75), True)
            ]
            self.etcs = [Log(self, 'log', (700, 420), False)]

    def lockToOpen(self, lock_window=None):
        if self.map == 0:
            if lock_window is not None and lock_window.file.name == 'LTS':
                self.asset['sfx/open'].play()
                for directory in self.directories:
                    if directory.name == 'sys': directory.interaction = True
                lock_window.password = 0
                return

            drive = next((d for d in self.directories if d.name == 'DRIVE' and not d.interaction), None)
            if not drive: return

            if detectCover(self, ['1aaad4', 'enyl1'], 'image', (49, 45), (3, 3)):
                self.asset['sfx/open'].play()
                drive.interaction = True
                old_lock = next((image for image in self.images if image.name == 'lock'), None)
                pos = old_lock.window.rect.topleft if old_lock else (300, 400)
                if old_lock: self.unregister_file(old_lock)
                self.asset['image/lock'] = pygame.transform.scale(loadImg('lock.png', [1], 2, 1)[0], (55, 55))
                lock = LockImg(self, 'lock', (300, 400), True)
                lock.window.rect.topleft = pos
                self.images.append(lock)
                self.windows.append(lock.window)
            else:
                self.asset['sfx/locked'].play()

        elif self.map == 1:
            if lock_window is not None:
                if lock_window.file.name == 'sig_wire':
                    self.asset['sfx/open'].play()
                    for directory in self.directories:
                        if directory.name == 'decrypt': directory.interaction = True
                    lock_window.password = 0
                elif lock_window.file.name == 'key_wire':
                    self.asset['sfx/open'].play()
                    for etc in self.etcs:
                        if etc.name == 'AUTHKEY': etc.interaction = True
                    lock_window.password = 0
                elif lock_window.file.name == 'wire7':
                    self.asset['sfx/open'].play()
                    for etc in self.etcs:
                        if etc.name == 'access': etc.interaction = True
                    lock_window.password = 0

    def download(self, file):
        if self.map == 0:
            if self.light:
                if file.name == 'sysDownload':
                    directory = next((d for d in self.directories if d.name == 'sys'), None)
                    if directory:
                        pos = directory.window.rect.topleft
                        directory.files = [f for f in directory.files if f.name != 'sysDownload']
                        for etc in self.etcs[:]:
                            if etc.name == 'sysDownload': self.unregister_file(etc)
                        directory.files.extend([
                            PadLock(self, 'reboot', (0, 0), True, [[1, 0, 0, 1, 1, 0], [0, 1, 0, 1, 0, 0], [1, 0, 0, 0, 0, 0]], True),
                            Text(self, '9o12', (50, 0), True, True),
                            Text(self, '2nasHf', (100, 0), True, True)
                        ])
                        self.open_directory(directory, pos)
                self.light = False
        elif self.map == 1:
            if file.name == 'decrypt':
                file.interaction = False
                self.commands['decrypt'] = True
                self.asset['sfx/open'].play()
            elif file.name == 'AUTHKEY':
                file.interaction = False
                self.auth_key = True
                self.asset['sfx/open'].play()
            elif file.name == 'access':
                self.commands['access'] = True
                self.asset['sfx/open'].play()

    def padLockClear(self):
        if self.map == 0:
            self.windows.clear()
            self.directories.clear()
            self.images.clear()
            self.texts.clear()
            self.etcs.clear()

            self.light = False
            self.suppress_bgm = True
            self.bgm_playing = False
            self.bgm_channel.stop()

            self.windows.append(SystemRebootWindow(None, self))

        elif self.map == 1:
            for etc in self.etcs:
                if etc.name == 'log': etc.interaction = True

    def makeHidden(self):
        return Directory(self, '.hidden', (705, 60), [
            Cmd(self, 'cmd', (5, 0), True, True),
            Text(self, 'cmd_note', (55, 0), True, True)
        ], True, size=(100, 70))

    def checkMoonClock(self):
        moon = None; clock = None

        for w in self.windows:
            if not w.file: continue
            if w.file.name == 'moon': moon = w.index
            elif w.file.name == 'clock': clock = (w.hour, w.minute)

        if moon == 3 and clock == (2, 40):
            if any(directory.name == '.hidden' for directory in self.directories): return
            self.asset['sfx/open'].play()
            self.directories.append(self.makeHidden())

    def update_view_rect(self):
        win_w, win_h = self.display.get_size()
        base_w, base_h = self.BASE_SIZE

        scale = min(win_w / base_w, win_h / base_h)
        view_w = int(base_w * scale)
        view_h = int(base_h * scale)

        self.view_rect = pygame.Rect(
            (win_w - view_w) // 2,
            (win_h - view_h) // 2,
            view_w,
            view_h
        )

    def to_game_pos(self, pos):
        x, y = pos

        if self.view_rect.w == 0 or self.view_rect.h == 0:
            return 0, 0

        gx = (x - self.view_rect.x) * self.BASE_SIZE[0] / self.view_rect.w
        gy = (y - self.view_rect.y) * self.BASE_SIZE[1] / self.view_rect.h

        gx = max(0, min(self.BASE_SIZE[0] - 1, int(gx)))
        gy = max(0, min(self.BASE_SIZE[1] - 1, int(gy)))

        return gx, gy

    def to_game_event(self, event):
        if hasattr(event, 'pos'):
            data = event.__dict__.copy()
            data['pos'] = self.to_game_pos(event.pos)
            return pygame.event.Event(event.type, data)
        return event

    def present(self):
        self.display.fill((0, 0, 0))
        scaled = pygame.transform.scale(self.screen, self.view_rect.size)
        self.display.blit(scaled, self.view_rect.topleft)
        pygame.display.update()

    def main(self):
        while True:
            if self.loaded_map != self.map:
                self.loadmap()
                self.loaded_map = self.map
            if self.map == 1:
                self.checkMoonClock()
                if self.auth_key and not any(etc.name == '.auth42' for etc in self.etcs):
                    self.etcs.append(Dummy(self, '.auth42', (400, 400)))
                if self.ptr_decrypted and not any(directory.name == 'access' for directory in self.directories):
                    self.directories.append(Directory(self, 'access', (350, 400), [
                        Text(self, 'access_note', (5, 0), True, True),
                        Directory(self, 'wire', (55, 0),
                                  list(Image(self, 'wire{}'.format(i), (5 + i % 4 * 50, i // 4 * 60), True, True) for i in range(7)) +
                                  [ImgLocker(self, 'wire7', (155, 60), '11010', 2, (9, 7), (21, 30), 9, True, True)],
                                  True, True),
                        Sys(self, 'access', (105, 0), False, True)
                    ], True))

            self.FPSCLOCK.tick(60)
            self.screen.fill((10, 15, 22))
            dc_pos = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    self.display = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    self.update_view_rect()
                    continue

                event = self.to_game_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.focus_window_at(event.pos)

                if self.dc(event): dc_pos = self.dc.pos
                for wnd in reversed(self.windows[:]): wnd.update(event)

            for directory in self.directories[:]: directory.update(dc_pos)
            for image in self.images[:]: image.update(dc_pos)
            for text in self.texts[:]: text.update(dc_pos)
            for etc in self.etcs[:]: etc.update(dc_pos)
            for window in self.windows[:]:
                window.render()
                window.tick(self.FPSCLOCK.get_time())

            if dc_pos: self.dc.reset()

            try:
                open_crack = any(w.file.name == 'y6c20' for w in self.windows)
                self.crack_loop.set_enabled(open_crack)
                self.crack_loop.update()
            except AttributeError: pass

            self.c_loop.set_enabled(not self.light)
            self.c_loop.update()

            if not self.bgm_playing and not self.suppress_bgm:
                self.bgm_channel.play(self.asset['sfx/bass'], loops=-1)
                self.bgm_playing = True

            self.screen.blit(self.asset['cursor'], self.mouse_pos())
            if not self.light: alphaRect(self.screen, (0, 0, 0, 170), (0, 0, *self.BASE_SIZE))
            self.present()


if __name__ == '__main__':
    Game().main()
