__all__ = ['set_meta', 'set_melody', 'set_output_progression_style', 'set_output_chord_style',
           'set_preprocess_model', 'set_main_model', 'set_postprocess_model', 'generate',
           'Key', 'Mode', 'Meter', 'set_phrase', 'ChordStyle', 'ProgressionStyle', 'generate_save']

from .core import Core
from .settings import *
from .utils.excp import handle_exception
from .utils.utils import Logging

_core = Core.get_core()


def set_melody(midi_path: str):
    _core.midi_path = midi_path


def set_phrase(phrase: list):
    _core.phrase = phrase


def set_meta(tonic: str = None, mode: str = None, meter: str = None, tempo=None):
    if tonic is not None:
        _core.meta['tonic'] = tonic
    if mode is not None:
        _core.meta['mode'] = mode
    if meter is not None:
        _core.meta['meter'] = meter
    if tempo is not None:
        _core.meta['tempo'] = tempo


def set_output_progression_style(style: str):
    _core.set_output_progression_style(style)


def set_output_chord_style(style: str):
    _core.set_output_chord_style(style)


def set_preprocess_model(name: str):
    _core.set_pipeline(pre=name)
    Logging.info('Preprocess model set as', name)


def set_main_model(name: str):
    _core.set_pipeline(main=name)
    Logging.info('Main model set as', name)


def set_postprocess_model(name: str):
    _core.set_pipeline(post=name)
    Logging.info('Postprocess model set as', name)


def generate():
    verified = _core.verify()
    if verified != 100:
        handle_exception(verified)
    return _core.run()


def generate_save(output_name, with_log=False):
    try:
        os.makedirs(output_name)
    except:
        pass
    if not with_log:
        gen = generate()[0]
        gen.write(output_name + '/generated.mid')
        return
    else:
        gen, gen_log = generate()
        gen.write(output_name + '/generated.mid')
        file = open(output_name + '/generated.log', 'w')
        for i in range(len(gen_log)):
            file.write('Chord Progression {i}\n'.format(i=i))
            file.write('Score: {s}\n'.format(s=gen_log[i]['score']))
            file.write('Chord Style: {s}\n'.format(s=gen_log[i]['chord_style']))
            file.write('Progression Style: {s}\n'.format(s=gen_log[i]['progression_style']))
            file.write('Cycle: {s}\n'.format(s=gen_log[i]['cycle']))
            file.write('Pattern: {s}\n'.format(s=gen_log[i]['pattern']))
            file.write('Position: {s}\n'.format(s=gen_log[i]['position']))
            file.write('Progression: {s}\n\n'.format(s=gen_log[i]['progression']))
        file.close()
        return


class Key:
    C = 'C'
    CSharp, DFlat = 'C#', 'Db'
    D = 'D'
    DSharp, EFlat = 'D#', 'Eb'
    E = 'E'
    F = 'F'
    FSharp, GFlat = 'F#', 'Gb'
    G = 'G'
    GSharp, AFlat = 'G#', 'Ab'
    A = 'A'
    ASharp, BFlat = 'A#', 'Bb'
    B = 'B'


class Mode:
    MAJOR = 'maj'
    MINOR = 'min'


class Meter:
    FOUR_FOUR = '4/4'
    THREE_FOUR = '3/4'


class ChordStyle:
    CLASSY = 'classy'
    EMOTIONAL = 'emotional'
    STANDARD = 'standard'
    SECOND_INVERSION = 'second-inversion'
    ROOT_NOTE = 'root-note'
    CLUSTER = 'cluster'
    POWER_CHORD = 'power-chord'
    SUS2 = 'sus2'
    SEVENTH = 'seventh'
    POWER_OCTAVE = 'power-octave'
    SUS4 = 'sus4'
    FIRST_INVERSION = 'first-inversion'
    FULL_OCTAVE = 'full-octave'


class ProgressionStyle:
    EMOTIONAL = 'emotional'
    POP = 'pop'
    DARK = 'dark'
    EDM = 'edm'
    RANDB = 'r&b'
