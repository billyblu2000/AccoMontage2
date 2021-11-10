from . import notes
from . import keys


def interval(key, start_note, interval):
    if not notes.is_valid_note(start_note):
        raise KeyError("The start note '%s' is not a valid note" % start_note)
    notes_in_key = keys.get_notes(key)
    for n in notes_in_key:
        if n[0] == start_note[0]:
            index = notes_in_key.index(n)
    return notes_in_key[(index + interval) % 7]


def unison(note, key=None):
    return interval(note, note, 0)


def second(note, key):
    return interval(key, note, 1)


def third(note, key):
    return interval(key, note, 2)


def fourth(note, key):
    return interval(key, note, 3)


def fifth(note, key):
    return interval(key, note, 4)


def sixth(note, key):
    return interval(key, note, 5)


def seventh(note, key):
    return interval(key, note, 6)


def minor_unison(note):
    return notes.diminish(note)


def major_unison(note):
    return note


def augmented_unison(note):
    return notes.augment(note)


def minor_second(note):
    sec = second(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, sec, 1)


def major_second(note):
    sec = second(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, sec, 2)


def minor_third(note):
    trd = third(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, trd, 3)


def major_third(note):
    trd = third(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, trd, 4)


def minor_fourth(note):
    frt = fourth(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, frt, 4)


def major_fourth(note):
    frt = fourth(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, frt, 5)


def perfect_fourth(note):
    return major_fourth(note)


def minor_fifth(note):
    fif = fifth(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, fif, 6)


def major_fifth(note):
    fif = fifth(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, fif, 7)


def perfect_fifth(note):
    return major_fifth(note)


def minor_sixth(note):
    sth = sixth(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, sth, 8)


def major_sixth(note):
    sth = sixth(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, sth, 9)


def minor_seventh(note):
    sth = seventh(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, sth, 10)


def major_seventh(note):
    sth = seventh(note[0], "C")
    return augment_or_diminish_until_the_interval_is_right(note, sth, 11)


def get_interval(note, interval, key="C"):
    intervals = [(notes.note_to_int(key) + x) % 12 for x in [0, 2, 4, 5, 7, 9, 11, ]]
    key_notes = keys.get_notes(key)
    for x in key_notes:
        if x[0] == note[0]:
            result = (intervals[key_notes.index(x)] + interval) % 12
    if result in intervals:
        return key_notes[intervals.index(result)] + note[1:]
    else:
        return notes.diminish(key_notes[intervals.index((result + 1) % 12)] + note[1:])


def measure(note1, note2):
    res = notes.note_to_int(note2) - notes.note_to_int(note1)
    if res < 0:
        return 12 - res * -1
    else:
        return res


def augment_or_diminish_until_the_interval_is_right(note1, note2, interval):
    cur = measure(note1, note2)
    while cur != interval:
        if cur > interval:
            note2 = notes.diminish(note2)
        elif cur < interval:
            note2 = notes.augment(note2)
        cur = measure(note1, note2)

    val = 0
    for token in note2[1:]:
        if token == "#":
            val += 1
        elif token == "b":
            val -= 1

    if val > 6:
        val = val % 12
        val = -12 + val
    elif val < -6:
        val = val % -12
        val = 12 + val

    result = note2[0]
    while val > 0:
        result = notes.augment(result)
        val -= 1
    while val < 0:
        result = notes.diminish(result)
        val += 1
    return result


def invert(interval):
    interval.reverse()
    res = list(interval)
    interval.reverse()
    return res


def determine(note1, note2, shorthand=False):
    if note1[0] == note2[0]:

        def get_val(note):
            """Private function: count the value of accidentals."""
            r = 0
            for x in note[1:]:
                if x == "b":
                    r -= 1
                elif x == "#":
                    r += 1
            return r

        x = get_val(note1)
        y = get_val(note2)
        if x == y:
            if not shorthand:
                return "major unison"
            return "1"
        elif x < y:
            if not shorthand:
                return "augmented unison"
            return "#1"
        elif x - y == 1:
            if not shorthand:
                return "minor unison"
            return "b1"
        else:
            if not shorthand:
                return "diminished unison"
            return "bb1"

    n1 = notes.fifths.index(note1[0])
    n2 = notes.fifths.index(note2[0])
    number_of_fifth_steps = n2 - n1
    if n2 < n1:
        number_of_fifth_steps = len(notes.fifths) - n1 + n2

    fifth_steps = [
        ["unison", "1", 0],
        ["fifth", "5", 7],
        ["second", "2", 2],
        ["sixth", "6", 9],
        ["third", "3", 4],
        ["seventh", "7", 11],
        ["fourth", "4", 5],
    ]

    half_notes = measure(note1, note2)

    current = fifth_steps[number_of_fifth_steps]

    maj = current[2]

    if maj == half_notes:

        if current[0] == "fifth":
            if not shorthand:
                return "perfect fifth"
        elif current[0] == "fourth":
            if not shorthand:
                return "perfect fourth"
        if not shorthand:
            return "major " + current[0]
        return current[1]
    elif maj + 1 <= half_notes:

        if not shorthand:
            return "augmented " + current[0]
        return "#" * (half_notes - maj) + current[1]
    elif maj - 1 == half_notes:

        if not shorthand:
            return "minor " + current[0]
        return "b" + current[1]
    elif maj - 2 >= half_notes:
        if not shorthand:
            return "diminished " + current[0]
        return "b" * (maj - half_notes) + current[1]


def from_shorthand(note, interval, up=True):
    if not notes.is_valid_note(note):
        return False

    shorthand_lookup = [
        ["1", major_unison, major_unison],
        ["2", major_second, minor_seventh],
        ["3", major_third, minor_sixth],
        ["4", major_fourth, major_fifth],
        ["5", major_fifth, major_fourth],
        ["6", major_sixth, minor_third],
        ["7", major_seventh, minor_second],
    ]

    val = False
    for shorthand in shorthand_lookup:
        if shorthand[0] == interval[-1]:
            if up:
                val = shorthand[1](note)
            else:
                val = shorthand[2](note)

    if val == False:
        return False

    # Collect accidentals
    for x in interval:
        if x == "#":
            if up:
                val = notes.augment(val)
            else:
                val = notes.diminish(val)
        elif x == "b":
            if up:
                val = notes.diminish(val)
            else:
                val = notes.augment(val)
        else:
            return val


def is_consonant(note1, note2, include_fourths=True):
    return is_perfect_consonant(
        note1, note2, include_fourths
    ) or is_imperfect_consonant(note1, note2)


def is_perfect_consonant(note1, note2, include_fourths=True):
    dhalf = measure(note1, note2)
    return dhalf in [0, 7] or include_fourths and dhalf == 5


def is_imperfect_consonant(note1, note2):
    return measure(note1, note2) in [3, 4, 8, 9]


def is_dissonant(note1, note2, include_fourths=False):
    return not is_consonant(note1, note2, not include_fourths)
