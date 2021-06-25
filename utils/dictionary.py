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
