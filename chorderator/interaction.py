__all__ = ['set_meta', 'set_melody', 'set_output_progression_style', 'set_output_chord_style', 'set_output_style',
           'set_preprocess_model', 'set_main_model', 'set_postprocess_model', 'generate',
           'Key', 'Mode', 'Meter', 'Style', 'set_phrase', 'ChordStyle', 'ProgressionStyle', 'generate_save',
           'get_chorderator']

import json

from .core import Core
from .settings import *
from .utils.excp import handle_exception
from .utils.utils import Logging, listen

_core = Core.get_core()


def get_chorderator():
    return Core.get_core()


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


# abandoned
def set_output_progression_style(style: str):
    _core.set_output_progression_style(style)


# abandoned
def set_output_chord_style(style: str):
    _core.set_output_chord_style(style)


def set_output_style(style):
    _core.set_output_style(style)


def set_preprocess_model(name: str):
    _core.set_pipeline(pre=name)
    Logging.info('Preprocess model set as', name)


def set_main_model(name: str):
    _core.set_pipeline(main=name)
    Logging.info('Main model set as', name)


def set_postprocess_model(name: str):
    _core.set_pipeline(post=name)
    Logging.info('Postprocess model set as', name)


def generate(cut_in=False, with_log=False, **kwargs):
    verified = _core.verify()
    if verified != 100:
        handle_exception(verified)
    gen = _core.run(cut_in, **kwargs)
    return gen if with_log else gen[0]


def generate_save(output_name, with_log=False, formats=None, cut_in=False, **kwargs):
    if formats is None:
        formats = ['mid']

    def write_log(gen_log):
        file = open(output_name + '/' + output_name + '.json', 'w')
        json.dump(gen_log, file)
        file.close()

    try:
        os.makedirs(output_name)
    except:
        pass
    if not with_log:
        gen = generate(cut_in, **kwargs)
    else:
        gen, gen_log = generate(cut_in, with_log=with_log, **kwargs)
        write_log(gen_log)
    if 'mid' in formats:
        gen.write(output_name + '/' + output_name + '.mid')
    if 'wav' in formats:
        listen(gen, path=output_name, out='/' + output_name + '.wav')


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


class Style:
    POP_STANDARD = 'pop_standard'
    POP_COMPLEX = 'pop_complex'
    DARK = 'dark'
    RANDB = 'r&b'
