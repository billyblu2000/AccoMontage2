import pretty_midi

from ..chords.ChordProgression import read_progressions
from .excp import handle_exception
from .utils import Logging, pickle_read, combine_ins


class Pipeline:

    def __init__(self, pipeline):
        self.meta = None
        self.melo = None
        self.final_output = None
        self.final_output_log = None
        self.chord_gen_output = None
        self.state = 0
        self.pipeline = pipeline
        if len(pipeline) < 3:
            Logging.critical('Pipeline length not match!')

    def send_in(self, midi_path, cut_in=False, cut_in_arg=None, with_texture=True, **kwargs):
        if cut_in == 'from_post':
            self.state = 1
            Logging.warning('Pre-processing...')
            self.melo, splited_melo, self.meta = self.__preprocess(midi_path, **kwargs)
            Logging.warning('Pre-process done!')
            if not cut_in_arg:
                handle_exception(500)
            self.state = 3
            Logging.warning('Post-processing...')
            self.chord_gen_output, self.final_output_log = self.__postprocess(kwargs['cut_in_arg'], **kwargs)
            Logging.warning('Post-process done!')
            self.state = 4
        elif cut_in == 'from_texture':
            self.state = 1
            Logging.warning('Pre-processing...')
            self.melo, splited_melo, self.meta = self.__preprocess(midi_path, **kwargs)
            Logging.warning('Pre-process done!')
            self.state = 4
            if not cut_in_arg:
                handle_exception(500)
            self.chord_gen_output = pretty_midi.PrettyMIDI(kwargs['cut_in_arg']).instruments[1]
        else:
            self.state = 1
            Logging.warning('Pre-processing...')
            self.melo, splited_melo, self.meta = self.__preprocess(midi_path, **kwargs)
            Logging.warning('Pre-process done!')
            self.state = 2
            Logging.warning('Solving...')
            progression_list = self.__main_model(splited_melo, self.meta)
            Logging.warning('Solved!')
            self.state = 3
            Logging.warning('Post-processing...')
            self.chord_gen_output, self.final_output_log = self.__postprocess(progression_list, **kwargs)
            Logging.warning('Post-process done!')
            self.state = 4
        Logging.warning('Generating textures...')
        if with_texture:
            self.final_output = self.__add_textures(self.chord_gen_output, **kwargs)
        else:
            self.final_output = self.__add_textures(self.chord_gen_output, do_add_textures=False, **kwargs)
        self.state = 5
        Logging.warning('All process finished!')

    def __preprocess(self, midi_path, **kwargs):
        processor = self.pipeline[0](midi_path, kwargs['phrase'], kwargs['meta'])
        return processor.get()

    def __main_model(self, splited_melo, meta):
        templates = read_progressions('rep')
        meta['metre'] = meta['meter']
        processor = self.pipeline[1](splited_melo, meta, templates)
        processor.solve()
        return processor.get()

    def __postprocess(self, progression_list, **kwargs):
        if 'templates' not in kwargs:
            templates = read_progressions('dict')
        else:
            templates = kwargs['templates']
        if 'lib' not in kwargs:
            lib = pickle_read('lib')
        else:
            lib = kwargs['lib']
        processor = self.pipeline[2](progression_list,
                                     templates,
                                     lib,
                                     self.meta,
                                     kwargs['output_chord_style'],
                                     kwargs['output_progression_style'],
                                     kwargs['output_style'])
        return processor.get()

    def __add_textures(self, output, do_add_textures=True, **kwargs):
        original_tempo = self.meta['tempo']
        new_melo = self.__to_tempo(self.melo, original_tempo, 120)
        new_chord = self.__to_tempo(output, original_tempo, 120)
        midi = combine_ins(new_melo, new_chord, init_tempo=120)
        if do_add_textures:
            processor = self.pipeline[3](midi=midi, segmentation=kwargs['segmentation'], note_shift=0,
                                         spotlight=kwargs['texture_spotlight'],
                                         prefilter=kwargs['texture_prefilter'], state_dict=kwargs['state_dict'],
                                         phrase_data=kwargs['phrase_data'], edge_weights=kwargs['edge_weights'],
                                         song_index=kwargs['song_index'], original_tempo=original_tempo)
            processor.solve()
            return processor.get()
        else:
            return midi

    @staticmethod
    def __to_tempo(ins, original, target):
        new_ins = pretty_midi.Instrument(0)
        for note in ins.notes:
            new_ins.notes.append(pretty_midi.Note(
                start=note.start*original/target,
                end=note.end*original/target,
                pitch=note.pitch,
                velocity=note.velocity
            ))
        return new_ins

    def send_out(self):
        if self.final_output:
            return combine_ins(self.melo, self.final_output.instruments[1], init_tempo=self.meta['tempo']), \
                   combine_ins(self.melo, self.chord_gen_output, init_tempo=self.meta['tempo']), \
                   self.final_output_log
        else:
            Logging.critical('Nothing is in pipeline yet!')


if __name__ == '__main__':
    pass
