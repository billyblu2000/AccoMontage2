from pretty_midi import PrettyMIDI, Instrument, Note

from utils.excp import handle_exception
from utils.utils import MIDILoader


class PreProcessor:
    accepted_phrase_length = [4, 8, 16, 12, 24, 32]

    def __init__(self, midi_path='', phrase=None, meta=None):
        try:
            self.midi = PrettyMIDI(midi_path)
            self.melo = self.midi.instruments[0]
        except:
            self.midi = midi_path
            self.melo = self.__load_pop909_melo()
        self.meta = meta
        self.phrase = phrase

    def get(self):

        if type(self.midi) is str:
            pop909_loader = MIDILoader(files='POP909')
            pop909_loader.config(output_form='number')
            melo_source_name = MIDILoader.auto_find_pop909_source_name(start_with=self.midi)[:5]
            splited_melo = [pop909_loader.get(name=i) for i in melo_source_name]
            self.meta['pos'] = [name[6] for name in melo_source_name]
        else:
            # TODO
            print(self.midi.get_beats())
            input()
            splited_melo = []
            self.meta['pos'] = []

        for i in splited_melo:
            if len(i) // 16 not in PreProcessor.accepted_phrase_length:
                handle_exception(0)

        return self.melo, splited_melo, self.meta

    def __load_pop909_melo(self):
        pop909_loader = MIDILoader(files='POP909')
        pitch_list = pop909_loader.get_full_midi_ins_from_pop909(index=self.midi, change_key_to='C')
        ins = Instrument(program=0)
        current_pitch = pitch_list[0]
        start = 0
        for i in range(len(pitch_list)):
            if i == len(pitch_list) - 1:
                note = Note(pitch=current_pitch, velocity=80, start=start * 0.125, end=(i + 1) * 0.125)
                ins.notes.append(note)
                break
            if pitch_list[i + 1] != pitch_list[i]:
                if current_pitch is not 0:
                    note = Note(pitch=current_pitch, velocity=80, start=start * 0.125, end=(i + 1) * 0.125)
                    ins.notes.append(note)
                current_pitch = pitch_list[i+1]
                start = i + 1
        return ins


