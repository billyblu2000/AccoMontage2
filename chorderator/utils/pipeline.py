import importlib

from chords.ChordProgression import read_progressions
from utils.utils import Logging


class Pipeline:

    def __init__(self, pipeline):
        self.pipeline = pipeline
        if len(pipeline) != 3:
            Logging.critical('Pipeline length not match!')
        self.final_output = None

    # noinspection PyTupleAssignmentBalance,PyNoneFunctionAssignment
    def send_in(self, midi_path, **kwargs):
        splited_melo, meta = self.__preprocess(midi_path, **kwargs)
        progression_list = self.__main_model(splited_melo, meta)
        self.final_output = self.__postprocess(progression_list, **kwargs)

    def __preprocess(self, midi_path, **kwargs):
        processor = self.pipeline[0](midi_path, kwargs['meta'])
        return processor.get()

    def __main_model(self, splited_melo, meta):
        templates = read_progressions('progressions_representative.pcls')
        meta['metre'] = meta['meter']
        processor = self.pipeline[1](splited_melo, meta, templates)
        processor.solve()
        return processor.get()

    def __postprocess(self, progression_list, **kwargs):
        processor = self.pipeline[2](progression_list)
        return processor.get()

    def send_out(self):
        if self.final_output:
            return self.final_output
        else:
            Logging.critical('Nothing is in pipeline yet!')


if __name__ == '__main__':
    pass
