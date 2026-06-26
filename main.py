import pygame
import sys
from codes.util import DoubleClick, loadImg, loadText, alphaRect, LayeredLooper, loadImgs
from codes.funcs import lm, lto, dl, plc, cmc

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

        self.asset = {
            'cursor': pygame.transform.scale(pygame.image.load('asset/img/cursor.png'), (24, 24)),
            'lock': loadImg('lock.png', [0], 2, 1)[0].convert_alpha(),

            'icon/directory': loadImg('icon.png', [0], 2, 2)[0],
            'icon/image': loadImg('icon.png', [1], 2, 2)[0],
            'icon/txt': loadImg('icon.png', [2], 2, 2)[0],
            'icon/etc': loadImg('icon.png', [3], 2, 2)[0],

            'txt/readme': loadText('readme.txt'),
            'txt/L3I1l7': loadText('L3I1l7.txt'),
            'txt/empty': loadText('empty1.txt'),
            'txt/em?ty': loadText('empty2.txt'),
            'txt/em?t\'/': loadText('empty3.txt'),
            'txt/empty.': loadText('empty4.txt'),
            'txt/Tx7y1': loadText('Tx7y1.txt'),
            'txt/2nasHf': loadText('2nasHf.txt'),
            'txt/9o12': loadText('9o12.txt'),
            'txt/align': loadText('align.txt'),
            'txt/encoded': loadText('encoded.txt'),

            'image/lock': pygame.transform.scale(loadImg('lock.png', [0], 2, 1)[0], (55, 55)),
            'image/1aaad4': pygame.image.load('asset/img/1aaad4.png'),
            'image/enyl1': pygame.image.load('asset/img/enyl1.png'),
            'image/kf3s': pygame.image.load('asset/img/kf3s.png'),
            'image/3qy4': pygame.image.load('asset/img/3qy4.png'),
            'image/33256': pygame.image.load('asset/img/33256.png'),
            'image/y6c20': pygame.image.load('asset/img/y6c20.png'),
            'image/o771a': loadImg('pw.png', [0], 3, 2)[0],
            'image/fyw1': loadImg('pw.png', [1], 3, 2)[0],
            'image/z1p81': loadImg('pw.png', [2], 3, 2)[0],
            'image/ka31go': loadImg('pw.png', [3], 3, 2)[0],
            'image/s131p': loadImg('pw.png', [4], 3, 2)[0],
            'image/y30o1': loadImg('pw.png', [5], 3, 2)[0],
            'image/clock': loadImg('clock.png', range(1), 1, 1)[0],
            'image/moon': loadImg('moon.png', range(6), 2, 3),
            'image/calib': pygame.image.load('asset/img/calib.png'),
            'image/num': pygame.image.load('asset/img/num.png'),

            'sfx/locked': pygame.mixer.Sound('asset/sfx/locked.wav'),
            'sfx/open': pygame.mixer.Sound('asset/sfx/open.wav'),
            'sfx/crack': pygame.mixer.Sound('asset/sfx/crack.wav'),
            'sfx/bass': pygame.mixer.Sound('asset/sfx/bass.wav'),
            'sfx/c': pygame.mixer.Sound('asset/sfx/c.wav'),
            'sfx/tick': pygame.mixer.Sound('asset/sfx/tick.wav'),
            'sfx/ominous': pygame.mixer.Sound('asset/sfx/ominous.wav'),
            'sfx/reboot': pygame.mixer.Sound('asset/sfx/reboot.wav'),
        }
        self.asset['lock'].set_alpha(185)
        self.asset['sfx/bass'].set_volume(0.25)
        self.asset['sfx/c'].set_volume(0.5)
        self.asset['sfx/tick'].set_volume(0.05)
        for i in range(len(loadImgs('wire'))):
            self.asset['image/light' + str(i)] = loadImgs('wire')[i]

        self.crack_channels = [pygame.mixer.Channel(i) for i in range(2, 17)]
        self.crack_loop = LayeredLooper(self.asset['sfx/crack'], self.crack_channels, interval_ms=1500, fade_ms=150)
        self.c_channels = [pygame.mixer.Channel(i) for i in range(17, 41)]
        self.c_loop = LayeredLooper(self.asset['sfx/c'], self.c_channels, interval_ms=13)
        self.bgm_channel = pygame.mixer.Channel(1)
        self.bgm_playing = False
        self.suppress_bgm = False

        self.font = pygame.font.Font('asset/font/OCR-B.ttf', 7)
        self.font2 = pygame.font.Font('asset/font/OCR-B.ttf', 8)
        self.font3 = pygame.font.Font('asset/font/OCR-B.ttf', 35)
        self.font4 = pygame.font.Font('asset/font/ChicagoFLF.ttf', 10)

        self.directories = []
        self.images = []
        self.texts = []
        self.etcs = []
        self.windows = []

        self.map = 1
        self.light = True

        pygame.mouse.set_visible(False)

        self.console = None

    def loadmap(self): lm(self)

    def lockToOpen(self): lto(self)

    def download(self, name): dl(self, name)

    def padLockClear(self): plc(self)

    def checkMoonClock(self): cmc(self)

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
            if type(self.map) == int: self.loadmap(); self.map = (self.map, )#; self.asset['sfx/reboot'].play()
            if self.map[0] == 0:
                if not self.light: self.asset['Tx7y1'] = loadText('Tx7y1_.txt')
            if self.map[0] == 1: self.checkMoonClock()

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
                if self.dc(event): dc_pos = self.dc.pos
                for wnd in reversed(self.windows):
                    wnd.update(event)

            for directory in self.directories:
                directory.update(dc_pos)
            for image in self.images:
                image.update(dc_pos)
            for text in self.texts:
                text.update(dc_pos)
            for etc in self.etcs:
                etc.update(dc_pos)
            for window in self.windows:
                window.render()
                window.tick(self.FPSCLOCK.get_time())

            if dc_pos: self.dc.reset()

            try:
                open_crack = any(w.file.name == 'y6c20' for w in self.windows)

                self.crack_loop.set_enabled(open_crack)
                self.crack_loop.update()
            except AttributeError:
                pass

            self.c_loop.set_enabled(not self.light)
            self.c_loop.update()

            if not self.bgm_playing and not self.suppress_bgm:
                self.bgm_channel.play(self.asset['sfx/bass'], loops=-1)
                self.bgm_playing = True

            self.screen.blit(self.asset['cursor'], self.to_game_pos(pygame.mouse.get_pos()))
            if not self.light: alphaRect(self.screen, (0, 0, 0, 170), (0, 0, *self.BASE_SIZE))
            self.present()


Game().main()
