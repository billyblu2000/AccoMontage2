from utils.constants import *

# types
# MAJ_TRIAD, MIN_TRIAD, AUG_TRIAD, DIM_TRIAD, MAJ_SEVENTH,
# MIN_SEVENTH, DOM_SEVENTH, HALF_DIM_SEVENTH, FULLY_DIM_SEVENTH
#
# inversions
# T6, T64, S65, S43, S2
#
# sus
# SUS2, SUS4
#
# adds
# ADD6, ADD9, ADD69, ADD11, ADD13, ADD911,
# ADD913, ADD1113, ADD91113, ADDb7

POPULAR_CHORDS = [
    # ('raw', [type, inversion, sus, add])
    ('maj', [MAJ_TRIAD, -1, -1, -1]),
    ('min', [MIN_TRIAD, -1, -1, -1]),
    ('maj/5', [MAJ_TRIAD, T64, -1, -1]),
    ('min7', [MIN_SEVENTH, -1, -1, -1]),
    ('maj/9', [MAJ_TRIAD, -1, -1, -1]),
    ('7', [DOM_SEVENTH, -1, -1, -1]),
    ('maj/3', [MAJ_TRIAD, T6, -1, -1]),
    ('maj(9)', [MAJ_TRIAD, -1, -1, ADD9]),
    ('sus4', [MAJ_TRIAD, -1, SUS4, -1]),
    ('1', [MAJ_TRIAD, -1, -1, -1]),
    ('maj6', [MAJ_TRIAD, -1, -1, ADD6]),
    ('sus4(b7)', [DOM_SEVENTH, -1, SUS4, -1]),
    ('maj7', [MAJ_SEVENTH, -1, -1, -1]),
    ('min6', [MIN_TRIAD, -1, -1, ADD6]),
    ('maj9', [MAJ_SEVENTH, -1, -1, ADD9]),
    ('min9', [MIN_SEVENTH, -1, -1, ADD9]),
    ('sus2', [MAJ_TRIAD, -1, SUS2, -1]),
    ('5', [MAJ_TRIAD, -1, -1, -1]),
    ('min/b3', [MIN_TRIAD, T6, -1, -1]),
    ('9', [DOM_SEVENTH, -1, -1, ADD9]),
    ('7/3', [DOM_SEVENTH, S65, -1, -1]),
    ('7/5', [DOM_SEVENTH, S43, -1, -1]),
    ('aug(b7)', [AUG_TRIAD, -1, -1, ADDb7]),
    ('min/5', [MIN_TRIAD, T64, -1, -1]),
    ('maj/b7', [DOM_SEVENTH, S2, -1, -1]),
    ('min/b7', [MIN_TRIAD, S2, -1, ADDb7]),
    ('maj/7', [MAJ_SEVENTH, S2, -1, -1]),
    ('dim', [DIM_TRIAD, -1, -1, -1]),
    ('maj/11', [MAJ_SEVENTH, -1, -1, ADD11]),
    ('11', [DOM_SEVENTH, -1, -1, ADD911]),
    ('maj6(9)', [MAJ_TRIAD, -1, -1, ADD69]),
    ('min11', [MIN_SEVENTH, -1, -1, ADD911]),
    ('min7/5', [MIN_SEVENTH, S43, -1, -1]),
    ('min/11', [MIN_SEVENTH, -1, -1, ADD11]),
    ('7(b9)', [DOM_SEVENTH, -1, -1, -1]),
    ('7(#9)', [DOM_SEVENTH, -1, -1, -1]),
    ('13', [DOM_SEVENTH, -1, -1, ADD91113]),
    ('5(b7)', [DOM_SEVENTH, -1, -1, -1]),
    ('min7/b7', [MIN_SEVENTH, -1, -1, -1]),
    ('sus4(b7,9)', [DOM_SEVENTH, -1, SUS4, ADD9])
]

# 我来了