import time

from pretty_midi import *
from utils.structured import str_to_root
from utils.string import STATIC_DIR
from utils.constants import *

try:
    from midi2audio import FluidSynth
except:
    def FluidSynth():
        return None


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


def compute_distance(tonic, this, mode='M'):
    tonic_pitch = str_to_root(tonic)
    this_pitch = str_to_root(this)
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



def listen_pitches(midi_pitch: list, time, instrument=0):
    midi = PrettyMIDI()
    ins = Instrument(instrument)
    for i in midi_pitch:
        ins.notes.append(Note(pitch=i, start=0, end=time, velocity=80))
    midi.instruments.append(ins)
    listen(midi)


def listen(midi: PrettyMIDI, out=time.strftime("%H_%M_%S", time.localtime()) + ".wav"):
    midi.write(STATIC_DIR + "audio/" + "midi.mid")
    fs = FluidSynth()
    date = time.strftime("%Y-%m-%d", time.localtime()) + "/"
    try:
        os.makedirs(STATIC_DIR + "audio/" + date)
    except:
        pass
    if fs is not None:
        fs.midi_to_audio(STATIC_DIR + "audio/" + "midi.mid", STATIC_DIR + "audio/" + date + out)
        os.remove(STATIC_DIR + "audio/" + "midi.mid")


def pick_progressions(*args, **kwargs):
    PICKING_PARAMS = {
        'dense_sparse': 16,
        'long_short': 64,
    }

    prog_list = kwargs['progression_list']

    def calculate_density(prog, WINDOW=None):
        if WINDOW is None:
            WINDOW = len(prog.progression[0])
        K = 0
        corre_with_k = {}
        progression = [i for i in prog]
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

    new_list = []
    for i in prog_list:
        if SHORT in args:
            if len(i) > PICKING_PARAMS['long_short']:
                continue
        if LONG in args:
            if len(i) <= PICKING_PARAMS['long_short']:
                continue
        if DENSE in args:
            if calculate_density(i)[1] > PICKING_PARAMS['dense_sparse']:
                continue
        if SPARSE in args:
            if calculate_density(i)[1] <= PICKING_PARAMS['dense_sparse']:
                continue
        new_list.append(i)
    return new_list


if __name__ == '__main__':
    pass
