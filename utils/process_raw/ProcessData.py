import os
import pickle

from chords.Chord import Chord
from chords.ChordProgression import ChordProgression
from utils.parse_chord import CHORDS_ANALYSIS_2
from utils.string import RESOURCE_DIR, STATIC_DIR
from utils.process_raw.ProcessDataUtils import type_dict, root_map_major, root_map_minor

song_name = []
tmp_dict = {}
chord_analysis = CHORDS_ANALYSIS_2


def process_line(line):
    """a func used to process a single line, called by process_file()"""
    try:
        result = ["", ]

        # get rid of useless info and detect tonic,
        # metre and whether if starts a new paragraph
        if line[:9] == "# tonic: " or line[:9] == "# metre: ":
            return line[9:]
        line = line[len(line.split()[0]):].lstrip()
        if line.rstrip() == "silence" or line.rstrip() == "end":
            return result
        if line[0].isupper():
            result[0] = line.split()[1].rstrip(",")
            line = line[len(line.split()[0]) + len(line.split()[1]) + 1:].lstrip()
        if line[:7] == "fadeout":
            result[0] = "fadeout"
            line = line[len(line.split()[0]):].lstrip()
        if line[:7] == "refrain":
            result[0] = "refrain"
            line = line[len(line.split()[0]):].lstrip()
        if line.rstrip()[-1] is not "|":
            line = line[:-len(line.split("|")[-1])]
        else:
            line = line[:-1]

        # extract chords
        chord_list = line.split("|")
        for bar_chords in chord_list:
            if bar_chords == "":
                continue
            bar_chords_list = []
            bar_chords = bar_chords.strip()
            if " " not in bar_chords:
                bar_chords_list.append(bar_chords)
            else:
                bar_chord_list = bar_chords.split()
                memo = bar_chord_list[0]
                for chord in bar_chord_list:
                    if ":" in chord:
                        bar_chords_list.append(chord)
                        memo = chord
                    elif chord == ".":
                        bar_chords_list.append(memo)
                    elif chord == "N" or chord == "*":
                        pass
                    else:
                        raise Exception
            result.append(bar_chords_list)
        # print(result)
        return result
    except Exception as e:
        print(e)
        print("An error occurred when processing lines: ", e)
        return None


def process_file(file, source=None):
    """a function processing the whole file,
    append all the progressions in this file to progression list"""

    prog_list = []
    lines = file.readlines()
    try:
        # check if it's a new song
        title = lines[0][9:]
        if title in song_name:
            return []
        else:
            song_name.append(title)

        # get tonic and metre
        if lines[3][:9] == "# tonic: " and lines[2][:9] == "# metre: ":
            tonic = lines[3].split(" ")[-1].rstrip("\n")
            metre = lines[2].split(" ")[-1].rstrip("\n")
        elif lines[2][:9] == "# tonic: " and lines[3][:9] == "# metre: ":
            tonic = lines[2].split(" ")[-1].rstrip("\n")
            metre = lines[3].split(" ")[-1].rstrip("\n")
        else:
            raise Exception("cant't find tonic or metre")
        assert tonic[0].isupper() and metre[0].isdigit()

        # init progression and mode
        progression = None
        mode = None

        # start analyze lines
        for i in range(5, len(lines)):
            line = lines[i]

            # get chord result from process_line() function
            result = process_line(line)

            # the result of processing lines can be divided into the following
            # 1. something wrong happened or line is useless
            if result is None:
                progression = None

            # 2. line is info about tonic or metre, then change the current tonic or metre
            elif type(result) is str:
                if result[0].isdigit():
                    metre = result.strip("\n")
                else:
                    tonic = result.strip("\n")
                assert tonic[0].isupper() and metre[0].isdigit()
                continue

            # 3. line starts a new paragraph, append old progression to list and create new progression
            elif result[0] is not "" and result[0] in type_dict.keys():
                if progression is not None:
                    progression.meta["mode"] = mode
                    print(progression)
                    prog_list.append(progression)
                progression = ChordProgression(type=result[0], source=source, metre=metre, tonic=tonic)
                mode = None  # reset mode

            # 4. line start a new unknown paragraph, skip this progression
            elif result[0] is not "":
                progression = None
                # raise Exception("Cannot recognize this type:", result[0])

            # last. if nothing happens, start process the chords in result
            if progression is not None:

                # decide whether the result belongs to Major or Minor,
                # and compare the mode with the current mode

                # get all chords
                all_chords_list = set()
                for j in range(1, len(result)):
                    for k in result[j]:
                        if k not in ["N", "*", "&pause"]:
                            all_chords_list.add(k)

                # look at root
                root_in_major, root_in_minor = 0, 0
                for chord in all_chords_list:
                    root = chord.split(":")[0]
                    if type(root_map_major(root, tonic)) == int:
                        root_in_major += 1
                    if type(root_map_minor(root, tonic)) == int:
                        root_in_minor += 1

                if root_in_major == len(all_chords_list):
                    new_mode = "M"
                elif root_in_major < len(all_chords_list) and root_in_minor == len(all_chords_list):
                    new_mode = "m"
                else:
                    new_mode = "M"
                if new_mode != mode and mode is not None:
                    progression = None
                else:
                    mode = new_mode

                # append the chords in result to progression
                for j in range(1, len(result)):

                    bar_chord_list = result[j]
                    bar_chord = [0] * int((int(metre.split("/")[0]) / int(metre.split("/")[1])) * 8)
                    assert len(bar_chord) % len(bar_chord_list) == 0
                    chord_length = int(len(bar_chord) / len(bar_chord_list))
                    for k in range(len(bar_chord_list)):
                        if bar_chord_list[k] == "N" or bar_chord_list[k] == "*" or bar_chord_list[k] == "&pause":
                            my_chord = Chord(root=-1, attr=[-1, -1, -1, -1])
                        else:
                            chord_root = bar_chord_list[k].split(":")[0]
                            chord_type = bar_chord_list[k].split(":")[1]
                            for item in chord_analysis.items():
                                if chord_type in item[1]:
                                    type_num = item[0]
                                    break
                            else:
                                type_num = -1
                            my_chord = Chord(root=chord_root, attr=[type_num, -1, -1, -1])

                        bar_chord[chord_length * k:chord_length * (k + 1)] = [my_chord] * chord_length
                    if progression is not None:
                        progression.progression = progression._progression + [bar_chord]

        return prog_list

    except Exception as e:
        print("An error occurred when processing files: ", e)
        return []


def l2s(lst):
    str_ = ""
    for i in lst:
        str_ += str(i)
    return str_


def process_data(save):
    dir = RESOURCE_DIR + "billboard/McGill-Billboard/"
    prog_list, error_num, total_num = [], 0, 0
    for location in os.walk(top=dir):
        if not location[1]:
            file_dir = location[0] + "/" + location[2][0]
            file = open(file_dir)
            single_progression_list = process_file(file, source=location[0][-4:])
            if len(single_progression_list) == 0:
                error_num += 1
            prog_list += single_progression_list
            file.close()
            total_num += 1

    print("{s} succeeded, {e} failed.".format(s=total_num - error_num, e=error_num))

    # delete duplicates
    new_prog_list = []
    for progression in prog_list:
        if progression._progression not in [p._progression for p in new_prog_list]:
            new_prog_list.append(progression)
        else:
            for i in new_prog_list:
                if i._progression == progression._progression:
                    i.appeared_time += 1
                    if i.meta["source"] != progression.meta["source"]:
                        i.appeared_in_other_songs += 1
                    break
    prog_list = new_prog_list
    print(1)

    print(1)
    for progression in prog_list[:]:
        for i in progression:
            if i.root != -1:
                break
        else:
            for i in prog_list:
                if i._progression == progression._progression:
                    prog_list.remove(i)

    # save progressions
    if save == 'pk':
        file = open('progressions_with_type.pcls', 'bw')
        pickle.dump(prog_list, file, 1)
    if save == 'txt':
        progression_file = open(STATIC_DIR + "progressions_with_type.txt", "w")
        for progression in prog_list:
            progression_file.write(str(progression) + "\n")
        progression_file.close()
    print("progressions:", len(prog_list))


if __name__ == '__main__':
    process_data(save='pk')
