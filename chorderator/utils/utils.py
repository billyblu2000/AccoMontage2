import logging
import pickle
import random
import time
import os
import numpy as np
import warnings

from pretty_midi import Instrument, PrettyMIDI, Note

from ..utils import constants
from ..utils import structured
from ..utils import string
from ..settings import static_storage

try:
    from midi2audio import FluidSynth
except ImportError as e:
    FluidSynth = None

fs_exist = True
if FluidSynth is None:
    fs_exist = False
    warnings.warn('Could not import FluidSynth, audio formats writing disabled')


def pickle_read(path):
    if path == 'lib':
        Logging.info('start read progression library from source_base.pnt')
        file = open(static_storage[path], 'rb')
        lib = pickle.load(file)
        file.close()
        Logging.info('read library done')
        return lib
    else:
        with open(static_storage[path], 'rb') as file:
            return pickle.load(file)


def pitch_lists_to_midi_file(pitch_lists, midi_path):
    midi = PrettyMIDI()
    ins = Instrument(0)
    cursor = 0
    unit_length = 0.125
    for pitch_list in pitch_lists:
        for pitch in pitch_list:
            if pitch != 0:
                ins.notes.append(Note(start=cursor, end=cursor + unit_length, pitch=pitch, velocity=60))
            cursor += unit_length
    midi.instruments.append(ins)
    midi.write(midi_path)


def get_all_chord_pitches(progression_list, lib=None):
    if type(progression_list) is not list:
        progression_list = [progression_list]
    data = []
    if not lib:
        lib = pickle_read('lib')
    for progression in progression_list:
        midi_data = lib[progression.meta['source']]
        max_length = max([note[1] for note in midi_data])
        pitch_data = []
        for cursor in range(max_length):
            current_pitch_list = []
            for note in midi_data:
                if note[0] <= cursor < note[1]:
                    current_pitch_list.append(note[2])
            pitch_data.append(current_pitch_list)
        data.append(pitch_data)
    return data if type(progression_list) is list else data[0]


def nmat2ins(nmat, program=0, tempo=120, sixteenth_notes_in_bar=16) -> Instrument:
    ins = Instrument(program=program)
    snib = sixteenth_notes_in_bar
    unit_length = (60 / tempo) / 4
    for note in nmat:
        midi_note = Note(pitch=note[0], velocity=note[1],
                         start=(note[2][0] - 1) * unit_length * snib + note[2][1] * unit_length,
                         end=(note[3][0] - 1) * unit_length * snib + note[3][1] * unit_length + 0.05)
        ins.notes.append(midi_note)
    return ins


def combine_ins(*kargs: Instrument, init_tempo=120) -> PrettyMIDI:
    midi = PrettyMIDI(initial_tempo=init_tempo)
    for ins in kargs:
        midi.instruments.append(ins)
    return midi


def midi_shift(midi: PrettyMIDI, shift, tempo=120):
    unit_length = (60 / tempo) / 4
    for i in midi.instruments:
        for note in i.notes:
            note.start += unit_length * shift
            note.end += unit_length * shift
    return midi


def compute_beat_position(t, tempo_changes):
    # t is a float
    assert t >= 0
    time_stamps, tempi = tempo_changes
    beat_time = {}  # A dict to store the time stamp of a certain beat
    beat_cursor, now_time, now_tempo = 1, 0, tempi[0]
    tempi = tempi[1:]
    time_stamps = time_stamps[1:]
    while True:
        beat_length = 60 / now_tempo
        beat_time[beat_cursor] = now_time
        if now_time + beat_length <= time_stamps[0]:
            beat_cursor += 1
            now_time += beat_length
        else:
            beat_remain_percent = 1
            while now_time + beat_length * beat_remain_percent > time_stamps[0]:
                beat_remain_percent = beat_remain_percent - (time_stamps[0] - now_time) / beat_length
                now_time = time_stamps[0]
                time_stamps = time_stamps[1:]
                now_tempo = tempi[0]
                tempi = tempi[1:]
                beat_length = 60 / now_tempo
                if len(tempi) == 0:
                    break
            now_time = beat_remain_percent * beat_length + now_time
            beat_cursor += 1
        if len(tempi) == 0:
            break
    for i in beat_time.keys():
        if t < beat_time[i]:
            if t - beat_time[i - 1] > beat_time[i] - t:
                t = i
            else:
                t = i - 1
            break
    else:
        i = beat_cursor
        while True:
            beat_time[i] = beat_time[i - 1] + 60 / now_tempo
            if beat_time[i] > t:
                t = i
                break
            i += 1
    return t


def get_bar_and_position(time, beat_info):
    beat_time_list = list(beat_info.keys())
    closest = 0
    for i in range(len(beat_time_list)):
        if time < beat_time_list[i]:
            closest = i
            break
    if beat_time_list[closest] - time > time - beat_time_list[closest - 1]:
        closest -= 1
    left_unit = (beat_time_list[closest] - beat_time_list[closest - 1]) / 4
    right_unit = (beat_time_list[closest + 1] - beat_time_list[closest]) / 4
    divide_into_nine = [beat_time_list[closest - 1] + left_unit * i for i in range(4)] \
                       + [beat_time_list[closest] + right_unit * i for i in range(4)] + [beat_time_list[closest + 1]]
    micro_closest = 0
    for i in range(len(divide_into_nine)):
        if time < divide_into_nine[i]:
            micro_closest = i
            break
    if divide_into_nine[micro_closest] - time > time - divide_into_nine[micro_closest - 1]:
        micro_closest -= 1
    if micro_closest < 4:
        return beat_info[beat_time_list[closest - 1]][0], (
                beat_info[beat_time_list[closest - 1]][1] - 1) * 4 + micro_closest
    elif 4 <= micro_closest < 8:
        return beat_info[beat_time_list[closest]][0], (
                beat_info[beat_time_list[closest]][1] - 1) * 4 + micro_closest - 4
    else:
        return beat_info[beat_time_list[closest + 1]][0], 0


def get_melo_notes_from_midi(midi: PrettyMIDI, beat_audio, melo_track=0):
    """Note: [pitch, velocity, (start_bar_number, start_position_in_bar), (end_bar_number,end_position_in_bar)]"""
    my_note_list = []
    melo_notes = midi.instruments[melo_track].notes
    beat_info = {}
    bar = 1
    for line in beat_audio.readlines():
        time, position = line.split()[0], line.split()[1]
        if position == "1.0":
            bar += 1
        beat_info[float(time)] = (bar, int(position[0]))
    for note in melo_notes:
        my_note = [note.pitch, note.velocity, get_bar_and_position(note.start, beat_info),
                   get_bar_and_position(note.end, beat_info)]
        my_note_list.append(my_note)
    return my_note_list


# a function the order of notes according to tonic
# e.g., the order of F in C major is 4
# mode : M for major and m for minor
def compute_distance(tonic, this, mode='M'):
    tonic_pitch = structured.str_to_root[tonic]
    this_pitch = structured.str_to_root[this]
    pitch_distance = this_pitch - tonic_pitch
    if pitch_distance < 0:
        pitch_distance += 12
    if mode == 'M':
        pitch_distance_to_note_distance = {
            0: 1, 1: 1.5, 2: 2, 3: 2.5, 4: 3, 5: 4, 6: 4.5, 7: 5, 8: 5.5, 9: 6, 10: 6.5, 11: 7
        }
        return pitch_distance_to_note_distance[pitch_distance]
    else:
        pitch_distance_to_note_distance = {
            0: 1, 1: 1.5, 2: 2, 3: 3, 4: 3.5, 5: 4, 6: 4.5, 7: 5, 8: 6, 9: 6.5, 10: 7, 11: 7.5
        }
        return pitch_distance_to_note_distance[pitch_distance]


# a function that compute the destination note according to order
# e.g., the 4th order note of C major is F
# mode : M for major and m for minor
def compute_destination(tonic, order, mode='M'):
    root_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    if tonic == 'Db': tonic = 'C#'
    if tonic == 'Eb': tonic = 'D#'
    if tonic == 'Gb': tonic = 'F#'
    if tonic == 'Ab': tonic = 'G#'
    if tonic == 'Bb': tonic = 'A#'
    index = root_list.index(tonic)
    if mode == 'M':
        order_to_distance = {
            1: 0, 1.5: 1, 2: 2, 2.5: 3, 3: 4, 4: 5, 4.5: 6, 5: 7, 5.5: 8, 6: 9, 6.5: 10, 7: 11
        }

    else:
        order_to_distance = {
            1: 0, 1.5: 1, 2: 2, 3: 3, 3.5: 4, 4: 5, 4.5: 6, 5: 7, 6: 8, 6.5: 9, 7: 10, 7.5: 11
        }
    des_index = order_to_distance[order] + index
    des_index -= 12 if des_index >= 12 else 0
    return root_list[des_index]


def listen_pitches(midi_pitch: list, time, instrument=0):
    midi = PrettyMIDI()
    ins = Instrument(instrument)
    for i in midi_pitch:
        ins.notes.append(Note(pitch=i, start=0, end=time, velocity=80))
    midi.instruments.append(ins)
    listen(midi)


def listen(midi: PrettyMIDI, path=None, out=None):
    if not fs_exist:
        return False
    if not path:
        path = string.STATIC_DIR + "audio/"
    midi.write(path + "__listen__.mid")
    fs = FluidSynth(sound_font=string.STATIC_DIR + 'default_sound_font.sf2')
    try:
        os.makedirs(path)
    except:
        pass
    if out is None:
        out = time.strftime("%H_%M_%S", time.localtime()) + ".wav"
    fs.midi_to_audio(path + "__listen__.mid", path + out)
    os.remove(path + "__listen__.mid")
    return True


def split_huge_progression_dict(my_dict):
    all_dicts = []
    count = 0
    sub_dict = {}
    for item in my_dict.items():
        count += len(item[1])
        if count >= 30000:
            all_dicts.append(sub_dict)
            count = 0
            sub_dict = {}
        sub_dict[item[0]] = item[1]
    all_dicts.append(sub_dict)
    return all_dicts


def calculate_new_label(chord_style, progression_style):
    if progression_style == 'dark' or progression_style == 'r&b':
        new_style = progression_style
    else:
        if chord_style == 'standard':
            new_style = 'pop_standard'
        elif chord_style == 'emotional' or chord_style == 'classy':
            new_style = 'pop_complex'
        else:
            new_style = 'unknown'
    return new_style


def calculate_density(prog, WINDOW=None):
    if WINDOW is None:
        WINDOW = len(prog.progression[0])
    K = 0
    corre_with_k = {}
    progression = prog.get(only_root=True, flattened=True)
    if WINDOW >= len(progression):
        if WINDOW > 10:
            return 0, 0
        else:
            return -1, len(progression)
    try:
        while True:

            x, y = [], []
            K += WINDOW
            if K > len(progression) // 2:
                break
            for i in range(len(progression) // WINDOW):
                x.append(progression[i * WINDOW:(i + 1) * WINDOW])
                y.append(progression[i * WINDOW + K:(i + 1) * WINDOW + K])
                if (i + 1) * WINDOW + K == len(progression):
                    break
            x = np.array(x).transpose()
            y = np.array(y).transpose()
            i = 0
            while True:
                x_row = x[i]
                y_row = y[i]
                if len(np.unique(x_row)) == 1 or len(np.unique(y_row)) == 1:
                    x = np.delete(x, i, axis=0)
                    y = np.delete(y, i, axis=0)
                else:
                    i += 1
                if i >= len(x):
                    break
            corre_mat = np.corrcoef(x, y)
            avg_corre = 0
            for i in range(len(x)):
                avg_corre += corre_mat[i, i + len(x)]
            corre_with_k[K] = avg_corre / len(x)
        max_corre = -1
        max_k = 0
        for item in corre_with_k.items():
            if item[1] > max_corre:
                max_corre = item[1]
                max_k = item[0]
            elif item[1] == max_corre:
                if item[0] < max_k:
                    max_k = item[0]
        # print("Max autocorrelation {c} with K = {k}".format(c=max(value), k=max_k))
        return max_corre, max_k
    except Exception as e:
        return calculate_density(prog, WINDOW=WINDOW * 2)


def pick_progressions(*args, **kwargs):
    PICKING_PARAMS = {
        'dense_sparse': 32,
        'long_short': 100,
    }

    prog_list = kwargs['progression_list']

    new_list = []
    for i in prog_list:
        if constants.SHORT in args:
            if len(i) > PICKING_PARAMS['long_short']:
                continue
        if constants.LONG in args:
            if len(i) <= PICKING_PARAMS['long_short']:
                continue
        if constants.DENSE in args:
            if calculate_density(i)[1] > PICKING_PARAMS['dense_sparse']:
                continue
        if constants.SPARSE in args:
            if calculate_density(i)[1] <= PICKING_PARAMS['dense_sparse']:
                continue
        new_list.append(i)
    return new_list


class PathGenerator:

    def __init__(self, total_length, template_length):
        self.total_length = total_length
        self.template_length = template_length
        self.memo = {}

    def generate(self):
        return self.__generate(self.total_length)

    def __generate(self, l):
        if l in self.memo:
            return self.memo[l]
        else:
            all_path = []
            for length in self.template_length:
                if l - length < min(self.template_length):
                    continue
                for sub_path in self.__generate(l - length):
                    all_path.append(sub_path + [length])
            if l in self.template_length:
                all_path.append([l])
            self.memo[l] = all_path
            return all_path


class MIDILoader:

    def __init__(self, midi_dir=string.STATIC_DIR + 'midi/', files="*"):
        self.midi_dir = midi_dir
        self.midis = []
        self.transformed = []
        self.roll = []
        self._config = {
            'output_form': 'pitch'
        }
        self.load_midis(files)

    def config(self, output_form='pitch'):
        if output_form not in ['pitch', 'number', 'midi']:
            raise ValueError
        self._config['output_form'] = output_form

    def __get_data(self):
        if self._config['output_form'] == 'midi':
            return self.midis
        elif self._config['output_form'] == 'pitch':
            return self.transformed
        else:
            return self.roll

    def load_midis(self, files):
        if files == 'POP909':
            Logging.info("loading melodies, please wait for a few seconds...")
            data = pickle.load(open(string.RESOURCE_DIR + 'phrase_split_data/melodies.pk', 'rb'))
            Logging.info("melodies loaded.")
            self.midis = data['midi']
            self.transformed = data['melo']
            self.roll = data['roll']
        else:
            try:
                if files == '*':
                    files = os.listdir(self.midi_dir)
                    for file in files:
                        if file[-4:] == '.mid':
                            midi = PrettyMIDI(os.path.join(self.midi_dir, file))
                            try:
                                key_number = midi.key_signature_changes[0].key_number
                                if key_number >= 12:
                                    tonic = structured.root_to_str[key_number - 12]
                                    mode = 'min'
                                else:
                                    tonic = structured.root_to_str[key_number]
                                    mode = 'maj'
                            except:
                                tonic = 'C'
                                mode = 'maj'
                            self.midis.append((file, tonic, -1, mode, -1, midi))
                elif type(files) is list:
                    for file_name in files:
                        if file_name[-4:] == '.mid':
                            midi = PrettyMIDI(os.path.join(self.midi_dir, file_name))
                            try:
                                key_number = midi.key_signature_changes[0].key_number
                                if key_number >= 12:
                                    tonic = structured.root_to_str[key_number - 12]
                                    mode = 'min'
                                else:
                                    tonic = structured.root_to_str[key_number]
                                    mode = 'maj'
                            except:
                                tonic = 'C'
                                mode = 'maj'
                            self.midis.append((file_name, tonic, -1, mode, -1, midi))
                elif type(files) is str:
                    midi = PrettyMIDI(os.path.join(self.midi_dir, files))
                    try:
                        key_number = midi.key_signature_changes[0].key_number
                        if key_number >= 12:
                            tonic = structured.root_to_str[key_number - 12]
                            mode = 'min'
                        else:
                            tonic = structured.root_to_str[key_number]
                            mode = 'maj'
                    except:
                        tonic = 'C'
                        mode = 'maj'
                    self.midis.append((files, tonic, -1, mode, -1, midi))
                else:
                    raise ValueError("argument 'files' must be '*' or file name or list of file names")
                self.midi_to_pitch()
                self.pitch_to_number()
            except Exception as e:
                raise Exception('An error occored when loading midis')

    def midi_to_pitch(self):
        new = []
        for midi in self.midis:
            ins = midi[5].instruments[0]
            tempo = midi[5].get_tempo_changes()[1][0]
            note_list = np.zeros(10240, dtype=int)
            very_end = 0
            for note in ins.notes:
                start, end = self._get_note_location_from_start_end_time(note.start, note.end, tempo)
                if end > very_end:
                    very_end = end
                for i in range(start, end):
                    note_list[i] = int(note.pitch)
            note_list = note_list[:very_end]
            note_list = list(note_list)
            new.append((midi[0], midi[1], midi[2], midi[3], midi[4], note_list))
        self.transformed = new

    def pitch_to_number(self):
        new = []
        major_map = {
            0: 1, 1: 1.5, 2: 2, 3: 2.5, 4: 3, 5: 4, 6: 4.5, 7: 5, 8: 5.5, 9: 6, 10: 6.5, 11: 7
        }
        minor_map = {
            0: 1, 1: 1.5, 2: 2, 3: 3, 4: 3.5, 5: 4, 6: 4.5, 7: 5, 8: 6, 9: 6.5, 10: 7, 11: 7.5
        }
        for midi in self.transformed:
            tonic_index = structured.str_to_root[midi[1]]
            note_list = []
            map = major_map if midi[3] == 'maj' else minor_map
            for pitch in midi[5]:
                if pitch == 0:
                    note_list.append(0)
                else:
                    note_list.append(map[(pitch - tonic_index) % 12])
            new.append((midi[0], midi[1], midi[2], midi[3], midi[4], note_list))
        self.roll = new

    @staticmethod
    def _get_note_location_from_start_end_time(start_time, end_time, tempo):
        unit_length = 15 / tempo
        start_loc = int(start_time / unit_length)
        end_loc = int(end_time // unit_length + 2)
        return start_loc, end_loc

    def all(self):
        return self.sample(num=len(self.midis))

    def get(self, name='*', metre='*', mode='*', length='*', pos='*'):
        if name == "*":
            if metre == mode == length == pos == '*':
                return self.sample()
            else:
                midis = self.__get_data()
                picked_midis = []
                for i in range(len(midis)):
                    if (midis[i][2] == metre or metre == '*') and \
                            (midis[i][3] == mode or mode == '*') and \
                            (len(midis[i][5]) == length or length == '*') and \
                            (midis[i][4] == pos or pos == '*'):
                        picked_midis.append(midis[i][5])
                return picked_midis
        elif type(name) is list:
            midis = self.__get_data()
            picked_midis = []
            for i in range(len(midis)):
                if midis[i][0] in name:
                    picked_midis.append(midis[i][5])
            return picked_midis
        elif type(name) is str:
            midis = self.__get_data()
            for i in range(len(midis)):
                if midis[i][0] == name:
                    return midis[i][5]
        else:
            raise ValueError("name")

    def sample(self, num=1):
        midis = self.__get_data()
        sampled = random.sample(midis, k=num)
        sampled = [i[5] for i in sampled]
        if num == 1:
            sampled = sampled[0]
        return sampled

    def get_full_midi_ins_from_pop909(self, index: str, change_key_to=None):
        # TODO
        self.config(output_form='pitch')
        all_names = MIDILoader.auto_find_pop909_source_name(start_with=index)

        # get tonic
        midis = self.__get_data()
        for i in range(len(midis)):
            if midis[i][0] == all_names[0]:
                tonic = midis[i][1]
                break
        else:
            raise Exception('???')

        full_melo = []
        for name in all_names:
            full_melo += self.get(name=name)
        if change_key_to:
            distance = structured.root_to_pitch[structured.str_to_root[tonic]] \
                       - structured.root_to_pitch[structured.str_to_root[change_key_to]]
            for i in range(len(full_melo)):
                if full_melo[i] != 0:
                    full_melo[i] -= distance
        return full_melo

    @staticmethod
    def key_changer(melo, ori_key, des_key):
        distance = structured.str_to_root[ori_key] - structured.str_to_root[des_key]
        if distance < 0:
            distance += 12
        melo = [i + distance for i in melo]
        return melo

    @staticmethod
    def melo_to_midi(melo, tonic='C', unit=0.125):
        # ins = Instrument(program=0)
        # cursor = 0
        # for i in melo:
        #     root = major_map_backward[i]
        #     if root != -1:
        #         pitch = root_to_pitch[root]
        #         ins.notes.append(Note(start=cursor, end=cursor + 0.125, pitch=pitch, velocity=60))
        #     cursor += 0.125
        ins = Instrument(program=0)
        current_pitch = MIDILoader.__melo_number_to_pitch(melo[0])
        start = 0
        for i in range(len(melo)):
            if i == len(melo) - 1:
                note = Note(pitch=current_pitch, velocity=80, start=start * unit, end=(i + 1) * 0.125)
                ins.notes.append(note)
                break
            if melo[i + 1] != melo[i]:
                if current_pitch is not 0:
                    note = Note(pitch=current_pitch, velocity=80, start=start * unit, end=(i + 1) * 0.125)
                    ins.notes.append(note)
                current_pitch = MIDILoader.__melo_number_to_pitch(melo[i + 1])
                start = i + 1

        return ins

    @staticmethod
    def __melo_number_to_pitch(number):
        root = structured.major_map_backward[number]
        if root != -1:
            pitch = structured.root_to_pitch[root]
            return pitch
        else:
            return 0

    @staticmethod
    def auto_find_pop909_source_name(start_with=None):
        all_names = []
        temp_loader = MIDILoader(files='POP909')
        if start_with:
            if type(start_with) is str:
                start_with = [start_with]
            assert type(start_with) is list
            for this in start_with:
                for item in temp_loader.transformed:
                    if item[0][:len(this)] == this:
                        all_names.append(item[0])
        del temp_loader
        return sorted(all_names)


class Logging:

    @staticmethod
    def _preprocess(*args):
        msg = ''
        for arg in args:
            msg += str(arg) + ' '
        return msg.rstrip(' ')

    @staticmethod
    def debug(*args):
        logging.debug('\033[1;37m ' + Logging._preprocess(*args) + ' \033[0m')

    @staticmethod
    def info(*args):
        logging.info('\033[1;30m ' + Logging._preprocess(*args) + ' \033[0m')

    @staticmethod
    def warning(*args):
        logging.warning('\033[1;33m ' + Logging._preprocess(*args) + ' \033[0m')

    @staticmethod
    def error(*args):
        logging.error('\033[1;31m ' + Logging._preprocess(*args) + ' \033[0m')

    @staticmethod
    def critical(*args):
        logging.critical('\033[1;41m ' + Logging._preprocess(*args) + ' \033[0m')


if __name__ == '__main__':
    pass
