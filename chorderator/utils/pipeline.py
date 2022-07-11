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
            self.chord_gen_output, self.final_output_log = self.__postprocess(cut_in_arg, **kwargs)
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
            chord_gen_midi = pretty_midi.PrettyMIDI(cut_in_arg)
            self.chord_gen_output = chord_gen_midi.instruments[1]
            self.melo = chord_gen_midi.instruments[0]
            self.meta['tempo'] = chord_gen_midi.get_tempo_changes()[1][0]
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
            self.final_output = self.__add_textures(self.chord_gen_output, self.final_output_log, **kwargs)
            self.__shift_note(self.final_output.instruments[1], kwargs['note_shift'], self.meta['tempo'])
        else:
            self.final_output = self.__add_textures(self.chord_gen_output, do_add_textures=False, **kwargs)
        self.state = 5
        Logging.warning('All process finished!')

    def __preprocess(self, midi_path, **kwargs):
        processor = self.pipeline[0](midi_path, kwargs['phrase'], kwargs['meta'], kwargs['note_shift'])
        return processor.get()

    def __main_model(self, splited_melo, meta):
        templates = read_progressions('rep')
        meta['metre'] = meta['meter']
        print([len(i) for i in splited_melo])
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
                                     kwargs['output_style'],
                                     kwargs['note_shift'])
        return processor.get()

    def __add_textures(self, output, log, melo=None, do_add_textures=True, **kwargs):
        original_tempo = self.meta['tempo']
        if not melo:
            melo = self.melo
        new_melo = self.__to_tempo(melo, original_tempo, 120)
        new_chord = self.__to_tempo(output, original_tempo, 120)
        midi = combine_ins(new_melo, new_chord, init_tempo=120)
        if do_add_textures:
            processor = self.pipeline[3](midi=midi, log=log, segmentation=kwargs['segmentation'], note_shift=kwargs['note_shift'],
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

    @staticmethod
    def __shift_note(ins, shift, tempo):
        unit_len = 60 / tempo / 4
        for note in ins.notes:
            note.start = note.start + unit_len * shift
            note.end = note.end + unit_len * shift

    def send_out(self):
        if self.final_output:
            return combine_ins(self.melo, self.final_output.instruments[1], init_tempo=self.meta['tempo']), \
                   combine_ins(self.melo, self.chord_gen_output, init_tempo=self.meta['tempo']), \
                   self.final_output_log
        else:
            Logging.critical('Nothing is in pipeline yet!')


if __name__ == '__main__':
    pass
