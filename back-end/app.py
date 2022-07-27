import io
import json
import os
import shutil
import sys
import threading
import logging
import time

import pretty_midi
from flask import Flask, request, send_from_directory, send_file, make_response, jsonify

sys.path.append('..')
import chorderator as cdt
from Sessions import Sessions
from construct_midi_seg import construct_midi_seg

app = Flask(__name__, static_url_path='')
app.secret_key = 'AccoMontage2-GUI'
saved_data = cdt.load_data()
APP_ROUTE = '/api'
sessions = Sessions()
logging.basicConfig(level=logging.DEBUG)


def resp(msg=None, session_id=None, more=()):
    body = {'status': 'ok' if not msg else msg}
    for item in more:
        body[item[0]] = item[1]
    r = make_response(jsonify(body))
    if session_id:
        r.set_cookie('session', session_id, max_age=3600)
    return r


def send_file_from_session(file, name=None):
    return send_file(
        io.BytesIO(file),
        as_attachment=True,
        attachment_filename=name)


def begin_generate_thread(core, session_id):
    core.generate_save(session_id, log=True)


@app.route(APP_ROUTE + '/upload_melody', methods=['POST'])
def upload_melody():
    if sessions.get_session(request) is None:
        session, session_id = sessions.create_session()
        logging.debug('create new session {}'.format(session_id))
    else:
        session, session_id = sessions.get_session(request)
        logging.debug('request is in session {}'.format(session_id))
    session.melody = request.files['midi'].read()
    return resp(session_id=session_id)


@app.route(APP_ROUTE + '/generate', methods=['POST'])
def generate():
    session, session_id = sessions.get_session(request)
    if not session:
        return resp(msg='session expired')
    logging.debug('request is in session {}'.format(session_id))
    params = json.loads(request.data)
    session.load_params(params)

    session.core = cdt.get_chorderator()
    session.core.set_cache(**saved_data)
    os.makedirs(session_id, exist_ok=True)
    with open(f'{session_id}/melody.mid', 'wb') as f:
        f.write(session.melody)
    session.core.set_melody(f'{session_id}/melody.mid')
    session.core.set_output_style(session.chord_style)
    session.core.set_texture_prefilter(session.texture_style)
    session.core.set_meta(tonic=session.tonic, meter=session.meter, mode=session.mode)
    session.core.set_segmentation(session.segmentation)
    threading.Thread(target=begin_generate_thread, args=(session.core, session_id)).start()
    return resp(session_id=session_id)


@app.route(APP_ROUTE + '/stage_query', methods=['GET'])
def answer_stage():
    session, session_id = sessions.get_session(request)
    if not session:
        return resp(msg='session expired')
    logging.debug('request is in session {}'.format(session_id))
    return resp(session_id=session_id, more=[['stage', str(session.core.get_state())]])


@app.route(APP_ROUTE + '/generated_query', methods=['GET'])
def answer_gen():
    session, session_id = sessions.get_session(request)
    if not session:
        return resp(msg='session expired')
    logging.debug('request is in session {}'.format(session_id))
    for file in os.listdir(session_id):
        if file == 'chord_gen_log.json':
            session.generate_log = json.load(open(session_id + '/chord_gen_log.json', 'r'))
        elif file == 'textured_chord_gen.mid':
            with open(session_id + '/textured_chord_gen.mid', 'rb') as f:
                session.generate_midi = f.read()
        elif file == 'textured_chord_gen.wav':
            with open(session_id + '/textured_chord_gen.wav', 'rb') as f:
                session.generate_wav = f.read()
    session.generate_midi_seg = construct_midi_seg(session, session_id)
    chord_midi_name = session_id + '_' + str(time.time()) + '_chord_gen.mid'
    acc_midi_name = session_id + '_' + str(time.time()) + '_textured_chord_gen.mid'
    pretty_midi.PrettyMIDI(session_id + '/chord_gen.mid').write('static/midi/' + chord_midi_name)
    # shutil.copy(session_id + '/chord_gen.mid', 'static/midi/' + chord_midi_name)
    pretty_midi.PrettyMIDI(session_id + '/textured_chord_gen.mid').write('static/midi/' + acc_midi_name)
    # shutil.copy(session_id + '/textured_chord_gen.mid', 'static/midi/' + acc_midi_name)
    shutil.rmtree(session_id)
    new_log = []
    for i in range(len(session.generate_log)):
        new_log.append(session.generate_log[i])
        new_log[i]['midi_name'] = session.generate_midi_seg[i]
    return resp(session_id=session_id,
                more=[['log', new_log], ['chord_midi_name', chord_midi_name], ['acc_midi_name', acc_midi_name]])


@app.route(APP_ROUTE + '/wav/<ran>', methods=['GET'])
def wav(ran):
    session, session_id = sessions.get_session(request)
    if not session:
        return resp(msg='session expired')
    logging.debug('request is in session {}'.format(session_id))
    return send_file_from_session(session.generate_wav, 'accomontage2.wav')


@app.route(APP_ROUTE + '/midi/<ran>', methods=['GET'])
def midi(ran):
    session, session_id = sessions.get_session(request)
    if not session:
        return resp(msg='session expired')
    logging.debug('request is in session {}'.format(session_id))
    return send_file_from_session(session.generate_midi, 'accomontage2.mid')


@app.route(APP_ROUTE + '/midi-seg/<idx>', methods=['GET'])
def midi_seg(idx):
    session, session_id = sessions.get_session(request)
    if not session:
        return resp(msg='session expired')
    logging.debug('request is in session {}'.format(session_id))
    return send_file_from_session(session.generate_midi_seg[idx], f'accomontage2-{idx}.mid')


@app.errorhandler(404)
def index(error):
    return make_response(send_from_directory('static', 'index.html'))


if __name__ == '__main__':
    app.run()
