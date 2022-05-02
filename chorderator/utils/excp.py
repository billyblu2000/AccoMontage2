from .utils import Logging

website = ' For more information, please visit https://...com.'


def handle_exception(code):
    if int(str(code)[0]) == 2:
        if code == 201:
            msg = 'Pre-process model cannot be recognized!'
        elif code == 202:
            msg = 'Main model cannot be recognized!'
        else:
            msg = 'Post-process model cannot be recognized!'
        raise ValueError('[Error {e}] '.format(e=code) + msg + website)
    elif int(str(code)[0]) == 3:
        if int(str(code)[1]) == 0:
            msg = 'MIDI file have to be assigned! You may want to call chorderator.set_melody(PATH: str).'
        elif int(str(code)[1]) == 1:
            if code == 311:
                msg = 'Phrase or segmentation have to be assigned! You may want to call chorderator.set_phrase(PHRASE: ' \
                      'list) or chorderator.set_segmentation(str)'
            elif code == 312:
                msg = 'Phrase length not accepted. Up to the current version, only the following length is supported: ' \
                      '4, 8, 12, 16, 24, 32.'
            else:
                msg = ''
        elif int(str(code)[1]) == 2:
            if code == 321:
                msg = 'Melody meta have to be assigned! You may want to call chorderator.set_meta(tonic: ' \
                      'chorderator.Key, mode: chorderator.Mode, meter: chorderator.Meter).'
            elif code == 322:
                msg = 'Melody meta not completed. Please make sure you have called chorderator.set_meta(tonic: ' \
                      'chorderator.Key, mode: chorderator.Mode, meter: chorderator.Meter). All parameters are needed.'
            elif code == 323:
                msg = 'Melody tonic can not be recognized.'
            elif code == 324:
                msg = 'Melody mode can not be recognized.'
            elif code == 325:
                msg = 'Melody meter can not be recognized.'
            else:
                msg = ''
        elif int(str(code)[1]) == 3:
            if code == 331:
                msg = 'Chord style cannot be recognized.'
            else:
                msg = ''
        elif int(str(code)[1]) == 4:
            if code == 341:
                msg = 'Progression style cannot be recognized.'
            else:
                msg = ''
        elif int(str(code)[1]) == 5:
            if code == 341:
                msg = 'Output style cannot be recognized.'
            else:
                msg = ''
        else:
            msg = ''
        raise ValueError('[Error {e}] '.format(e=code) + msg + website)
    elif int(str(code)[0]) == 5:
        if int(str(code)[1]) == 0:
            if code == 500:
                msg = 'Cut in from post-process should pass in a progression list'
            else:
                msg = ''
        else:
            msg = ''
        raise ValueError('[Error {e}] '.format(e=code) + msg + website)