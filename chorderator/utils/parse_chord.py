from .constants import *

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

# 0: roots
# 1: triads (two options from here, a. mark sus2, sus4, dim as X (unknown); b. record them separately)
# 2: sevenths
# 3: extensions (all the 9, 11, 13, 6, potentially subdivide even further by its base chords)
# 4: inversions (basic idea is to first remove all the annotations that have little influences on tonality
#                a. potentially subdivide even more as follows:
#                4.1 triads, 4.1.1: first inversion, 4.1.2: second inversion,
#                4.2 sevenths, 4.2.1 first inversion, 4.2.2: second inversion, 4.2.3: third inversion;
#                b. remove octaves if recorded;
#                c. include power chord also in this hierarchy since it does not change tonality)
# 5: original

CHORD_HIERARCHY = {
    0: ['1'],
    1: ['maj', 'min',  'sus4', 'sus2', 'dim'],
    2: ['maj7', '7', 'min7', 'sus4(b7)', '5(b7)'],
    3: ['maj9', '9',  '11', '7(b9)', '7(#9)', '13', 'maj/9', 'maj(9)', 'maj6', 'maj/11', 'maj6(9)',
        'min9', 'min11', 'min6', 'min/11', 'sus4(b7,9)', 'aug(b7)', 'dim7', 'sus13'],
    4: ['5', 'maj/3', 'min/b3', 'maj/5', 'min/5',
        '7/3', '7/5', 'min7/5', 'maj/7', 'maj/b7', 'min/b7', 'min7/b7']
}


# CHORDS_ANALYSIS_1 is the most brutal way to analysis chords, it only considers if the chord is major or minor
CHORDS_ANALYSIS_1 = {
    MAJ_TRIAD: ['maj', 'maj7', '7','maj9', '9',  '11',
                '7(b9)', '7(#9)', '13', 'maj/9', 'maj(9)', 'maj6', 'maj/11', 'maj6(9)',
                'maj/3', 'maj/5', '7/3', '7/5', 'maj/7', 'maj/b7'],
    MIN_TRIAD: ['min', 'min7', 'min9', 'min11', 'min6', 'min/11', 'min/b3', 'min/5', 'min7/5', 'min/b7', 'min7/b7'],
    X: ['sus4', 'sus4(b7)', 'sus4(b7,9)', 'sus13', 'sus2', 'dim', '5(b7)', 'aug(b7)', 'dim7']
}


# CHORDS_ANALYSIS_2 is a more careful but still direct approach, it only considers the base chord of the given chord
CHORDS_ANALYSIS_2 = {
    MAJ_TRIAD: ['maj', 'maj/9', 'maj(9)', 'maj6', 'maj/11', 'maj6(9)', 'maj/3', 'maj/5'],
    MIN_TRIAD: ['min', 'min6', 'min/11', 'min/b3', 'min/5'],
    DIM_TRIAD: ['dim', 'dim7'],
    MAJ_SEVENTH: ['maj7', 'maj/7', 'maj9'],
    DOM_SEVENTH: ['7', '9',  '11', '7(b9)', '7(#9)', '13', '7/3', '7/5', 'maj/b7'],
    MIN_SEVENTH: ['min7', 'min9', 'min11', 'min7/5', 'min/b7', 'min7/b7'],
    SUS_4: ['sus4', 'sus4(b7)', 'sus4(b7,9)', 'sus13'],
    X: ['sus2', '5(b7)', 'aug(b7)']
}


# CHORDS_ANALYSIS_3 is a bit subjective, it considers the tonal function of the chord,
# such as maj69 functions as maj7, so I put maj67 in the MAJ_SEVENTH class
# This analysis needs more work (on how the chord sounds)
CHORDS_ANALYSIS_3 = {
    MAJ_TRIAD: ['maj', 'maj/9', 'maj(9)', 'maj/11', 'maj/3', 'maj/5', 'sus4'],
    MIN_TRIAD: ['min', 'min6', 'min/11', 'min/b3', 'min/5'],
    MAJ_SEVENTH: ['maj7', 'maj/7', 'maj9', 'maj6', 'maj6(9)'],
    DOM_SEVENTH: ['7', '9',  '11', '7(b9)', '7(#9)', '13', '7/3', '7/5', 'maj/b7', 'sus4(b7,9)', '5(b7)', 'sus13'],
    MIN_SEVENTH: ['min7', 'min9', 'min11', 'min7/5', 'min/b7', 'min7/b7'],
    X: ['sus2', 'dim', 'sus4(b7)', 'aug(b7)', 'dim7']
}