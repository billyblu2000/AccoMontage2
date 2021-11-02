# CHORDERATOR

> A useful tool to generate chord progressions according to melody MIDIs


### Demo

```python
import chorderator as cdt

# set your input MIDI path
cdt.set_melody('MIDI demos/inputs/4.mid')

# set phrase for your melody. If your melody have only one phrase, simply
# call set_phrase([1]) or remove the statement
cdt.set_phrase([1])

# set melody meta. tonic, mode, and meter must be specified
cdt.set_meta(tonic=cdt.Key.C, mode=cdt.Mode.MAJOR, meter=cdt.Meter.FOUR_FOUR)

# choose an output chord style; default is STANDARD
cdt.set_output_chord_style(cdt.ChordStyle.STANDARD)

# choose an output progression style; default is POP
cdt.set_output_progression_style(cdt.ProgressionStyle.POP)

# generate the progression. please specify the output MIDI path
cdt.generate('MIDI demos/outputs/generated.mid')

```


