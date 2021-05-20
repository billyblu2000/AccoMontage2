from utils.constants import *

tonality_dict = {
    "C": 0,
    "C#": 1, "Db": 1,
    "D": 2,
    "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4,
    "F": 5,
    "F#": 6, "Gb": 6,
    "G": 7,
    "G#": 8, "Ab": 8,
    "A": 9,
    "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11
}
type_dict = {
    "fadein": FADEIN,
    "intro": INTRO,
    "intro-a": INTRO,
    "intro-b": INTRO,
    "pre-verse": PREVERSE,
    "preverse": PREVERSE,
    "verse": VERSE,
    "pre-chorus": PRECHORUS,
    "prechorus": PRECHORUS,
    "chorus": CHORUS,
    "refrain": CHORUS,
    "bridge": BRIDGE,
    "trans": TRANS,
    "transition": TRANS,
    "interlude": INTERLUDE,
    "instrumental": INSTRUMENTAL,
    "solo": SOLO,
    "outro": OUTRO,
    "coda": OUTRO,
    "ending": OUTRO,
    "fadeout": FADEOUT,
}


def root_map_major(root,tonic):
    tr, tt = tonality_dict[root], tonality_dict[tonic]
    if tr < tt:
        tr += 12
    if tr - tt == 0:
        return 1
    elif tr - tt == 1:
        return 1.5
    elif tr - tt == 2:
        return 2
    elif tr - tt == 3:
        return 2.5
    elif tr - tt == 4:
        return 3
    elif tr - tt == 5:
        return 4
    elif tr - tt == 6:
        return 4.5
    elif tr - tt == 7:
        return 5
    elif tr - tt == 8:
        return 5.5
    elif tr - tt == 9:
        return 6
    elif tr - tt == 10:
        return 6.5
    elif tr - tt == 11:
        return 7
    else:
        return -1


def root_map_minor(root, tonic):
    tr, tt = tonality_dict[root], tonality_dict[tonic]
    if tr < tt:
        tr += 12
    if tr - tt == 0:
        return 1
    elif tr - tt == 1:
        return 1.5
    elif tr - tt == 2:
        return 2
    elif tr - tt == 3:
        return 3
    elif tr - tt == 4:
        return 3.5
    elif tr - tt == 5:
        return 4
    elif tr - tt == 6:
        return 4.5
    elif tr - tt == 7:
        return 5
    elif tr - tt == 8:
        return 6
    elif tr - tt == 9:
        return 6.5
    elif tr - tt == 10:
        return 7
    elif tr - tt == 11:
        return 7
    else:
        return -1
