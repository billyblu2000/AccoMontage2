__all__ = ['set_meta', 'set_melody', 'set_output_progression_style', 'set_output_chord_style',
           'set_preprocess_model', 'set_main_model', 'set_postprocess_model', 'generate',
           ]

from core import Core

_core = Core.get_core()


def set_melody():
    pass


def set_meta():
    pass


def set_output_progression_style():
    pass


def set_output_chord_style():
    pass


def set_preprocess_model(name):
    _core.set_pipeline(pre=name)


def set_main_model(name):
    _core.set_pipeline(main=name)


def set_postprocess_model(name):
    _core.set_pipeline(post=name)


def generate():
    verified = _core.verify_pipeline()
    if verified == 100:
        _core.run()
    else:
        _handel_exception(verified)


def _handel_exception(code):
    if code // 100 == 2:
        raise ValueError('pipeline cannot be recognized:', code)
