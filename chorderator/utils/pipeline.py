from chords.ChordProgression import read_progressions
from utils.excp import handle_exception
from utils.utils import Logging, pickle_read, combine_ins


class Pipeline:

    def __init__(self, pipeline):
        self.pipeline = pipeline
        if len(pipeline) != 3:
            Logging.critical('Pipeline length not match!')
        self.final_output = None

    # noinspection PyTupleAssignmentBalance,PyNoneFunctionAssignment
    def send_in(self, midi_path, **kwargs):
        self.melo, splited_melo, meta = self.__preprocess(midi_path, **kwargs)
        progression_list = self.__main_model(splited_melo, meta)
        self.final_output = self.__postprocess(progression_list, **kwargs)

    def __preprocess(self, midi_path, **kwargs):
        try:
            processor = self.pipeline[0](midi_path, kwargs['meta'])
            print(processor)
            return processor.get()
        except:
            handle_exception(500)

    def __main_model(self, splited_melo, meta):
        templates = read_progressions('representative.pcls')
        meta['metre'] = meta['meter']
        print(splited_melo,meta,templates[:100])
        try:
            processor = self.pipeline[1](splited_melo, meta, templates)
            processor.solve()
            return processor.get()
        except Exception as e:
            handle_exception(600)

    def __postprocess(self, progression_list, meta, **kwargs):
        templates = read_progressions('dict.pcls')
        lib = pickle_read('lib')
        try:
            processor = self.pipeline[2](progression_list, templates, lib, meta, **kwargs)
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
