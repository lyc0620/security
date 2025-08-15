import pygame
from codes.util import detectCover, loadImg
from codes.object import Directory, Text, Tx7y1, Image, TransparentImg, LockImg, Locker, Sys, Reboot, LoaderWindow

def lm(game):
    pygame.mixer.init()
    pygame.mixer.set_num_channels(64)
    if game.map == 0:
        game.directories = [Directory(game, 'DRIVE', (200, 200), [
            Directory(game, 'sys', (0, 0), [
                Sys(game, 'sysDownload', (0, 0), True, True)
            ], False, True, (100, 60)),
            Tx7y1(game, 'Tx7y1', (50, 0), True, True),
            Directory(game, 'empty', (100, 0), [
                Text(game, 'empty', (0, 0), True, True),
                Directory(game, 'empty', (50, 0), [
                    Text(game, 'em?ty', (0, 0), True, True),
                    Directory(game, 'empty', (50, 0), [
                        Text(game, 'em?t\'/', (0, 0), True, True),
                        Directory(game, 'empty', (50, 0), [
                            Text(game, 'empty.', (0, 0), True, True),
                            Image(game, 'y6c20', (50, 0), True, True)
                        ], True, True, (150, 70))
                    ], True, True, (150, 70))
                ], True, True, (150, 70))
            ], True, True, (150, 70)),
            Image(game, 'ka31go', (0, 60), True, True),
            Image(game, 'z1p81', (50, 60), True, True),
            Directory(game, '2n1', (100, 60), [
                Image(game, 'y30o1', (0, 0), True, True),
                Image(game, 'o771a', (50, 0), True, True),
                Image(game, 'fyw1', (100, 0), True, True),
                Image(game, 's131p', (0, 60), True, True),
                Locker(game, 'LTS', (50, 60), '640', True, True)
            ], True, True, (200, 120))
        ], False, size=(200, 120)),
                            Directory(game, 'a1nd2', (700, 100), [
                                Image(game, '3qy4', (0, 0), True, True),
                                Image(game, '1aaad4', (50, 0), True, True),
                                Image(game, 'kf3s', (100, 0), True, True),
                                Image(game, '33256', (0, 60), True, True),
                                Text(game, 'L3I1l7', (50, 60), True, True),
                                TransparentImg(game, 'enyl1', (100, 60), True, True)
                            ], True, size=(200, 120))]
        game.texts = [Text(game, 'readme', (500, 420), True)]
        game.images = [LockImg(game, 'lock', (300, 400), True)]

    elif game.map == 1:
        game.light = True

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
                        directory.files.append(Reboot(game, 'reboot', (0, 0), True, True))
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
            game.map = 1

def cm(game):
    if game.map[0] == 0:
        game.windows.clear()
        game.directories.clear()
        game.images.clear()
        game.texts.clear()
        game.etcs.clear()

        game.windows.append(LoaderWindow(None, game, comment='Rebooting the System.', size=(200, 60)))
