from ..chords.ChordProgression import read_progressions
from .excp import handle_exception
from .utils import Logging, pickle_read, combine_ins


class Pipeline:

    def __init__(self, pipeline):
        self.meta = None
        self.melo = None
        self.final_output = None
        self.pipeline = pipeline
        if len(pipeline) != 3:
            Logging.critical('Pipeline length not match!')

    def send_in(self, midi_path, **kwargs):
        Logging.warning('Pre-processing...')
        self.melo, splited_melo, self.meta = self.__preprocess(midi_path, **kwargs)
        Logging.warning('Pre-process done!')
        Logging.warning('Solving...')
        progression_list = self.__main_model(splited_melo, self.meta)
        Logging.warning('Solved!')
        Logging.warning('Post-processing...')
        self.final_output = self.__postprocess(progression_list, **kwargs)
        Logging.warning('Post-process done!')

    def __preprocess(self, midi_path, **kwargs):
        try:
            processor = self.pipeline[0](midi_path, kwargs['phrase'], kwargs['meta'])
            return processor.get()
        except:
            handle_exception(500)

    def __main_model(self, splited_melo, meta):
        templates = read_progressions('representative.pcls')
        meta['metre'] = meta['meter']
        try:
            processor = self.pipeline[1](splited_melo, meta, templates)
            processor.solve()
            return processor.get()
        except Exception as e:
            handle_exception(600)

    def __postprocess(self, progression_list, **kwargs):
        templates = read_progressions('dict.pcls')
        lib = pickle_read('lib')
        try:
            processor = self.pipeline[2](progression_list,
                                         templates,
                                         lib,
                                         self.meta,
                                         kwargs['output_chord_style'],
                                         kwargs['output_progression_style'])
            return processor.get()
        except Exception as e:
            handle_exception(700)

    def send_out(self, output_name):
        if self.final_output:
            return combine_ins(self.melo,self.final_output).write(output_name)
        else:
            Logging.critical('Nothing is in pipeline yet!')


if __name__ == '__main__':
    pass
