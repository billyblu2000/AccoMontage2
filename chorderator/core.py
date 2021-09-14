import importlib


class Core:
    registered_models = {
        'pre': [''],
        'main': ['DP'],
        'post': ['']
    }

    def __init__(self):
        self._pipeline = [self.preprocess_model(), self.main_model(), self.postprocess_model()]

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

    def preprocess_model(self, model_name=''):
        if model_name not in Core.registered_models['pre']:
            return False
        return self.__import_model(model_name)

    def main_model(self, model_name=''):
        if model_name not in Core.registered_models['main']:
            return False
        return self.__import_model(model_name)

    def postprocess_model(self, model_name=''):
        if model_name not in Core.registered_models['post']:
            return False
        return self.__import_model(model_name)

    @staticmethod
    def __import_model(model_name):
        if model_name == '':
            return True
        return importlib.import_module('utils.models.' + model_name).get_class()

    def verify_pipeline(self):
        if False in self._pipeline:
            return 200 + self._pipeline.index(False) + 1
        else:
            return 100

    def run(self):
        pass
