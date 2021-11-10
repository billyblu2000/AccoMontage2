import math
import pickle
from . import compute_transition_score
from .concatenate import Concatenate


def compute_all_from_dict(original):
    print('computing representatives.pcls')
    representatives = [lst[0] for lst in original.values()]
    file = open('new_representatives.pcls', 'wb')
    pickle.dump(representatives, file)
    file.close()

    print('computing transition_score.mdch')
    for i in representatives:
        for j in representatives:
            compute_transition_score.transition_score(i, j, representatives)
    trans = compute_transition_score.transition_dict
    max_score = max(trans.values())
    for item in trans.items():
        trans[item[0]] = math.log(item[1]) / math.log(max_score) if item[1] != 0 else 0
    file = open('new_transition_score.mdch', 'wb')
    pickle.dump(trans, file)
    file.close()

    print('computing new_major_score.mdch')
    major_templates = []
    minor_templates = []
    for template in representatives:
        if template.meta['mode'] == 'M' or template.meta['mode'] == 'maj':
            major_templates.append(template)
        else:
            minor_templates.append(template)
    print(len(major_templates), len(minor_templates))

    my_concatenater = Concatenate(templates=major_templates,
                                  transition_score=pickle.load(open('new_transition_score.mdch', 'rb')))
    all = my_concatenater.concatenate()
    file = open('new_major_score.mdch', 'wb')
    pickle.dump(all, file)
    file.close()

    print('computing new_minor_score.mdch')
    my_concatenater = Concatenate(templates=minor_templates,
                                  transition_score=pickle.load(open('new_transition_score.mdch', 'rb')))
    all = my_concatenater.concatenate()
    file = open('new_minor_score.mdch', 'wb')
    pickle.dump(all, file)
    file.close()