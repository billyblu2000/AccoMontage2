from .constants import *

# TODO
chord_type_to_pitch_relation = {
    MAJ_TRIAD: [4, 7],
    MIN_TRIAD: [3, 7],
    AUG_TRIAD: [4, 8],
    DIM_TRIAD: [3, 6],
    MAJ_SEVENTH: [4, 7, 11],
    MIN_SEVENTH: [3, 7, 10],
    DOM_SEVENTH: [4, 7, 10],
    HALF_DIM_SEVENTH: [],
    FULLY_DIM_SEVENTH: [],
    X: [4, 7]
}

root_to_pitch = {
    C: 60, CS: 61, DF: 61, D: 62, DS: 63, EF: 63, E: 64,
    F: 65, FS: 66, GF: 66, G: 67, GS: 68, AF: 68, A: 69,
    AS: 70, BF: 70, B: 71, CF: 71,
}

root_to_pitch_low = {}
for item in root_to_pitch.items():
    root_to_pitch_low[item[0]] = item[1] - 12

root_to_str = {
    C: "C", CS: "C#", DF: "Db", D: "D", DS: "D#", EF: "Eb", E: "E",
    F: "F", FS: "F#", GF: "Gb", G: "G", GS: "G#", AF: "Ab", A: "A",
    AS: "A#", BF: "Bb", B: "B", CF: 'Cb',
}

str_to_root = {}
for item in root_to_str.items():
    str_to_root[item[1]] = item[0]
str_to_root["C#"] = CS
str_to_root["D#"] = DS
str_to_root["F#"] = FS
str_to_root["G#"] = GS
str_to_root["A#"] = AS
str_to_root["B"] = B
str_to_root["Cb"] = CF

major_map = {
    0: 1, 1: 1.5, 2: 2, 3: 2.5, 4: 3, 5: 4, 6: 4.5, 7: 5, 8: 5.5, 9: 6, 10: 6.5, 11: 7, -1: 0
}
minor_map = {
    0: 1, 1: 1.5, 2: 2, 3: 3, 4: 3.5, 5: 4, 6: 4.5, 7: 5, 8: 6, 9: 6.5, 10: 7, 11: 7.5, -1: 0
}

major_map_backward = {}
minor_map_backward = {}
for item in major_map.items():
    major_map_backward[item[1]] = item[0]
for item in minor_map.items():
    minor_map_backward[item[1]] = item[0]
