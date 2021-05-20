### Demo

```python
from settings import *
from chords.ChordProgression import read_progressions, print_progression_list
from utils.constants import *
from utils.utils import pick_progressions, np, listen

POP909 = 'progressions_from_pop909.txt'
DEFAULT = 'progressions.txt'

# 1. read
# read progressions in the progression txt file
# a Python List is returned, each element is a ChordProgression object
prog_list = read_progressions(progression_file=DEFAULT)

# 2. print
# print progression list
print('Progression list is like this: \n', prog_list, '\n')
print('Print progression list in a pretty way by calling the "print_progression_list" function:\n')
print_progression_list(prog_list, limit=5)

# 3. pick
# pick out the progressions you want by calling 'pick_progressions'
# pass in the rules and progression list
# the rules now includes 'SHORT', 'DENSE', 'LONG', 'SPARSE', might append more
dense_prog_list = pick_progressions(DENSE, progression_list=prog_list)
print('Dense progressions were picked out by calling the "pick_progressions" function, '
      'showing the first 2:\n')
print_progression_list(dense_prog_list, limit=2)

dense_short_prog_list = pick_progressions(DENSE, SHORT, progression_list=prog_list)
print('Dense and short progressions were picked out by calling the "pick_progressions" function,'
      ' showing the first 2:\n')
print_progression_list(dense_short_prog_list, limit=2)

# 4. operate
# the following shows how to operate a single progression
test_progression = dense_short_prog_list[1] # choose a progression randomly
print('Print a single progression:\n\n', test_progression)

print('List representation of this progression:\n', test_progression.progression)
print('In Numpy:\n',np.array(test_progression.progression))
print('Meta Info:\n', test_progression.meta)

# save as MIDI
# my_midi = test_progression.to_midi(tonic="C", mode="M", tempo=120, instrument=PIANO)
# my_midi.write('my_midi.mid')

# listen a progression
# now that the sound source is removed, this function does not work!
# listen(test_progression.to_midi())
```


