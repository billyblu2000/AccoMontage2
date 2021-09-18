from pretty_midi import PrettyMIDI

from utils.utils import MIDILoader


class PreProcessor:

    def __init__(self, midi_path, meta):
        self.midi_path = midi_path
        self.meta = meta

    def get(self):
        # TODO temp for test!
        pop909_loader = MIDILoader(files='POP909')
        pop909_loader.config(output_form='number')
        melo_source_name = MIDILoader.auto_find_pop909_source_name(start_with='114')[:5]
        test_melo = [pop909_loader.get(name=i) for i in melo_source_name]
        self.meta['pos'] = [name[6] for name in melo_source_name]

        return test_melo, self.meta
