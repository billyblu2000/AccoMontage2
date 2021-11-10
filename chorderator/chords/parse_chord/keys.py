from itertools import cycle, islice

from six.moves import range

from . import notes
from .excp import NoteFormatError, RangeError

keys = [
    ("Cb", "ab"),  # 7 b
    ("Gb", "eb"),  # 6 b
    ("Db", "bb"),  # 5 b
    ("Ab", "f"),  # 4 b
    ("Eb", "c"),  # 3 b
    ("Bb", "g"),  # 2 b
    ("F", "d"),  # 1 b
    ("C", "a"),  # nothing
    ("G", "e"),  # 1 #
    ("D", "b"),  # 2 #
    ("A", "f#"),  # 3 #
    ("E", "c#"),  # 4 #
    ("B", "g#"),  # 5 #
    ("F#", "d#"),  # 6 #
    ("C#", "a#"),  # 7 #
]

major_keys = [couple[0] for couple in keys]
minor_keys = [couple[1] for couple in keys]

base_scale = ["C", "D", "E", "F", "G", "A", "B"]

_key_cache = {}


def is_valid_key(key):
    for couple in keys:
        if key in couple:
            return True
    return False


def get_key(accidentals=0):
    if accidentals not in range(-7, 8):
        raise RangeError("integer not in range (-7)-(+7).")
    return keys[accidentals + 7]


def get_key_signature(key="C"):
    if not is_valid_key(key):
        raise NoteFormatError("unrecognized format for key '%s'" % key)

    for couple in keys:
        if key in couple:
            accidentals = keys.index(couple) - 7
            return accidentals


def get_key_signature_accidentals(key="C"):
    accidentals = get_key_signature(key)
    res = []

    if accidentals < 0:
        for i in range(-accidentals):
            res.append("{0}{1}".format(list(reversed(notes.fifths))[i], "b"))
    elif accidentals > 0:
        for i in range(accidentals):
            res.append("{0}{1}".format(notes.fifths[i], "#"))
    return res


def get_notes(key="C"):
    if key in _key_cache:
        return _key_cache[key]
    if not is_valid_key(key):
        raise NoteFormatError("unrecognized format for key '%s'" % key)
    result = []

    # Calculate notes
    altered_notes = [x[0] for x in get_key_signature_accidentals(key)]

    if get_key_signature(key) < 0:
        symbol = "b"
    elif get_key_signature(key) > 0:
        symbol = "#"

    raw_tonic_index = base_scale.index(key.upper()[0])

    for note in islice(cycle(base_scale), raw_tonic_index, raw_tonic_index + 7):
        if note in altered_notes:
            result.append("%s%s" % (note, symbol))
        else:
            result.append(note)

    # Save result to cache
    _key_cache[key] = result
    return result


def relative_major(key):
    for couple in keys:
        if key == couple[1]:
            return couple[0]
    raise NoteFormatError("'%s' is not a minor key" % key)


def relative_minor(key):
    for couple in keys:
        if key == couple[0]:
            return couple[1]
    raise NoteFormatError("'%s' is not a major key" % key)


class Key(object):
    """A key object."""

    def __init__(self, key="C"):
        self.key = key

        if self.key[0].islower():
            self.mode = "minor"
        else:
            self.mode = "major"

        try:
            symbol = self.key[1]
            if symbol == "#":
                symbol = "sharp "
            else:
                symbol = "flat "
        except:
            symbol = ""
        self.name = "{0} {1}{2}".format(self.key[0].upper(), symbol, self.mode)

        self.signature = get_key_signature(self.key)

    def __eq__(self, other):
        if self.key == other.key:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
