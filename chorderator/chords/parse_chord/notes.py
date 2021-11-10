from .excp import NoteFormatError, RangeError, FormatError
from six.moves import range

_note_dict = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
fifths = ["F", "C", "G", "D", "A", "E", "B"]


def int_to_note(note_int, accidentals="#"):
    if note_int not in range(12):
        raise RangeError("int out of bounds (0-11): %d" % note_int)
    ns = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    nf = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    if accidentals == "#":
        return ns[note_int]
    elif accidentals == "b":
        return nf[note_int]
    else:
        raise FormatError("'%s' not valid as accidental" % accidentals)


def is_enharmonic(note1, note2):
    return note_to_int(note1) == note_to_int(note2)


def is_valid_note(note):
    if note[0] not in _note_dict:
        return False
    for post in note[1:]:
        if post != "b" and post != "#":
            return False
    return True


def note_to_int(note):
    if is_valid_note(note):
        val = _note_dict[note[0]]
    else:
        raise NoteFormatError("Unknown note format '%s'" % note)

    # Check for '#' and 'b' postfixes
    for post in note[1:]:
        if post == "b":
            val -= 1
        elif post == "#":
            val += 1
    return val % 12


def reduce_accidentals(note):
    val = note_to_int(note[0])
    for token in note[1:]:
        if token == "b":
            val -= 1
        elif token == "#":
            val += 1
        else:
            raise NoteFormatError("Unknown note format '%s'" % note)
    if val >= note_to_int(note[0]):
        return int_to_note(val % 12)
    else:
        return int_to_note(val % 12, "b")


def remove_redundant_accidentals(note):
    val = 0
    for token in note[1:]:
        if token == "b":
            val -= 1
        elif token == "#":
            val += 1
    result = note[0]
    while val > 0:
        result = augment(result)
        val -= 1
    while val < 0:
        result = diminish(result)
        val += 1
    return result


def augment(note):
    if note[-1] != "b":
        return note + "#"
    else:
        return note[:-1]


def diminish(note):
    if note[-1] != "#":
        return note + "b"
    else:
        return note[:-1]