from pretty_midi import PrettyMIDI

from utils.utils import MIDILoader


class PreProcessor:

    def __init__(self, midi_path, meta):
        self.midi = PrettyMIDI(midi_path) if midi_path else None
        self.meta = meta

    def get(self):

        if not self.midi:
            pop909_loader = MIDILoader(files='POP909')
            pop909_loader.config(output_form='number')
            melo_source_name = MIDILoader.auto_find_pop909_source_name(start_with='114')[:5]
            test_melo = [pop909_loader.get(name=i) for i in melo_source_name]
            self.meta['pos'] = [name[6] for name in melo_source_name]

        else:
            # TODO
            test_melo = []
            self.meta['pos'] = []

        return test_melo, self.meta
