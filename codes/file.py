import pygame

from codes.ui import (
    ICON_SIZE,
    LABEL_LINE_GAP,
    directory_auto_size,
    display_name,
    wrap_label,
)
from codes.window import (
    ClockWindow,
    CmdWindow,
    DirWindow,
    ImgLockerWindow,
    ImgWindow,
    InteractiveImgWindow,
    LoaderWindow,
    LockWindow,
    LockerWindow,
    LogWindow,
    PadLockWindow,
    PhaseWindow,
    RotorWindow,
    TextWindow,
    TranImgWindow,
    TxWindow,
    Window,
)


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
                self.game.dc.reset()
                self.game.open_file(self)
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
                self.game.dc.reset()
                self.game.open_directory(self)
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
        if self.name == 'moon': self.objType = 'lock'; self.display_name = display_name(self.name, self.objType)
        if self.name == 'clock':
            self.objType = 'lock'; self.display_name = display_name(self.name, self.objType)
            self.window = ClockWindow(self, self.game, self.size)
        else: self.window = InteractiveImgWindow(self, self.game, self.size, self.image)
        self.icon = self.game.asset['icon/etc']
class PhaseImg(Image):
    def __init__(self, game, name, pos, interaction, child = False):
        super().__init__(game, name, pos, interaction, child)
        self.objType = 'sys'
        self.display_name = display_name(self.name, self.objType)
        self.window = PhaseWindow(self, self.game, self.size, self.image)
        self.icon = self.game.asset['icon/etc']

class Locker(File):
    def __init__(self, game, name, pos, password, interaction, child=False, _max=10, initpt=(20, 20), initsz=(32, 64), initpd=20):
        self.game = game
        self.name = name
        self.password = password
        self.length = len(self.password)
        self.size = (52 * self.length + 20, 104)
        super().__init__(game, name, pos, 'locker', interaction, self.size, child)
        self.window = LockerWindow(self, self.game, self.size, self.password, _max, initpt, initsz, initpd)
class ImgLocker(File):
    def __init__(self, game, name, pos, password, _max, initpt, initsz, initpd, interaction, child=False):
        self.game = game
        self.name = name
        self.password = password
        self.length = len(self.password)
        self.image = self.game.asset['image/' + self.name]
        try: size = self.image.get_size()
        except AttributeError: size = self.image[0].get_size()
        super().__init__(game, name, pos, 'locker', interaction, size, child)
        self.window = ImgLockerWindow(self, self.game, size, self.password, self.image, _max, initpt, initsz, initpd)

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

class Log(File):
 def __init__(self, game, name, pos, interaction, child=False):
  super().__init__(game, name, pos, 'sys', interaction, (360, 220), child)
  self.window = LogWindow(self, self.game)

class CmdFile(File):
    def __init__(self, game, name, pos, interaction, child=False):
        super().__init__(game, name, pos, 'sys', interaction, (360, 220), child)
        self.window = CmdWindow(self, self.game)
