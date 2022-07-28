# AccoMontage2

<u>Code and files still refining. Will be completed in a few days.</u>

### Introduction

AccoMontage2 is a system capable of doing full-length song harmonization and accompaniment arrangement based on a lead melody. Based on AccoMontage, AccoMontage2 invents a harmonization module to generated chord progression, and provides a GUI to control the generating styles of chords and textures. Our paper *AccoMontage2: A Complete Harmonization and Accompaniment Arrangement System* is accepted by [ISMIR 2022](https://ismir2022.ismir.net/) (to be published). This repository stores the code corresponding to the paper.

### Binary Data Files Download

Will be uploaded in a few days.

### Interfaces and Demo

##### Run with terminal

A demo is provided. If you want to run demo, please check all the requirements in ``requirments.txt`` are satisfied, and run

```
python demo.py
```

This demo takes in the melody midi file `hpps30` and output the result in folder `hpps30_output_results`.

```python
# demo.py

import chorderator as cdt

if __name__ == '__main__':

    demo_name = 'hpps30'
    input_melody_path = 'MIDI demos/inputs/' + demo_name + '/melody.mid'

    cdt.set_melody(input_melody_path)
    cdt.set_meta(tonic=cdt.Key.A)
    cdt.set_segmentation('A8B8A8B8')
    cdt.set_texture_prefilter((0, 2))
    cdt.set_note_shift(16)
    cdt.set_output_style(cdt.Style.POP_STANDARD)
    cdt.generate_save(demo_name + '_output_results')
```

Interfaces are provided as follows:

| Method Name             | Description                                                  | Mandatory before generating                                  | Usage Example                                            |
| ----------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | -------------------------------------------------------- |
| `set_melody`            | The input melody path                                        | True                                                         | `set_melody('input.mid')`                                |
| `set_meta`              | Assign tonic (mandatory), mode (default major), and meter (default 4/4, and currently only 4/4 is supported) to the melody | True                                                         | `set_meta(tonic=cdt.Key.A, mode=cdt.Mode.MAJOR)`         |
| `set_segmentation`      | A string to represent the phrase information of the melody. Should be in form 'phrase_name+phrase_length'*n. For example, `A8A8B8B8`. Phrase length only support 4-bars and 8-bars. | True                                                         | `set_segmentation('A8A8B8B8')`                           |
| `set_texture_prefilter` | A tuple (a, b) controlling the style of the textures. a, b can be integers in [0, 4], each controlling horizontal rhythmic density and vertical voice number. The higher number, the denser rhythms. For more information, please refer to [AccoMontage](https://github.com/zhaojw1998/AccoMontage). | False, texture might be in any style if not assigned         | `set_texture_prefilter((2,2))`                           |
| `set_note_shift`        | If there is a piece of blank at the beginning of the melody that you don't want to start generating, please specify the length of the blank with the number of 16-th note. | False, default 0                                             | `set_note_shift(16)`                                     |
| `set_output_style`      | A string to control the chord progression style. Currently, four styles are available: `'pop_standard'`, `'pop_complex'`, `'r&b'`, `'dark'`. | False, chord progression might be in any style if not assigned | `set_output_style(cdt.Style.POP_STANDARD)`               |
| `generate_save`         | Start generating with the specified parameters. A string must be passed in to specify the output folder. By default, the program will output three files: `chord_gen.mid`: a melody track and a chord progression track; `chord_gen.json`: generate log of the harmonization module; `textured_chord_gen.mid`: a melody track and a accompaniment track. Three more parameters are available for this method. `task`: what to output and from where to generate, for example, `task='textured_chord'` will make the program only output the `textured_chord_gen.mid`; `log`: whether to output the log file; `wav`: whether to generate a .wav file for the generating result. If you want to generate a .wav file, please make sure you have [midi2audio](https://pypi.org/project/midi2audio/) and [FulidSynth](https://www.fluidsynth.org/) installed. | -                                                            | `generate_save('generate_result', log=False, wav=False)` |

More detailed controllability is provided. Please refer to the `Core` Class in `chorderator/core.py`. A core object can be instantiated by calling `cdt.get_chorderator()`.

##### Run with GUI

Please check all the requirements in ``backend/requirments.txt`` are satisfied, and run

```
python back-end/app.py
```

You can interact with the GUI at http://127.0.0.1:5000.

### Reference and Acknowledgement

Thanks to Prof. Gus Xia for his guidance. Thanks to Jingwei Zhao and the AccoMontage system that provides solid foundations for this research. His repository can be found at [AccoMontage](https://github.com/zhaojw1998/AccoMontage). Thanks to all members at NYUSH Music-X-Lab for their generous support.

### Cite Our Work

To be published Dec 2022.