import pygame

from codes.util import loadImg, loadText


def load_assets():
    asset = {
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
        'txt/Tx7y1_': loadText('Tx7y1_.txt'),
        'txt/2nasHf': loadText('2nasHf.txt'),
        'txt/9o12': loadText('9o12.txt'),
        'txt/align': loadText('align.txt'),
        'txt/encoded': loadText('encoded.txt'),
        'txt/cmd_note': loadText('cmd_note.txt'),
        'txt/.cache': loadText('cache.txt'),
        'txt/decrypt_note.txt': loadText('decrypt_note.txt'),

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
        'image/phase': loadImg('moon.png', range(6), 2, 3),
        'image/calib': pygame.image.load('asset/img/calib.png'),
        'image/num': pygame.image.load('asset/img/num.png'),
        'image/wire': pygame.image.load('asset/img/wire.png'),

        'sfx/locked': pygame.mixer.Sound('asset/sfx/locked.wav'),
        'sfx/open': pygame.mixer.Sound('asset/sfx/open.wav'),
        'sfx/crack': pygame.mixer.Sound('asset/sfx/crack.wav'),
        'sfx/bass': pygame.mixer.Sound('asset/sfx/bass.wav'),
        'sfx/c': pygame.mixer.Sound('asset/sfx/c.wav'),
        'sfx/tick': pygame.mixer.Sound('asset/sfx/tick.wav'),
        'sfx/ominous': pygame.mixer.Sound('asset/sfx/ominous.wav'),
        'sfx/reboot': pygame.mixer.Sound('asset/sfx/reboot.wav'),
    }
    asset['lock'].set_alpha(185)
    asset['sfx/bass'].set_volume(0.25)
    asset['sfx/c'].set_volume(0.5)
    asset['sfx/tick'].set_volume(0.05)
    return asset


def load_fonts():
    return {
        'font': pygame.font.Font('asset/font/OCR-B.ttf', 7),
        'font2': pygame.font.Font('asset/font/OCR-B.ttf', 8),
        'font3': pygame.font.Font('asset/font/OCR-B.ttf', 35),
        'font4': pygame.font.Font('asset/font/ChicagoFLF.ttf', 10),
    }
