import numpy as np
import pandas as pd
import pretty_midi

from ....settings import ACCOMONTAGE_DATA_DIR
from .util_tools.acc_utils import split_phrases
from .util_tools import format_converter_update as cvt
from .util_tools.AccoMontage import find_by_length, dp_search, render_acc, ref_spotlight, get_texture_filter, \
    render_acc_new

import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
DATA_DIR = ACCOMONTAGE_DATA_DIR


class AccoMontage:

    def __init__(self, midi, log, segmentation, note_shift=0, spotlight=[], prefilter=None,
                 state_dict=None, phrase_data=None, edge_weights=None, song_index=None, original_tempo=120):
        # all_ref = [i[:-1] for i in open(r'D:\projects\Chorderator\a.txt', encoding='utf-8').readlines()]
        # all_ref.remove('今生只为遇见你')
        self.final_output = None
        self.midi = midi
        self.chord_gen_log = log
        self.segmentation = segmentation
        self.note_shift = note_shift//4
        self.spotlight = spotlight
        self.prefilter = prefilter
        self.state_dict = state_dict
        self.phrase_data = phrase_data
        self.edge_weights = edge_weights
        self.song_index = song_index
        self.original_tempo = original_tempo

    def solve(self):
        SPOTLIGHT, PREFILTER = self.spotlight, self.prefilter
        SEGMENTATION, NOTE_SHIFT = self.segmentation, self.note_shift

        print('Loading Reference Data')
        if not self.phrase_data:
            data = np.load(DATA_DIR + '/phrase_data0714.npz', allow_pickle=True)
        else:
            data = self.phrase_data
        melody = data['melody']
        acc = data['acc']
        chord = data['chord']
        if not self.edge_weights:
            edge_weights = np.load(DATA_DIR + '/edge_weights_0714.npz', allow_pickle=True)
        else:
            edge_weights = self.edge_weights

        print('Processing Query Lead Sheet')
        melody_track, chord_track = self.midi.instruments[0], self.midi.instruments[1]
        downbeats = self.midi.get_downbeats()
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

        piano_roll = np.concatenate((melody_matrix, chroma), axis=-1)  # T*142, quantized at 16th
        query_phrases = split_phrases(SEGMENTATION)  # [('A', 8, 0), ('A', 8, 8), ('B', 8, 16), ('B', 8, 24)]
        query_seg = [item[0] + str(item[1]) for item in query_phrases]  # ['A8', 'A8', 'B8', 'B8']

        melody_queries = []
        for item in query_phrases:
            start_bar = item[-1]
            length = item[-2]
            segment = piano_roll[start_bar * 16: (start_bar + length) * 16]
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

        print('Phrase Selection Begins:\n\t', len(query_phrases), 'phrases in query lead sheet;\n\t', 'Refer to',
              SPOTLIGHT,
              'as much as possible;\n\t', 'Set note density filter:', PREFILTER, '.')
        phrase_indice, chord_shift = dp_search(
            melody_queries,
            query_seg,
            acc_pool,
            edge_weights,
            texture_filter,
            filter_id=PREFILTER,
            spotlights=ref_spotlight(SPOTLIGHT, song_index=self.song_index))

        path = phrase_indice[0]
        shift = chord_shift[0]
        reference_set = []
        df = pd.read_excel(DATA_DIR + "/POP909 4bin quntization/four_beat_song_index.xlsx") \
            if self.song_index is None else self.song_index
        for idx_phrase, phrase in enumerate(query_phrases):
            phrase_len = phrase[1]
            song_ref = acc_pool[phrase_len][-1]
            idx_song = song_ref[path[idx_phrase][0]][0]
            song_name = df.iloc[idx_song][1]
            reference_set.append((idx_song, song_name))
        print('Reference chosen:', reference_set)
        print('Pitch Transposition (Fit by Model):', shift)

        print('Generating...')

        # AccoMontage MIDI render
        midi = render_acc(piano_roll, chord_table, query_seg, path, shift, acc_pool, state_dict=self.state_dict)

        if self.original_tempo != 120:
            for ins in midi.instruments:
                for note in ins.notes:
                    note.start = note.start * 120 / self.original_tempo
                    note.end = note.end * 120 / self.original_tempo
        self.final_output = midi
        return midi

    def get(self):
        return self.final_output
