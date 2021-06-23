# ######
# Chords
# ######

# roots
C = 0
CS, DF = 1, 1
D = 2
DS, EF = 3, 3
E = 4
F = 5
FS, GF = 6, 6
G = 7
GS, AF = 8, 8
A = 9
AS, BF = 10, 10
B = 11

# types
MAJ_TRIAD = 0
MIN_TRIAD = 1
AUG_TRIAD = 2
DIM_TRIAD = 3
MAJ_SEVENTH = 4
MIN_SEVENTH = 5
DOM_SEVENTH = 6
HALF_DIM_SEVENTH = 7
FULLY_DIM_SEVENTH = 8


# inversions
T6 = 0
T64 = 1
S65 = 2
S43 = 3
S2 = 4

# sus
SUS2 = 0
SUS4 = 1

# adds
ADD6 = 0
ADD9 = 1
ADD69 = 2
ADD11 = 3
ADD13 = 4
ADD911 = 5
ADD913 = 6
ADD1113 = 7
ADD91113 = 8
ADDb7 = 9

# type inversions sus adds
POPULAR_CHORDS = [
    ('maj', [MAJ_TRIAD, -1, -1, -1]), ('MIN', [MIN_TRIAD, -1, -1, -1]), ('maj/5', [MAJ_TRIAD, T64, -1, -1]),
    ('min7', [MIN_SEVENTH, -1, -1, -1]), ('maj/9', [MAJ_TRIAD, -1, -1, -1]), ('7', [DOM_SEVENTH, -1, -1, -1]),
    ('maj/3', [MAJ_TRIAD, T6, -1, -1]), ('maj(9)', [MAJ_TRIAD, -1, -1, ADD9]), ('sus4', [MAJ_TRIAD, -1, SUS4, -1]),
    ('1', [MAJ_TRIAD, -1, -1, -1]), ('maj6', [MAJ_TRIAD, -1, -1, ADD6]), ('sus4(b7)', [DOM_SEVENTH, -1, SUS4, -1]),
    ('maj7', [MAJ_SEVENTH, -1, -1, -1]), ('min6', [MIN_TRIAD, -1, -1, ADD6]), ('maj9', [MAJ_SEVENTH, -1, -1, ADD9]),
    ('min9', [MIN_SEVENTH, -1, -1, ADD9]), ('sus2', [MAJ_TRIAD, -1, SUS2, -1]),
    ('5', [MAJ_TRIAD, -1, -1, -1]), ('min/b3', [MIN_TRIAD, T6, -1, -1]), ('9', [DOM_SEVENTH, -1, -1, ADD9]),
    ('7/3', [DOM_SEVENTH, S65, -1, -1]), ('7/5', [DOM_SEVENTH, S43, -1, -1]), ('aug(b7)', [AUG_TRIAD, -1, -1, ADDb7]),
    ('min/5', [MIN_TRIAD, T64, -1, -1]), ('maj/b7', [DOM_SEVENTH, S2, -1, -1]), ('min/b7', [MIN_TRIAD, S2, -1, ADDb7]),
    ('maj/7', [MAJ_SEVENTH, S2, -1, -1]), ('dim', [DIM_TRIAD, -1, -1, -1]), ('maj/11', [MAJ_SEVENTH, -1, -1, ADD11]),
    ('11', [DOM_SEVENTH, -1, -1, ADD911]), ('maj6(9)', [MAJ_TRIAD, -1, -1, ADD69]),
    ('min11', [MIN_SEVENTH, -1, -1, ADD911]), ('min7/5', [MIN_SEVENTH, S43, -1, -1]),
    ('min/11', [MIN_SEVENTH, -1, -1, ADD11]), ('7(b9)', [DOM_SEVENTH, -1, -1, -1]),
    ('7(#9)', [DOM_SEVENTH, -1, -1, -1]), ('13', [DOM_SEVENTH, -1, -1, ADD91113]), ('5(b7)', [DOM_SEVENTH, -1, -1, -1]),
    ('min7/b7', [MIN_SEVENTH, -1, -1, -1]), ('sus4(b7,9)', [DOM_SEVENTH, -1, SUS4, ADD9])
]

# ############
# Progressions
# ############

# types
FADEIN = 0
INTRO = 1
PREVERSE = 2
VERSE = 3
PRECHORUS = 4
CHORUS = 5
BRIDGE = 6
TRANS = 7
INTERLUDE = 8
INSTRUMENTAL = 9
SOLO = 10
OUTRO = 11
FADEOUT = 12

# #######
# General
# #######

# instruments
PIANO = 0
ORGAN = 19
HARMONICA = 22
GUITAR = 24
E_GUITAR = 27
D_GUITAR = 30
BASS = 33
VLN = 40
VLA = 41
CELLO = 42
BRASS = 61
VOCAL = 52
SAX = 66
FLUTE = 73
SQUARE = 80
SAWTOOTH = 81
SHAKUHACHI = 77

# pick progressions
SHORT = 0
LONG = 1
DENSE = 2
SPARSE = 3
