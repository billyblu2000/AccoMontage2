__all__ = ['set_meta', 'set_melody', 'set_output_progression_style', 'set_output_chord_style',
           'set_preprocess_model', 'set_main_model', 'set_postprocess_model', 'generate',
           'Const']

from core import Core
from utils.utils import Logging

_core = Core.get_core()


def set_melody(midi_path):
    _core.midi_path = midi_path


def set_meta(tonic=None, mode=None, meter=None):
    if tonic is not None:
        _core.meta['tonic'] = tonic
    if mode is not None:
        _core.meta['mode'] = mode
    if meter is not None:
        _core.meta['meter'] = meter


def set_output_progression_style():
    pass


def set_output_chord_style():
    pass


def set_preprocess_model(name):
    _core.set_pipeline(pre=name)
    Logging.info('Preprocess model set as', name)


def set_main_model(name):
    _core.set_pipeline(main=name)
    Logging.info('Main model set as', name)


def set_postprocess_model(name):
    _core.set_pipeline(post=name)
    Logging.info('Postprocess model set as', name)


def generate():
    verified = _core.verify_pipeline()
    if verified == 100:
        _core.run()
    else:
        _handel_exception(verified)


def _handel_exception(code):
    if code // 100 == 2:
        if code == 201:
            msg = '[Error {e}] Pre-process model cannot be recognized!'
        elif code == 202:
            msg = '[Error {e}] Main model cannot be recognized!'
        else:
            msg = '[Error {e}] Post-process model cannot be recognized!'
        raise ValueError(msg.format(e=code))


class Const:
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
