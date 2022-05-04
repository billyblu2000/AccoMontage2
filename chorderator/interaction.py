__all__ = ['set_meta', 'set_melody', 'set_output_progression_style', 'set_output_chord_style', 'set_output_style',
           'set_preprocess_model', 'set_main_model', 'set_postprocess_model', 'generate',
           'Key', 'Mode', 'Meter', 'Style', 'set_phrase', 'ChordStyle', 'ProgressionStyle', 'generate_save',
           'get_chorderator', 'set_texture_model', 'set_texture_prefilter', 'set_texture_spotlight', 'set_segmentation',
           'get_current_config', 'load_data']

from .core import Core
from .utils.utils import Logging

_core = Core.get_core()


def get_chorderator():
    return Core.get_core()


def set_melody(midi_path: str):
    _core.set_melody(midi_path)


def set_phrase(phrase: list):
    _core.set_phrase(phrase)


def set_segmentation(segmentation: str):
    _core.set_segmentation(segmentation)


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


def set_output_style(style: str):
    _core.set_output_style(style)


def set_texture_spotlight(spotlight: list):
    _core.set_texture_spotlight(spotlight)


def set_texture_prefilter(prefilter: tuple):
    _core.set_texture_prefilter(prefilter)


def set_preprocess_model(name: str):
    _core.set_pipeline(pre=name)
    Logging.info('Preprocess model set as', name)


def set_main_model(name: str):
    _core.set_pipeline(main=name)
    Logging.info('Main model set as', name)


def set_postprocess_model(name: str):
    _core.set_pipeline(post=name)
    Logging.info('Postprocess model set as', name)


def set_texture_model(name: str):
    _core.set_texture_model(name=name)
    Logging.info('Texture model set as', name)


def generate(cut_in=False, with_texture=True, log=False, **kwargs):
    return _core.generate(cut_in=cut_in, with_texture=with_texture, log=log, **kwargs)


def generate_save(output_name, task='textured_chord', log=False, wav=False, **kwargs):
    return _core.generate_save(output_name=output_name, task=task, log=log, wav=wav, **kwargs)


def get_current_config():
    return str(_core)


def load_data():
    return _core.load_data()


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
