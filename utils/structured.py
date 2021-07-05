from utils.constants import *

chord_type_to_pitch_relation = {
    MAJ_TRIAD: [4, 7],
    MIN_TRIAD: [3, 7],
    AUG_TRIAD: [4, 8],
    DIM_TRIAD: [3, 6],
    MAJ_SEVENTH: [4, 7, 11],
    MIN_SEVENTH: [3, 7, 10],
    DOM_SEVENTH: [4, 7, 10],
    HALF_DIM_SEVENTH: [3, 6, 10],
    FULLY_DIM_SEVENTH: [3, 6, 9],
}

root_to_pitch = {
    C: 60, CS: 61, DF: 61, D: 62, DS: 63, EF: 63, E: 64,
    F: 65, FS: 66, GF: 66, G: 67, GS: 68, AF: 68, A: 69,
    AS: 70, BF: 70, B: 71,
}

root_to_pitch_low = {}
for item in root_to_pitch.items():
    root_to_pitch_low[item[0]] = item[1] - 12

root_to_str = {
    C: "C", CS: "C#", DF: "Db", D: "D", DS: "D#", EF: "Eb", E: "E",
    F: "F", FS: "F#", GF: "Gb", G: "G", GS: "G#", AF: "Ab", A: "A",
    AS: "A#", BF: "Bb", B: "B",
}

str_to_root = {}
for item in root_to_str.items():
    str_to_root[item[1]] = item[0]
str_to_root["C#"] = CS
str_to_root["D#"] = DS
str_to_root["F#"] = FS
str_to_root["G#"] = GS
str_to_root["A#"] = AS

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
