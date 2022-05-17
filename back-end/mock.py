import json

from flask import Flask

app = Flask(__name__, static_url_path='')


@app.route('/api/chorderator_back_end/stage_query', methods=['GET'])
def a():
    return '6'

@app.route('/api/chorderator_back_end/generated_query', methods=["POST", "GET"])
def d():
    test_json = [{"score": 1, "chord_style": "standard", "progression_style": "edm", "duplicate_id": 169, "style": "pop_standard", "cycle": [1.0, 32], "pattern": "unknown", "position": None, "rhythm": "unknown", "progression": [["G 0"], ["D 0"], ["B 1"], ["A 0"], ["G 0"], ["D 0"], ["B 1"], ["A 0"]], "other_possible_styles": ["pop_standard", "pop_complex"]}, {"score": 1, "chord_style": "standard", "progression_style": "pop", "duplicate_id": 151, "style": "pop_standard", "cycle": [1.0, 32], "pattern": "unknown", "position": None, "rhythm": "unknown", "progression": [["F 0"], ["D 1"], ["Bb0"], ["C 0"], ["F 0"], ["D 1"], ["Bb0"], ["C 0"]], "other_possible_styles": ["pop_standard", "pop_complex"]}, {"score": 1, "chord_style": "standard", "progression_style": "pop", "duplicate_id": 172, "style": "pop_standard", "cycle": [1.0, 32], "pattern": "unknown", "position": None, "rhythm": "unknown", "progression": [["Db0"], ["Gb0"], ["Bb1"], ["Ab0"], ["Db0"], ["Gb0"], ["Bb1"], ["Ab0"]], "other_possible_styles": ["pop_standard", "pop_complex"]}, {"score": 1, "chord_style": "standard", "progression_style": "pop", "duplicate_id": 172, "style": "pop_standard", "cycle": [1.0, 32], "pattern": "unknown", "position": None, "rhythm": "unknown", "progression": [["E 0"], ["A 0"], ["C#1"], ["B 0"], ["E 0"], ["A 0"], ["C#1"], ["B 0"]], "other_possible_styles": ["pop_standard", "pop_complex"]}, {"score": 1, "chord_style": "standard", "progression_style": "pop", "duplicate_id": 151, "style": "pop_standard", "cycle": [1.0, 32], "pattern": "unknown", "position": None, "rhythm": "unknown", "progression": [["Bb0"], ["G 1"], ["Eb0"], ["F 0"], ["Bb0"], ["G 1"], ["Eb0"], ["F 0"]], "other_possible_styles": ["pop_standard", "pop_complex"]}, {"score": 1, "chord_style": "standard", "progression_style": "pop", "duplicate_id": 172, "style": "pop_standard", "cycle": [1.0, 32], "pattern": "unknown", "position": None, "rhythm": "unknown", "progression": [["C 0"], ["F 0"], ["A 1"], ["G 0"], ["C 0"], ["F 0"], ["A 1"], ["G 0"]], "other_possible_styles": ["pop_standard", "pop_complex"]}, {"score": 1, "chord_style": "standard", "progression_style": "pop", "duplicate_id": 172, "style": "pop_standard", "cycle": [1.0, 32], "pattern": "unknown", "position": None, "rhythm": "unknown", "progression": [["A 0"], ["D 0"], ["F#1"], ["E 0"], ["A 0"], ["D 0"], ["F#1"], ["E 0"]], "other_possible_styles": ["pop_standard", "pop_complex"]}]
    return json.dumps(test_json)


if __name__ == '__main__':
    app.run()
