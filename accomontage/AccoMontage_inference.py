import pretty_midi as pyd
import numpy as np
import pandas as pd
import datetime

from .util_tools.acc_utils import split_phrases
from .util_tools import format_converter_update as cvt
from .util_tools.AccoMontage import find_by_length, dp_search, render_acc, ref_spotlight, get_texture_filter

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
DATA_DIR = "/".join(os.path.abspath(__file__).replace('\\', '/').split("/")[:-2]) + '/accomontage/data files'

def accomontage(song_name,
                song_root,
                segmentation,
                note_shift=0,
                output_root='',
                output_name='',
                spotlight=[],
                prefilter=(4, 1),
                state_dict=None,
                phrase_data=None,
                edge_weights=None,
                song_index=None,
                ):
    SPOTLIGHT, PREFILTER = spotlight, prefilter
    SONG_NAME, SONG_ROOT, SEGMENTATION, NOTE_SHIFT = song_name, song_root, segmentation, note_shift

    print('Loading Reference Data')
    data = np.load(DATA_DIR + '/phrase_data0714.npz', allow_pickle=True) if phrase_data is None else phrase_data
    melody = data['melody']
    acc = data['acc']
    chord = data['chord']
    edge_weights = np.load(DATA_DIR + '/edge_weights_0714.npz', allow_pickle=True) if edge_weights is None else edge_weights

    print('Processing Query Lead Sheet')
    midi = pyd.PrettyMIDI(os.path.join(SONG_ROOT, SONG_NAME))
    melody_track, chord_track = midi.instruments[0], midi.instruments[1]
    downbeats = midi.get_downbeats()
    melody_matrix = cvt.melody_data2matrix(melody_track, downbeats)  # T*130, quantized at 16th note
    if not NOTE_SHIFT == 0:
        melody_matrix = np.concatenate(
            (melody_matrix[int(NOTE_SHIFT * 4):, :], melody_matrix[-int(NOTE_SHIFT * 4):, :]), axis=0)
    chroma = cvt.chord_data2matrix(chord_track, downbeats, 'quater')  # T*36, quantized at 16th note (quater beat)
    if not NOTE_SHIFT == 0:
        chroma = np.concatenate((chroma[int(NOTE_SHIFT * 4):, :], chroma[-int(NOTE_SHIFT * 4):, :]), axis=0)
    chord_table = chroma[::4, :]  # T'*36, quantized at 4th notes
    # chord_table[-8:, :] = chord_table[56:64, :]
    chroma = chroma[:, 12: -12]  # T*12, quantized at 16th notes

    pianoRoll = np.concatenate((melody_matrix, chroma), axis=-1)  # T*142, quantized at 16th
    query_phrases = split_phrases(SEGMENTATION)  # [('A', 8, 0), ('A', 8, 8), ('B', 8, 16), ('B', 8, 24)]
    query_seg = [item[0] + str(item[1]) for item in query_phrases]  # ['A8', 'A8', 'B8', 'B8']

    melody_queries = []
    for item in query_phrases:
        start_bar = item[-1]
        length = item[-2]
        segment = pianoRoll[start_bar * 16: (start_bar + length) * 16]
        melody_queries.append(segment)  # melody queries: list of T16*142, segmented by phrases

    print('Processing Reference Phrases')
    acc_pool = {}
    (mel, acc_, chord_, song_reference) = find_by_length(melody, acc, chord, 8)
    acc_pool[8] = (mel, acc_, chord_, song_reference)

    (mel, acc_, chord_, song_reference) = find_by_length(melody, acc, chord, 4)
    acc_pool[4] = (mel, acc_, chord_, song_reference)

    (mel, acc_, chord_, song_reference) = find_by_length(melody, acc, chord, 6)
    acc_pool[6] = (mel, acc_, chord_, song_reference)

    texture_filter = get_texture_filter(acc_pool)

    print('Phrase Selection Begins:\n\t', len(query_phrases), 'phrases in query lead sheet;\n\t', 'Refer to', SPOTLIGHT,
          'as much as possible;\n\t', 'Set note density filter:', PREFILTER, '.')
    phrase_indice, chord_shift = dp_search(
        melody_queries,
        query_seg,
        acc_pool,
        edge_weights,
        texture_filter,
        filter_id=PREFILTER,
        spotlights=ref_spotlight(SPOTLIGHT, song_index=song_index))

    path = phrase_indice[0]
    shift = chord_shift[0]
    reference_set = []
    df = pd.read_excel(DATA_DIR + "/POP909 4bin quntization/four_beat_song_index.xlsx") \
        if song_index is None else song_index
    for idx_phrase, phrase in enumerate(query_phrases):
        phrase_len = phrase[1]
        song_ref = acc_pool[phrase_len][-1]
        idx_song = song_ref[path[idx_phrase][0]][0]
        song_name = df.iloc[idx_song][1]
        reference_set.append((idx_song, song_name))
    print('Reference chosen:', reference_set)
    print('Pitch Transpositon (Fit by Model):', shift)

    print('Generating...')
    midi = render_acc(pianoRoll, chord_table, query_seg, path, shift, acc_pool, state_dict=state_dict)
    output_name = SONG_NAME if output_name == '' else output_name
    output_path = output_root + '/' + output_name if output_root != '' else output_name
    midi.write(output_path)
    print('Result saved at', output_path)


if __name__ == '__main__':

    """
    Inference Script of AccoMontage 

    To run inference with AccoMontage, you should specify the following:
    Required:
        SONG_NAME & SONG_ROOT
            -- directory to a MIDI lead sheet file. This MIDI file should consists of two tracks, each containing melody (monophonic) and chord (polyphonic). Now complex chords (9th, 11th, and more) is supported.
        SEGMENTATION
            -- phrase annotation (string) of the MIDI file. For example, for an AABB song with 8 bars for each phrase, the annotation should be in the format 'A8A8B8B8\n'. Note that by default we only support the transition among 4-bar, 6-bar, and 8-bar phrases
        NOTE_SHIFT
            -- The number of upbeats in the  pickup bar (can be float). If no upbeat, specify 0.
    Optional:
        SPOTLIGHT
            -- a list of names of your prefered reference songs. See all 860 supported reference songs (Chinese POP) at ./data files/POP909 4bin quntization/four_beat_song_index.
        PREFILTER
            -- a tuple (a, b) controlling rhythmic patters. a, b can be integers in [0, 4], each controlling horrizontal rhythmic density and vertical voice number. Ther higher number, the denser rhythms.

    """

    """
    Configurations upon inference
    """

    SPOTLIGHT = []

    # PREFILTER = None
    PREFILTER = (4, 1)

    # SONG_NAME, SEGMENTATION, NOTE_SHIFT = 'Boggy Brays.mid', 'A8A8B8B8\n', 0
    # SONG_NAME, SEGMENTATION, NOTE_SHIFT = 'Cuillin Reel.mid', 'A4A4B8B8\n', 1
    # SONG_NAME, SEGMENTATION, NOTE_SHIFT = "Kitty O'Niel's Champion.mid", 'A4A4B4B4A4A4B4B4\n', 1
    SONG_NAME, SEGMENTATION, NOTE_SHIFT = 'Castles in the Air.mid', 'A8A8B8B8\n', 1
    # SONG_NAME, SEGMENTATION, NOTE_SHIFT = "Proudlocks's Variation.mid", 'A8A8B8B8\n', 1
    # SONG_NAME, SEGMENTATION, NOTE_SHIFT = 'ECNU University Song.mid', 'A8A8B8B8C8D8E4F6A8A8B8B8C8D8E4F6\n', 0
    SONG_ROOT = './demo/demo lead sheets'

    """
    Inferencing
    """
    print('Loading Reference Data')
    data = np.load('./data files/phrase_data0714.npz', allow_pickle=True)
    melody = data['melody']
    acc = data['acc']
    chord = data['chord']

    # For saving time, we directly load in edge weights instead of actually infering the model. Currently, we only support the transition among 4-bar, 6-bar, and 8-bar phrases
    edge_weights = np.load('./data files/edge_weights_0714.npz', allow_pickle=True)

    print('Processing Query Lead Sheet')
    midi = pyd.PrettyMIDI(os.path.join(SONG_ROOT, SONG_NAME))
    melody_track, chord_track = midi.instruments[0], midi.instruments[1]
    downbeats = midi.get_downbeats()
    melody_matrix = cvt.melody_data2matrix(melody_track, downbeats)  # T*130, quantized at 16th note
    if not NOTE_SHIFT == 0:
        melody_matrix = np.concatenate(
            (melody_matrix[int(NOTE_SHIFT * 4):, :], melody_matrix[-int(NOTE_SHIFT * 4):, :]), axis=0)
    chroma = cvt.chord_data2matrix(chord_track, downbeats, 'quater')  # T*36, quantized at 16th note (quater beat)
    if not NOTE_SHIFT == 0:
        chroma = np.concatenate((chroma[int(NOTE_SHIFT * 4):, :], chroma[-int(NOTE_SHIFT * 4):, :]), axis=0)
    chord_table = chroma[::4, :]  # T'*36, quantized at 4th notes
    # chord_table[-8:, :] = chord_table[56:64, :]
    chroma = chroma[:, 12: -12]  # T*12, quantized at 16th notes

    pianoRoll = np.concatenate((melody_matrix, chroma), axis=-1)  # T*142, quantized at 16th
    query_phrases = split_phrases(SEGMENTATION)  # [('A', 8, 0), ('A', 8, 8), ('B', 8, 16), ('B', 8, 24)]
    query_seg = [item[0] + str(item[1]) for item in query_phrases]  # ['A8', 'A8', 'B8', 'B8']

    melody_queries = []
    for item in query_phrases:
        start_bar = item[-1]
        length = item[-2]
        segment = pianoRoll[start_bar * 16: (start_bar + length) * 16]
        melody_queries.append(segment)  # melody queries: list of T16*142, segmented by phrases

    print('Processing Reference Phrases')
    acc_pool = {}
    (mel, acc_, chord_, song_reference) = find_by_length(melody, acc, chord, 8)
    acc_pool[8] = (mel, acc_, chord_, song_reference)

    (mel, acc_, chord_, song_reference) = find_by_length(melody, acc, chord, 4)
    acc_pool[4] = (mel, acc_, chord_, song_reference)

    (mel, acc_, chord_, song_reference) = find_by_length(melody, acc, chord, 6)
    acc_pool[6] = (mel, acc_, chord_, song_reference)

    texture_filter = get_texture_filter(acc_pool)

    print('Phrase Selection Begins:\n\t', len(query_phrases), 'phrases in query lead sheet;\n\t', 'Refer to', SPOTLIGHT,
          'as much as possible;\n\t', 'Set note density filter:', PREFILTER, '.')
    phrase_indice, chord_shift = dp_search(
        melody_queries,
        query_seg,
        acc_pool,
        edge_weights,
        texture_filter,
        filter_id=PREFILTER,
        spotlights=ref_spotlight(SPOTLIGHT))

    path = phrase_indice[0]
    shift = chord_shift[0]
    reference_set = []
    df = pd.read_excel("./data files/POP909 4bin quntization/four_beat_song_index.xlsx")
    for idx_phrase, phrase in enumerate(query_phrases):
        phrase_len = phrase[1]
        song_ref = acc_pool[phrase_len][-1]
        idx_song = song_ref[path[idx_phrase][0]][0]
        song_name = df.iloc[idx_song][1]
        reference_set.append((idx_song, song_name))
    print('Reference chosen:', reference_set)
    print('Pitch Transpositon (Fit by Model):', shift)
    # uncomment if you want the acc register to be lower or higher
    # for i in range(len(shift)):
    #    if shift[i] > 0: 
    #        shift[i] = shift[i] - 6
    # print('Adjusted Pitch Transposition:', shift)

    time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = './demo/demo_generate/' + time + '.mid'
    print('Generating...')
    midi = render_acc(pianoRoll, chord_table, query_seg, path, shift, acc_pool)
    midi.write(save_path)
    print('Result saved at', save_path)
