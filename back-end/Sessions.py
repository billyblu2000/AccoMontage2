import os
import shutil
import threading
import time
import uuid

EXPIRE = 3600


class Session:

    def __init__(self, session_id):
        self.last_active = time.time()
        self.session_id = session_id
        self.__core = None
        self.__generate_log = None
        self.__generate_midi = None
        self.__generate_wav = None
        self.__generate_midi_seg = []
        self.__melody = None
        self.__tonic = None
        self.__meter = None
        self.__mode = None
        self.__segmentation = None
        self.__chord_style = None
        self.__texture_style = None

    @staticmethod
    def get_log(log_dict):
        log = []
        count = 0
        for progression in log_dict:
            current = {'id': count,
                       'score': progression['score'],
                       'chordStyle': progression['chord_style'],
                       'progressionStyle': progression['progression_style'],
                       'cycle': progression['cycle'][1],
                       'pattern': progression['pattern'],
                       'position': progression['position'],
                       'progression': progression['progression'],
                       'style': progression['style'],
                       'otherStyles': progression['other_possible_styles'],
                       'rhythm': progression['rhythm'],
                       'duplicate_id': progression['duplicate_id']}
            log.append(current)
        return log

    def load_params(self, params):
        if 'tonic' in params:
            self.tonic = params['tonic']
        if 'mode' in params:
            self.mode = params['mode']
        if 'meter' in params:
            self.meter = params['meter']
        if 'phrases' in params:
            self.segmentation = params['phrases']
        if 'chord_style' in params:
            if 'enable_chord_style' in params:
                if params['enable_chord_style']:
                    self.chord_style = params['chord_style']
                else:
                    self.chord_style = '*'
            else:
                self.chord_style = params['chord_style']
        if 'rhythm_density' in params:
            if 'enable_texture_style' in params:
                if params['enable_texture_style']:
                    self.texture_style = (params['rhythm_density'], params['voice_number'])
                else:
                    self.texture_style = None
            else:
                self.texture_style = (params['rhythm_density'], params['voice_number'])

    @property
    def core(self):
        return self.__core

    @core.setter
    def core(self, new):
        self.__core = new
        self.last_active = time.time()

    @property
    def generate_log(self):
        if self.__generate_log is not None:
            return self.get_log(self.__generate_log)
        else:
            return None

    @generate_log.setter
    def generate_log(self, new):
        self.__generate_log = new
        self.last_active = time.time()

    @property
    def generate_midi(self):
        return self.__generate_midi

    @generate_midi.setter
    def generate_midi(self, new):
        self.__generate_midi = new
        self.last_active = time.time()

    @property
    def generate_wav(self):
        return self.__generate_wav

    @generate_wav.setter
    def generate_wav(self, new):
        self.__generate_wav = new
        self.last_active = time.time()

    @property
    def generate_midi_seg(self):
        return self.__generate_midi_seg

    @generate_midi_seg.setter
    def generate_midi_seg(self, new):
        self.__generate_midi_seg = new
        self.last_active = time.time()

    @property
    def melody(self):
        return self.__melody

    @melody.setter
    def melody(self, new):
        self.__melody = new
        self.last_active = time.time()

    @property
    def tonic(self):
        return self.__tonic

    @tonic.setter
    def tonic(self, new):
        self.__tonic = new
        self.last_active = time.time()

    @property
    def meter(self):
        return self.__meter

    @meter.setter
    def meter(self, new):
        self.__meter = new
        self.last_active = time.time()

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, new):
        self.__mode = new
        self.last_active = time.time()

    @property
    def segmentation(self):
        return self.__segmentation

    @segmentation.setter
    def segmentation(self, new):
        if type(new) == str:
            self.__segmentation = new
        else:
            segmentation = ''
            for phrase in new:
                segmentation = segmentation + str(phrase['phrase_name']) + str(phrase['phrase_length'])
            self.__segmentation = segmentation
        self.last_active = time.time()

    @property
    def chord_style(self):
        return self.__chord_style

    @chord_style.setter
    def chord_style(self, new):
        self.__chord_style = new
        self.last_active = time.time()

    @property
    def texture_style(self):
        return self.__texture_style

    @texture_style.setter
    def texture_style(self, new):
        self.__texture_style = new
        self.last_active = time.time()

    def __str__(self):
        s = '<Session ' \
            f'last_active = {self.last_active} ' \
            f'session_id = {self.session_id} ' \
            f'core = {self.core} ' \
            f'generate_log = {self.generate_log} ' \
            f'generate_midi = {self.generate_midi} ' \
            f'generate_wav = {self.generate_wav} ' \
            f'generate_midi_seg = {self.generate_midi_seg} ' \
            f'melody = {self.melody} ' \
            f'tonic = {self.tonic} ' \
            f'meter = {self.meter} ' \
            f'mode = {self.mode} ' \
            f'segmentation = {self.segmentation} ' \
            f'chord_style = {self.chord_style} ' \
            f'texture_style = {self.texture_style} />'
        return s


class Sessions:

    def __init__(self):
        self.sessions = {}

    def get_session(self, request):
        session = request.cookies.get("session")
        if session is None:
            return None
        else:
            if session not in self.sessions:
                return None
            else:
                return self.sessions[session], session

    def create_session(self):
        session_id = str(uuid.uuid4())
        session = Session(session_id)
        self.sessions[session_id] = session
        threading.Thread(target=self.__clear_inactive).start()
        return session, session_id

    def __clear_inactive(self):
        current_time = time.time()
        for session_id, session in self.sessions.items():
            if current_time - session.last_active >= EXPIRE:
                del self.sessions[session_id]
                for file in os.listdir('..'):
                    if session_id in file:
                        shutil.rmtree(file)
        for file in os.listdir('static/pianoroll/midi'):
            session_time = int(file.split('_')[1])
            if current_time - session_time >= EXPIRE:
                os.remove(file)

