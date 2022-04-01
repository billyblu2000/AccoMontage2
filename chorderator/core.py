import importlib
import inspect
import json
import os

from .utils.utils import listen
from .utils.excp import handle_exception
from .utils.pipeline import Pipeline
from .settings import MAXIMUM_CORES


class Core:
    registered = {
        'pre': ['PreProcessor'],
        'main': ['DP'],
        'post': ['PostProcessor'],
        'phrase': [4, 8, 12, 16, 24, 32],
        'chord_style': ['classy', 'emotional', 'standard', 'second-inversion', 'root-note', 'cluster', 'power-chord',
                        'sus2', 'seventh', 'power-octave', 'unknown', 'sus4', 'first-inversion', 'full-octave'],
        'progression_style': ['emotional', 'pop', 'dark', 'r&b', 'edm', 'unknown'],
        'style': ['pop_standard', 'pop_complex', 'dark', 'r&b', 'unknown'],
        'meta.key': ['C', 'C#', 'Db', 'Eb', 'D#', 'D', 'F', 'E', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'B', 'Bb'],
        'meta.mode': ['maj', 'min'],
        'meta.meter': ['4/4', '3/4'],
    }

    def __init__(self):
        self._pipeline = [self.preprocess_model(), self.main_model(), self.postprocess_model()]
        self.state = 0
        self.pipeline = None
        self.midi_path = ''
        self.phrase = []
        self.meta = {}
        self.output_progression_style = 'unknown'
        self.output_chord_style = 'unknown'
        self.output_style = 'unknown'

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance_list'):
            cls._instance_list = []
        if len(cls._instance_list) >= MAXIMUM_CORES:
            new_instance_list = []
            for instance in cls._instance_list:
                if instance.get_state() == 6:
                    del instance
                else:
                    new_instance_list.append(instance)
            cls._instance_list = new_instance_list
            if len(cls._instance_list) >= MAXIMUM_CORES:
                return None
        cls._instance_list.append(super(Core, cls).__new__(cls))
        return cls._instance_list[-1]

    @classmethod
    def get_core(cls):
        return Core()

    def get_pipeline_models(self):
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
        self.output_progression_style = style

    def set_output_chord_style(self, style):
        self.output_chord_style = style

    def set_output_style(self, style):
        self.output_style = style

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
        m = importlib.import_module('.utils.models.' + model_name, package='chorderator')
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
            if self.phrase[cursor] - self.phrase[cursor - 1] not in self.registered['phrase']:
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

    def run(self, cut_in, **kwargs):
        self.pipeline = Pipeline(self._pipeline)
        self.pipeline.send_in(self.midi_path,
                              cut_in=cut_in,
                              phrase=self.phrase,
                              meta=self.meta,
                              output_progression_style=self.output_progression_style,
                              output_chord_style=self.output_chord_style,
                              output_style=self.output_style,
                              **kwargs)
        return self.pipeline.send_out()

    # added APIs, making it similar with package API
    def set_melody(self, midi_path: str):
        self.midi_path = midi_path

    def set_phrase(self, phrase: list):
        self.phrase = phrase

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

    def generate(self, cut_in=False, with_log=False, **kwargs):
        verified = self.verify()
        if verified != 100:
            handle_exception(verified)
        gen = self.run(cut_in, **kwargs)
        return gen if with_log else gen[0]

    def generate_save(self, output_name, file_name=None, with_log=False, formats=None, cut_in=False, **kwargs):
        if formats is None:
            formats = ['mid']

        if file_name is None:
                file_name = output_name.split('/')[-1]

        def write_log(gen_log):
            file = open(output_name + '/' + output_name + '.json', 'w')
            json.dump(gen_log, file)
            file.close()

        try:
            os.makedirs(output_name)
        except:
            pass
        if not with_log:
            gen = self.generate(cut_in, **kwargs)
        else:
            gen, gen_log = self.generate(cut_in, with_log=with_log, **kwargs)
            write_log(gen_log)
        if 'mid' in formats:
            gen.write(output_name + '/' + file_name + '.mid')
            self.state = 5
        if 'wav' in formats:
            listen(gen, path=output_name, out='/' + file_name + '.wav')
            self.state = 6
