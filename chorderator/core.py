import importlib
import inspect
import time

from utils.pipeline import Pipeline
from utils.utils import Logging


class Core:
    registered_models = {
        'pre': ['PreProcessor'],
        'main': ['DP'],
        'post': ['PostProcessor']
    }

    def __init__(self):
        self._pipeline = [self.preprocess_model(), self.main_model(), self.postprocess_model()]
        self.midi_path = ''
        self.meta = {}
        self.output_progression_style = None
        self.output_chord_style = None

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
            self._pipeline[0] = self.preprocess_model(pre)
        if main:
            self._pipeline[1] = self.main_model(main)
        if post:
            self._pipeline[2] = self.postprocess_model(post)

    def preprocess_model(self, model_name=registered_models['pre'][0]):
        if model_name not in Core.registered_models['pre']:
            return False
        return self.__import_model(model_name)

    def main_model(self, model_name=registered_models['main'][0]):
        if model_name not in Core.registered_models['main']:
            return False
        return self.__import_model(model_name)

    def postprocess_model(self, model_name=registered_models['post'][0]):
        if model_name not in Core.registered_models['post']:
            return False
        return self.__import_model(model_name)

    @staticmethod
    def __import_model(model_name):
        surpass = ['Chord', 'ChordProgression', 'MIDILoader', 'Logging']
        m = importlib.import_module('utils.models.' + model_name)
        for cls in dir(m):
            if inspect.isclass(getattr(m, cls)) and cls not in surpass:
                return getattr(m, cls)
        else:
            return False

    def verify_pipeline(self):
        if False in self._pipeline:
            return 200 + self._pipeline.index(False) + 1
        else:
            return 100

    def run(self):
        pipeline = Pipeline(self._pipeline)
        pipeline.send_in(self.midi_path,meta=self.meta)
        print(pipeline.send_out())
