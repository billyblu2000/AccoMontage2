# CHORDERATOR

> A useful tool to generate chord progressions according to melody MIDIs


### Demo

```python
from utils.models.accomontage.AccoMontage import accomontage
import chorderator as cdt

name = 'D#_78_4-4-4-4.mid'
cdt.set_melody('MIDI demos/inputs/' + name)
cdt.set_phrase([1, 5, 9, 13])
cdt.set_meta(tonic=cdt.Key.DSharp, mode=cdt.Mode.MAJOR, meter=cdt.Meter.FOUR_FOUR)

cdt.set_output_style(cdt.Style.POP_STANDARD)
cdt.generate_save('generated_' + name, with_log=True)

accomontage(song_name='generated_' + name + '.mid',
            song_root='generated_' + name,
            segmentation='A4A4A4A4\n',
            output_name='final.mid')
```

Folder ``accomotage`` referencing AccoMontage by Jingwei Zhao and Gus Xia, available at https://github.com/zhaojw1998/AccoMontage
