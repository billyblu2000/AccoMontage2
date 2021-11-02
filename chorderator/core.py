import importlib
import inspect
import time

from chords.ChordProgression import print_progression_list
from utils.excp import handle_exception
from utils.pipeline import Pipeline
from utils.utils import Logging


class Core:
    registered = {
        'pre': ['PreProcessor'],
        'main': ['DP'],
        'post': ['PostProcessor'],
        'phrase': [4, 8, 12, 16, 24, 32],
        'chord_style':['classy', 'emotional','standard', 'second-inversion', 'root-note', 'cluster', 'power-chord',
                       'sus2', 'seventh', 'power-octave', 'unknown', 'sus4', 'first-inversion', 'full-octave'],
        'progression_style':['emotional', 'pop','dark', 'r&b', 'edm', 'unknown'],
        'meta.key':['C', 'C#', 'Db', 'Eb', 'D#', 'D', 'F', 'E', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'B', 'Bb'],
        'meta.mode':['maj', 'min'],
        'meta.meter':['4/4', '3/4'],
    }

    def __init__(self):
        self._pipeline = [self.preprocess_model(), self.main_model(), self.postprocess_model()]
        self.midi_path = ''
        self.phrase = []
        self.meta = {}
        self.output_progression_style = 'unknown'
        self.output_chord_style = 'unknown'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Core, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_core(cls):
        core = Core()
        return core

    def get_pipeline(self):
        return self._pipeline

    def set_pipeline(self, pre=None, main=None, post=None):
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

    def set_output_progression_style(self, style):
        if style not in ['pop']:
            handle_exception(0)
        self.output_progression_style = style

    def set_output_chord_style(self, style):
        if style not in ['standard']:
            handle_exception(0)
        self.output_chord_style = style

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

    @staticmethod
    def __import_model(model_name):
        surpass = ['Chord', 'ChordProgression', 'MIDILoader', 'Logging', 'Instrument', 'PrettyMIDI', 'Note']
        m = importlib.import_module('utils.models.' + model_name)
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
                  self.__check_meta(),
                  self.__check_chord_style(),
                  self.__check_progression_style()]

        for check in checks:
            if check != 100:
                return check
        else:
            return 100

    def __check_midi_path(self):
        return 301 if self.midi_path == '' else 100

    def __check_phrase(self):
        if not self.phrase:
            return 311
        cursor = 1
        while cursor < len(self.phrase):
            if self.phrase[cursor] - self.phrase[cursor-1] not in self.registered['phrase']:
                return 312
            cursor += 1
        else:
            return 100

    def __check_meta(self):
        if self.meta == {}:
            return 321
        if 'tonic' not in self.meta.keys() \
                or 'meter' not in self.meta.keys() \
                or 'mode' not in self.meta.keys():
            return 322
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

    def run(self, output_name):
        pipeline = Pipeline(self._pipeline)
        pipeline.send_in(self.midi_path,
                         phrase=self.phrase,
                         meta=self.meta,
                         output_progression_style=self.output_progression_style,
                         output_chord_style=self.output_chord_style)
        return pipeline.send_out(output_name)
