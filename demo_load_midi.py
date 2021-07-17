# PLEASE PUT MIDI FILES IN '/static/midi/'
from utils.utils import MIDILoader

if __name__ == '__main__':

    # ##########
    # load midis
    # ##########

    my_midis = MIDILoader()  # load every midi files in the midi folder
    # alternatives
    # midi = MIDILoader(files = '*') # also load every midi files in the midi folder
    # midi = MIDILoader(files = '1.mid') # load '1.mid' in the midi folder
    # midi = MIDILoader(files = ['1.mid','2.mid']) # load '1.mid' and '2.mid' in the midi folder

    # #####################################
    # the following code can get transformed midi data
    # data form: [pitch, pitch, pitch, ...]
    # each element is a sixteenth note
    # pitch = 0 means rest
    # #####################################

    all_midis = my_midis.all()

    data_of_a_specific_midi = my_midis.get(name='6.mid')
    # alternatives
    # data_of_a_specific_midi = my_midis.get(name=['3.mid','4.mid']) # pick 3.mid and 4.mid

    pick_midis_randomly = my_midis.sample()
    # alternatives
    # pick_midis_randomly = my_midis.sample(num=3) # pick 3 midis

    print("All MIDIs: ", all_midis)
    print("Data of '3.mid': ", data_of_a_specific_midi)
    print("Pick a MIDI randomly: ", pick_midis_randomly)

    # switch output form to 1234567
    my_midis.config(output_form='number')

    number_data_of_a_specific_midi = my_midis.get(name='6.mid')
    print("Make the melody read-friendly ('6.mid' for example)': ", number_data_of_a_specific_midi)

    # switch output form to midi object
    my_midis.config(output_form='midi')

    midi_object_of_a_specific_midi = my_midis.get(name='6.mid')
    print("Return a MIDI object': ", midi_object_of_a_specific_midi)

    print('\n\nDemo of MIDILoader (load from pop909)\n-------------------------------')

    pop909_loader = MIDILoader(files='POP909')
    pop909_loader.config(output_form='number')
    print("Show melo with name 00101_i4: ", pop909_loader.get(name='00101_i4'))
    print("Pick out melo with special constraints: ", pop909_loader.get(metre='4/4', length=64, mode='min'))
