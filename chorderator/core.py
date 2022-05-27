import importlib
import inspect
import json
import os
import warnings
import numpy as np
import pandas as pd
import torch
from .utils.utils import listen, pickle_read
from .utils.excp import handle_exception
from .utils.pipeline import Pipeline
from .settings import MAXIMUM_CORES, ACCOMONTAGE_DATA_DIR

from .chords.ChordProgression import read_progressions


class Core:
    registered = {
        'pre': ['PreProcessor'],
        'main': ['DP'],
        'post': ['PostProcessor'],
        'texture': ['AccoMontage'],
        'phrase': [4, 8, 12, 16, 24, 32],
        'chord_style': ['classy', 'emotional', 'standard', 'second-inversion', 'root-note', 'cluster', 'power-chord',
                        'sus2', 'seventh', 'power-octave', 'unknown', 'sus4', 'first-inversion', 'full-octave'],
        'progression_style': ['emotional', 'pop', 'dark', 'r&b', 'edm', 'unknown'],
        'style': ['pop_standard', 'pop_complex', 'dark', 'r&b', 'unknown', '*'],
        'meta.key': ['C', 'C#', 'Db', 'Eb', 'D#', 'D', 'F', 'E', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'B', 'Bb'],
        'meta.mode': ['maj', 'min'],
        'meta.meter': ['4/4', '3/4'],
    }

    def __init__(self):

        self._pipeline = [self.preprocess_model(), self.main_model(), self.postprocess_model(), self.texture_model()]
        self.state = 0
        self.pipeline = None
        self.midi_path = ''
        self.phrase = []
        self.segmentation = ''
        self.meta = {}
        self.note_shift = 0
        self.output_progression_style = 'unknown'
        self.output_chord_style = 'unknown'
        self.output_style = '*'
        self.texture_spotlight = []
        self.texture_prefilter = None
        self.cache = {
            'dict': None,
            'lib': None,
            'state_dict': None,
            'phrase_data': None,
            'edge_weights': None,
            'song_index': None,
        }

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, '_instance_list'):
    #         cls._instance_list = []
    #     if len(cls._instance_list) >= MAXIMUM_CORES:
    #         new_instance_list = []
    #         for instance in cls._instance_list:
    #             if instance.get_state() == 6:
    #                 del instance
    #             else:
    #                 new_instance_list.append(instance)
    #         cls._instance_list = new_instance_list
    #         if len(cls._instance_list) >= MAXIMUM_CORES:
    #             return None
    #     cls._instance_list.append(super(Core, cls).__new__(cls))
    #     return cls._instance_list[-1]

    @classmethod
    def get_core(cls):
        return Core()

    def get_pipeline_models(self):
        return self._pipeline

    def set_pipeline(self, pre=None, main=None, post=None, texture=None):
        if pre:
            try:
                self._pipeline[0] = self.preprocess_model(pre)
            except:
                handle_exception(0)
        if main:
            try:
                self._pipeline[1] = self.main_model(main)
            except:
                handle_exception(0)
        if post:
            try:
                self._pipeline[2] = self.postprocess_model(post)
            except:
                handle_exception(0)
        if texture:
            try:
                self._pipeline[3] = None
            except:
                handle_exception(0)

    def set_note_shift(self, shift):
        self.note_shift = shift

    def set_output_progression_style(self, style: str):
        self.output_progression_style = style

    def set_output_chord_style(self, style: str):
        self.output_chord_style = style

    def set_output_style(self, style: str):
        self.output_style = style

    def set_texture_spotlight(self, spotlight: list):
        self.texture_spotlight = spotlight

    def set_texture_prefilter(self, prefilter: tuple):
        if prefilter is not None:
            assert 0 <= prefilter[0] <= 4 and 0 <= prefilter[1] <= 4 and len(prefilter) == 2
            self.texture_prefilter = prefilter

    def set_cache(self, **kwargs):
        print('check', kwargs.keys())
        for cache_name in ['lib, dict, state_dict', 'phrase_data', 'edge_weights', 'song_index']:
            if cache_name in kwargs:
                self.cache[cache_name] = kwargs[cache_name]

    def load_data(self):
        self.cache = {
            'dict': read_progressions('dict'),
            'lib': pickle_read('lib'),
            'state_dict': torch.load(ACCOMONTAGE_DATA_DIR + '/model_master_final.pt', map_location=torch.device('cpu')) \
                if not torch.cuda.is_available() else torch.load(ACCOMONTAGE_DATA_DIR + '/model_master_final.pt',
                                                                 map_location=torch.device('cuda')),
            'phrase_data': np.load(ACCOMONTAGE_DATA_DIR + '/phrase_data0714.npz', allow_pickle=True),
            'edge_weights': np.load(ACCOMONTAGE_DATA_DIR + '/edge_weights_0714.npz', allow_pickle=True),
            'song_index': pd.read_excel(ACCOMONTAGE_DATA_DIR + '/POP909 4bin quntization/four_beat_song_index.xlsx'),
        }
        return self.cache

    def preprocess_model(self, model_name=registered['pre'][0]):
        if model_name not in Core.registered['pre']:
            return False
        return self.__import_model(model_name)

    def main_model(self, model_name=registered['main'][0]):
        if model_name not in Core.registered['main']:
            return False
        return self.__import_model(model_name)

    def postprocess_model(self, model_name=registered['post'][0]):
        if model_name not in Core.registered['post']:
            return False
        return self.__import_model(model_name)

    def texture_model(self, model_name=registered['texture'][0]):
        if model_name not in Core.registered['texture']:
            return False
        return self.__import_model(model_name)

    def get_state(self):
        if self.state <= 5:
            if self.pipeline is not None:
                return self.pipeline.state
            else:
                return 0
        else:
            return self.state

    @staticmethod
    def __import_model(model_name):
        surpass = ['Chord', 'ChordProgression', 'MIDILoader', 'Logging', 'Instrument', 'PrettyMIDI', 'Note']
        try:
            m = importlib.import_module('.utils.models.' + model_name, package='chorderator')
        except:
            m = importlib.import_module('.utils.models.accomontage.' + model_name, package='chorderator')
        for cls in dir(m):
            if inspect.isclass(getattr(m, cls)) and cls not in surpass:
                return getattr(m, cls)
        else:
            return False

    def verify(self):
        if False in self._pipeline:
            return 200 + self._pipeline.index(False) + 1

        checks = [self.__check_midi_path(),
                  self.__check_phrase(),
                  self.__check_segmentation(),
                  self.__check_meta(),
                  self.__check_style()]

        for check in checks:
            if check != 100:
                return check
        else:
            return 100

    def __check_midi_path(self):
        return 301 if self.midi_path == '' else 100

    def __check_phrase(self):
        if not self.phrase:
            if self.segmentation:
                self.phrase = self.__segmentation_to_phrase(self.segmentation)
            else:
                return 311
        cursor = 1
        while cursor < len(self.phrase):
            if self.phrase[cursor] - self.phrase[cursor - 1] not in self.registered['phrase']:
                return 312
            cursor += 1
        else:
            return 100

    def __check_segmentation(self):
        if not self.segmentation:
            if self.phrase:
                self.segmentation = self.__phrase_to_segmentation(self.phrase)
            else:
                return 311
        phrase = self.__segmentation_to_phrase(self.segmentation)
        cursor = 1
        while cursor < len(phrase):
            if phrase[cursor] - phrase[cursor - 1] not in self.registered['phrase']:
                return 312
            cursor += 1
        else:
            return 100

    def __check_meta(self):
        if self.meta == {}:
            return 321
        if 'tonic' not in self.meta.keys():
            return 322
        if 'meter' not in self.meta.keys():
            self.meta['meter'] = '4/4'
            warnings.warn('Meter auto set to 4/4/. Please set meter if this is not your expectation')
        if 'mode' not in self.meta.keys():
            self.meta['mode'] = 'maj'
            warnings.warn('Mode auto set to major. Please set mode if this is not your expectation')
        if self.meta['tonic'] not in self.registered['meta.key']:
            return 323
        if self.meta['mode'] not in self.registered['meta.mode']:
            return 324
        if self.meta['meter'] not in self.registered['meta.meter']:
            return 325
        return 100

    def __check_chord_style(self):
        return 331 if self.output_chord_style not in self.registered['chord_style'] else 100

    def __check_progression_style(self):
        return 341 if self.output_progression_style not in self.registered['progression_style'] else 100

    def __check_style(self):
        if type(self.output_style) == str:
            return 351 if self.output_style not in self.registered['style'] else 100
        if type(self.output_style) == list:
            for i in self.output_style:
                if i not in self.registered['style']:
                    return 351
            else:
                return 100
        return 351

    def run(self, cut_in, cut_in_arg, with_texture, **kwargs):
        self.pipeline = Pipeline(self._pipeline)
        if self.cache['dict'] is None:
            templates = read_progressions('dict')
            self.cache['dict'] = templates
        if self.cache['lib'] is None:
            lib = pickle_read('lib')
            self.cache['lib'] = lib
        self.pipeline.send_in(self.midi_path,
                              cut_in=cut_in,
                              cut_in_arg=cut_in_arg,
                              with_texture=with_texture,
                              phrase=self.phrase,
                              meta=self.meta,
                              note_shift=self.note_shift,
                              output_progression_style=self.output_progression_style,
                              output_chord_style=self.output_chord_style,
                              output_style=self.output_style,
                              lib=self.cache['lib'],
                              templates=self.cache['dict'],
                              state_dict=self.cache['state_dict'],
                              phrase_data=self.cache['phrase_data'],
                              edge_weights=self.cache['edge_weights'],
                              song_index=self.cache['song_index'],
                              segmentation=self.segmentation,
                              texture_spotlight=self.texture_spotlight,
                              texture_prefilter=self.texture_prefilter,
                              **kwargs)
        return self.pipeline.send_out()

    # added APIs, making it similar with package API
    def set_melody(self, midi_path: str):
        self.midi_path = midi_path

    def set_phrase(self, phrase: list):
        warnings.warn('set_phrase not supported currently, should use set_segmentation')

    @staticmethod
    def __segmentation_to_phrase(s):
        phrase = [1]
        memo = ''
        for i in s:
            if i == '\\':
                return phrase
            if not i.isdigit():
                if memo != '':
                    phrase.append(phrase[-1] + int(memo))
                    memo = ''
            else:
                memo += i
        return phrase[:-1]

    @staticmethod
    def __phrase_to_segmentation(p):
        seg = ''
        for i in range(len(p) - 1):
            seg += 'A' + str(p[i + 1] - p[i])
        return seg + '\n'

    def set_segmentation(self, segmentation):
        if self.phrase:
            if self.phrase != self.__segmentation_to_phrase(segmentation):
                warnings.warn(
                    'Segmentation {} not match phrase {}, using segmentation'.format(segmentation, self.phrase))
                self.phrase = self.__segmentation_to_phrase(segmentation)
        self.segmentation = segmentation + '\n'
        self.phrase = self.__segmentation_to_phrase(self.segmentation)

    def set_meta(self, tonic: str = None, mode: str = None, meter: str = None, tempo=None):
        if tonic is not None:
            self.meta['tonic'] = tonic
        if mode is not None:
            self.meta['mode'] = mode
        if meter is not None:
            self.meta['meter'] = meter
        if tempo is not None:
            self.meta['tempo'] = tempo

    def set_preprocess_model(self, name: str):
        self.set_pipeline(pre=name)

    def set_main_model(self, name: str):
        self.set_pipeline(main=name)

    def set_postprocess_model(self, name: str):
        self.set_pipeline(post=name)

    def set_texture_model(self, name: str):
        self.set_pipeline(texture=name)

    def generate(self, cut_in=False, cut_in_arg=None, with_texture=True, log=False, **kwargs):
        verified = self.verify()
        if verified != 100:
            handle_exception(verified)
        gen = self.run(cut_in, cut_in_arg, with_texture, **kwargs)
        return gen if log else gen[0:2]

    def generate_save(self, output_name, task='chord_and_textured_chord', log=True, wav=False, **kwargs):

        cwd = os.getcwd()
        try:
            if 'base_dir' in kwargs:
                os.makedirs(kwargs['base_dir'], exist_ok=True)
                os.chdir(kwargs['base_dir'])
            os.makedirs(output_name)
        except:
            pass
        os.chdir(cwd)

        if task == 'chord':
            cut_in, cut_in_arg, with_texture = False, None, False
        elif task == 'textured_chord' or task == 'chord_and_textured_chord':
            cut_in, cut_in_arg, with_texture = False, None, True
        elif task == 'texture':
            cut_in, cut_in_arg, with_texture = 'from_texture', kwargs['cut_in_arg'], True
        else:
            raise RuntimeError(task)

        if 'cut_in_arg' in kwargs:
            del kwargs['cut_in_arg']

        if not log:
            gen, chord_gen = self.generate(cut_in=cut_in, cut_in_arg=cut_in_arg, with_texture=with_texture, **kwargs)
        else:
            gen, chord_gen, gen_log = self.generate(cut_in=cut_in, cut_in_arg=cut_in_arg, with_texture=with_texture,
                                                    log=True, **kwargs)
            if 'base_dir' in kwargs:
                cwd = os.getcwd()
                os.chdir(kwargs['base_dir'])
            file = open(output_name + '/chord_gen_log.json', 'w')
            json.dump(gen_log, file)
            file.close()
            if 'base_dir' in kwargs:
                os.chdir(cwd)

        if 'base_dir' in kwargs:
            cwd = os.getcwd()
            os.chdir(kwargs['base_dir'])
        if task == 'chord' or task == 'chord_and_textured_chord':
            chord_gen.write(output_name + '/chord_gen.mid')
        if task == 'textured_chord' or task == 'texture' or task == 'chord_and_textured_chord':
            gen.write(output_name + '/textured_chord_gen.mid')
        self.state = 6
        if wav:
            if task == 'chord':
                listen(chord_gen, path=output_name, out='/chord_gen.wav')
            if task == 'textured_chord' or task == 'texture' or task == 'chord_and_textured_chord':
                listen(gen, path=output_name, out='/textured_chord_gen.wav')
        self.state = 7
        if 'base_dir' in kwargs:
            os.chdir(cwd)

    def __str__(self):
        s = '''Chorderator Core (
state = {}
pipeline = {}
melody_midi_path = {}
phrase = {}
segmentation = {}
melody_meta_data = {}
chord_gen_style = {}
texture_spotlight = {}
texture_prefilter = {})'''.format(self.state,
                                  self.pipeline,
                                  self.midi_path,
                                  self.phrase,
                                  self.segmentation.rstrip('\n'),
                                  self.meta,
                                  self.output_style,
                                  self.texture_spotlight,
                                  self.texture_prefilter)
        return s
