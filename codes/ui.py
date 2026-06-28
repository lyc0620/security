import pygame

CLR_BODY = pygame.Color("#a6b5d6")
CLR_BORDER = pygame.Color("#7e8dae")
CLR_CLOSE = pygame.Color("#667596")
CLR_DARK = pygame.Color("#0A0F16")

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
    _ellipsis = '...'
    while text and font.size(text + _ellipsis)[0] > max_w:
        text = text[:-1]
    return text + _ellipsis if text else _ellipsis


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
