import time
from codes.util import detectCover, loadImg
from codes.object import *

def lm(game):
    pygame.mixer.init()
    pygame.mixer.set_num_channels(64)
    if game.map == 0:
        game.directories = [Directory(game, 'DRIVE', (200, 200), [
            Directory(game, 'sys', (5, 0), [
                Sys(game, 'sysDownload', (5, 0), True, True)
            ], False, True, (100, 70)),
            Tx7y1(game, 'Tx7y1', (55, 0), True, True),
            Directory(game, 'empty', (105, 0), [
                Text(game, 'empty', (5, 0), True, True),
                Directory(game, 'empty', (55, 0), [
                    Text(game, 'em?ty', (5, 0), True, True),
                    Directory(game, 'empty', (55, 0), [
                        Text(game, 'em?t\'/', (5, 0), True, True),
                        Directory(game, 'empty', (55, 0), [
                            Text(game, 'empty.', (5, 0), True, True),
                            Image(game, 'y6c20', (55, 0), True, True)
                        ], True, True, (155, 70))
                    ], True, True, (150, 70))
                ], True, True, (150, 70))
            ], True, True, (150, 70)),
            Image(game, 'ka31go', (5, 60), True, True),
            Image(game, 'z1p81', (55, 60), True, True),
            Directory(game, '2n1', (105, 60), [
                Image(game, 'y30o1', (5, 0), True, True),
                Image(game, 'o771a', (55, 0), True, True),
                Image(game, 'fyw1', (105, 0), True, True),
                Image(game, 's131p', (5, 60), True, True),
                Locker(game, 'LTS', (55, 60), '640', True, True)
            ], True, True, (200, 120))
        ], False, size=(200, 120)),
                            Directory(game, 'a1nd2', (700, 100), [
                                Image(game, '3qy4', (5, 0), True, True),
                                Image(game, '1aaad4', (55, 0), True, True),
                                Image(game, 'kf3s', (105, 0), True, True),
                                Image(game, '33256', (5, 60), True, True),
                                Text(game, 'L3I1l7', (55, 60), True, True),
                                TransparentImg(game, 'enyl1', (105, 60), True, True)
                            ], True, size=(200, 120))]
        game.texts = [Text(game, 'readme', (500, 420), True)]
        game.images = [LockImg(game, 'lock', (300, 400), True)]
        game.etcs = []

    elif game.map == 1:
        game.directories = [Directory(game, 'dir', (500, 350), [
            PadLock(game, 'AuthN', (5, 0), True, [[1, 0, 0], [0, 0, 1], [1, 1, 0]], True),
            Directory(game, 'Auth', (55, 0), [
                Image(game, 'light0', (5, 0), True, True),
                Image(game, 'light1', (55, 0), True, True),
                Image(game, 'light2', (105, 0), True, True),
                Image(game, 'light3', (155, 0), True, True),
                Image(game, 'light4', (5, 60), True, True),
                Image(game, 'light5', (55, 60), True, True),
                Image(game, 'light6', (105, 60), True, True),
                Image(game, 'light7', (155, 60), True, True),
            ], True, True, (250, 140)),
            InteractiveImg(game, 'moon', (105, 0), True)
        ], True, False, (200, 70))]
        game.texts = [Text(game, 'log', (150, 150), True),
                      Text(game, 'help', (200, 120), True)]
        game.images = [InteractiveImg(game, 'clock', (620, 200), True)]
        game.etcs = [Command(game, 'cmd', (700, 420), False)]

def lto(game):
    if game.map[0] == 0:
        for directory in game.directories:
            if directory.name == 'DRIVE' and not directory.interaction:
                if detectCover(game, ['1aaad4', 'enyl1'], 'image', (49, 45), (3, 3)):
                    game.asset['sfx/open'].play()
                    if directory.name == 'DRIVE': directory.interaction = True
                    for image in game.images:
                        if image.name == 'lock':
                            game.images.remove(image)
                            game.windows.remove(image.window)
                            game.asset['image/lock'] = pygame.transform.scale(loadImg('lock.png', [1], 2, 1)[0], (55, 55))
                            pos = image.window.rect.topleft
                            break
                    game.images.append(LockImg(game, 'lock', (300, 400), True))
                    for image in game.images:
                        if image.name == 'lock':
                            image.window.rect.topleft = pos
                            game.windows.append(image.window)
                            break
                else:
                    game.asset['sfx/locked'].play()

        for etc in game.etcs:
            if etc.name == 'LTS':
                if etc.window.password == etc.window.inputPW:
                    game.asset['sfx/open'].play()
                    for directory in game.directories:
                        if directory.name == 'sys': directory.interaction = True
                    etc.window.password = 0

def dl(game, file):
    if game.map[0] == 0:
        if game.light:
            if file.name == 'sysDownload':
                for window in game.windows:
                    if window.file.name == 'sys':
                        pos = window.rect.topleft
                        game.windows.remove(window)
                        break

                for directory in game.directories:
                    if directory.name == 'sys':
                        del directory.files[0]
                        for etc in game.etcs:
                            if etc.name == 'sysDownload': game.etcs.remove(etc)
                        directory.files.append(PadLock(game, 'reboot', (0, 0), True, [[1, 0, 0, 1, 1, 0], [0, 1, 0, 1, 0, 0], [1, 0, 0, 0, 0, 0]], True))
                        directory.files.append(Text(game, '9o12', (50, 0), True, True))
                        directory.files.append(Text(game, '2nasHf', (100, 0), True, True))
                        for f in directory.files:
                            f.owner_window = directory.window
                        directory.window.rect.w = 150
                        directory.window.rect.topleft = pos
                        for file in directory.files:
                            if file.objType == 'directory' and file not in game.directories:
                                game.directories.append(file)
                            elif file.objType == 'image' and file not in game.images:
                                game.images.append(file)
                            elif file.objType == 'txt' and file not in game.texts:
                                game.texts.append(file)
                            elif file not in game.etcs:
                                game.etcs.append(file)
                        game.windows.append(directory.window)
                        break
            game.light = False
        else:
            game.light = True
            pygame.mixer.stop()
            game.asset['sfx/ominous'].play()
            pygame.draw.rect(game.screen, '#000000', (0, 0, 900, 650))
            pygame.display.update()
            time.sleep(7)
            game.map = 1
            game.bgm_playing = False

def plc(game):
    if game.map[0] == 0:
        game.windows.clear()
        game.directories.clear()
        game.images.clear()
        game.texts.clear()
        game.etcs.clear()

        game.light = True
        game.windows.append(SystemRebootWindow(None, game))
    elif game.map[0] == 1:
        for etc in game.etcs:
            if etc.name == 'cmd':
                etc.interaction = True

def ec(game):
    if game.console and (game.console in game.windows):
        return game.console
    dummy = File(game, 'console', (520, 220), 'etc', True, size=(1, 1))
    cw = ConsoleWindow(dummy, game, size=(320, 180))
    cw.rect.topleft = (520, 220)
    game.windows.append(cw)
    game.console = cw
    return cw

def log(game, target):
    cw = game.ensureConsole()
    cw.add_line('$log {}'.format(target))
    if target.lower() == 'edward':
        cw.add_line('past log'.format(target))
        cw.add_line(''.format(target))
        cw.add_line('19.01.13'.format(target))
        cw.add_line('=============================='.format(target))
        cw.add_line('22:17'.format(target))
        cw.add_line('system downloaded.'.format(target))
        cw.add_line('23:48'.format(target))
        cw.add_line('port 22 decoded.'.format(target))
        cw.add_line('23:58'.format(target))
        cw.add_line('session opened with encoded embed.'.format(target))
        cw.add_line('=============================='.format(target))
        cw.add_line(''.format(target))
        cw.add_line('19.01.14'.format(target))
        cw.add_line('=============================='.format(target))
        cw.add_line('00:07'.format(target))
        cw.add_line('sys-base unlocked.'.format(target))
        cw.add_line('00:32'.format(target))
        cw.add_line('user-root activated.'.format(target))
        cw.add_line('user-Edward logged in.'.format(target))
        cw.add_line('write dir with safe mode.'.format(target))
        cw.add_line('=============================='.format(target))
        cw.add_line(''.format(target))
        cw.add_line('19.01.15'.format(target))
        cw.add_line('=============================='.format(target))
        cw.add_line('02:44'.format(target))
        cw.add_line('system: msg from L□■■f□r'.format(target))
        cw.add_line('system: connected with L□■■f□r'.format(target))
        cw.add_line('03:11'.format(target))
        cw.add_line('system: msg from L□■■f□r'.format(target))
        cw.add_line('03:28'.format(target))
        cw.add_line('write dir for next user'.format(target))
        cw.add_line('system: del -u Edward'.format(target))
        cw.add_line('system: kill sys'.format(target))
    else:
        cw.add_line('command only for the offline user')
    game.asset['sfx/tick'].play()

def ping(game, target):
    cw = game.ensureConsole()
    cw.add_line('$ ping {}'.format(target))
    import random
    ms = random.randint(23, 140)
    if target == 'L□■■f□r':
        cw.add_line('PING {} ... {}ms'.format(target, ms))
        cw.add_line('reply: ...')
        cw.add_line('reply: stop.')
        game.asset['sfx/crack'].play()
    elif target.lower() == 'root':
        cw.add_line('PING root ... {}ms'.format(ms))
        cw.add_line('reply: ok')
    else:
        cw.add_line('PING {} ... timeout'.format(target))
        game.asset['sfx/locked'].play()
        
def msg(game, target):
    cw = game.ensureConsole()
    cw.add_line('$ msg {}'.format(target))
    if target == 'L□■■f□r':
        pass
        game.c_loop.set_enabled(True)
        game.asset['sfx/open'].play()
    else:
        cw.add_line('{}: not found'.format(target))
        game.asset['sfx/locked'].play()

def cmc(game):
    moon = None; clock = None
    for w in game.windows:
        if w.file.name == 'moon': moon = w.index
        elif w.file.name == 'clock': clock = w.index

    if moon == 3 and clock == 2:
        game.directories.append(Directory(game, 'dir_Ed', (705, 60), [
            Text(game, 'Ed-readme', (5, 0), True, True),
        ], True))
