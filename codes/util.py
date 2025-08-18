import pygame
import random
import os

BASE_IMG_PATH = 'asset/img/'
BASE_TEXT_PATH = 'asset/txt/'

class DoubleClick:
    def __init__(self):
        self.time = 0
        self.armed = False
        self.last_pos = None
        self.pos = None

    def __call__(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False

        now = pygame.time.get_ticks()
        self.pos = event.pos

        if self.armed:
            if (now - self.time) <= 250 and self._dist2(self.pos, self.last_pos) <= 64:
                return True
            self.time = now
            self.last_pos = self.pos
            return False
        else:
            self.armed = True
            self.time = now
            self.last_pos = self.pos
            return False

    def reset(self):
        self.armed = False
        self.time = 0
        self.last_pos = None
        self.pos = None

    @staticmethod
    def _dist2(a, b):
        if a is None or b is None:
            return 10 ** 9
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

def splitImg(path, w, h):
    imgs = []
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    img_w, img_h = img.get_size()
    frame_w = img_w // w
    frame_h = img_h // h

    for j in range(h):
        for i in range(w):
            rect = pygame.Rect(i * frame_w, j * frame_h, frame_w, frame_h)
            frame = img.subsurface(rect).copy()
            imgs.append(frame)
    return imgs

def loadImg(path, index, w, h):
    imgs = splitImg(path, w, h)
    return [imgs[i] for i in index]

def loadText(path):
    with open(BASE_TEXT_PATH + path, 'r', encoding='utf-8') as f:
        texts = [line.rstrip('\n') for line in f]
    return texts

def detectCover(game, names, objtype, dif, buf):
    attr = {'directory': 'directories', 'image': 'images', 'txt': 'texts'}[objtype]
    objs = getattr(game, attr)

    pos = {o.name: o.window.rect.topleft for o in objs if o.name in names}
    if len(pos) < 2:
        return False

    (x1, y1), (x2, y2) = pos[names[0]], pos[names[1]]
    dx, dy = x2 - x1, y2 - y1

    return (abs(dx - dif[0]) <= buf[0]) and (abs(dy - dif[1]) <= buf[1])

def rgbToHex(rgb, *, include_hash=True, uppercase=True):
    def to_byte(x):
        if isinstance(x, float):
            x = round(x * 255)
        return max(0, min(255, int(x)))

    vals = [to_byte(v) for v in rgb]
    fmt = "{:02X}{:02X}{:02X}"
    s = fmt.format(*vals)
    if not uppercase:
        s = s.lower()
    return ("#" + s) if include_hash else s

def alphaRect(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

class LayeredLooper:
    def __init__(self, sound: pygame.mixer.Sound, channels, interval_ms=None, fade_ms=120, volume=0.45, jitter_ms=70):
        self.sound = sound
        self.channels = channels
        self.fade_ms = fade_ms
        self.volume = volume
        self.jitter_ms = jitter_ms
        self.enabled = False
        self._next_tick = 0

        # 길이 기반 기본 인터벌(겹침: 70%)
        if interval_ms is None:
            length_ms = int(self.sound.get_length() * 1000)
            interval_ms = int(length_ms * 0.7)
        self.interval_ms = interval_ms

        for ch in self.channels:
            ch.set_volume(self.volume)

    def set_enabled(self, on: bool):
        if on == self.enabled:
            return  # 상태 변화 없으면 아무 것도 안 함
        self.enabled = on
        if on:
            self._next_tick = pygame.time.get_ticks()  # 지금부터 스케줄링
        else:
            # 부드럽게 모두 끄기
            for ch in self.channels:
                ch.fadeout(self.fade_ms)
            self._next_tick = 0

    def update(self):
        if not self.enabled:
            return
        now = pygame.time.get_ticks()
        if now < self._next_tick:
            return

        # 빈 채널 하나만 사용해서 겹치기 레이어 추가
        ch = None
        for c in self.channels:
            if not c.get_busy():
                ch = c
                break
        if ch is not None:
            ch.play(self.sound, loops=0, fade_ms=self.fade_ms)

        # 다음 재생 예약 (지터 추가)
        jitter = random.randint(-self.jitter_ms, self.jitter_ms)
        self._next_tick = now + max(50, self.interval_ms + jitter)

def loadImgs(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(pygame.image.load(BASE_IMG_PATH + path + '/' + img_name))
    return images


if __name__ == '__main__': print(rgbToHex((10, 15, 22)))