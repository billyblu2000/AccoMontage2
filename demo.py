import pickle

import numpy
from matplotlib import pyplot

import chorderator as cdt
from chorderator import Const
from chords.ChordProgression import read_progressions
from utils.string import STATIC_DIR

from utils.utils import read_lib, split_huge_progression_dict, PathGenerator

if __name__ == '__main__':
    pass

    # cc = 0
    # new_transition_score = {}
    # for pre_prog in all:
    #     for cur_prog in all:
    #         cc += 1
    #         if cc % 1000 == 0:
    #             print(cc)
    #         transition_bars = pre_prog.progression[-1] + cur_prog.progression[0]
    #         if tuple(transition_bars) not in transition_score and tuple(transition_bars) not in new_transition_score:
    #             chord_sequence_prev = [pre_prog.progression[-1][0]]
    #             for i in pre_prog.progression[-1]:
    #                 chord_sequence_prev.append(i) if i != chord_sequence_prev[-1] else None
    #
    #             chord_sequence_cur = [cur_prog.progression[-1][0]]
    #             for i in cur_prog.progression[0]:
    #                 chord_sequence_cur.append(i) if i != chord_sequence_cur[-1] else None
    #
    #             prev_part = [chord_sequence_prev[i:] for i in range(len(chord_sequence_prev))]
    #             cur_part = [chord_sequence_cur[:i + 1] for i in range(len(chord_sequence_cur))]
    #
    #             chord_sequences_dup = []
    #             for i in range(len(prev_part)):
    #                 for j in range(len(cur_part)):
    #                     chord_sequences_dup.append(prev_part[i] + cur_part[j])
    #
    #             chord_sequences = []
    #             for c in chord_sequences_dup:
    #                 new = [c[0]]
    #                 for i in c:
    #                     new.append(i) if i != new[-1] else None
    #                 chord_sequences.append(new)
    #
    #             # search the number of occurrence in the template space
    #             score = 0
    #             for template in all:
    #                 unique_temp = [template.get(only_root=True, flattened=True)[0]]
    #                 for i in template.get(only_root=True, flattened=True):
    #                     unique_temp.append(i) if i != unique_temp[-1] else None
    #                 for chord_sequence in chord_sequences:
    #                     # if chord_sequence in unique_temp:
    #                     #     score += 1
    #                     if len(chord_sequence) > len(unique_temp):
    #                         continue
    #                     all_slices = [unique_temp[i:i + len(chord_sequence)]
    #                                   for i in range(len(unique_temp) - len(chord_sequence) + 1)]
    #                     new = []
    #                     for slc in all_slices:
    #                         if len(slc) != 1:
    #                             new.append(slc)
    #                     all_slices = new
    #                     # print(all_slices, chord_sequence)
    #                     for slc in all_slices:
    #                         if slc == chord_sequence:
    #                             score += 1
    #                             break
    #
    #             new_transition_score[tuple(transition_bars)] = score
    #
    # items = list(new_transition_score.items())
    # keys = [i[0] for i in items]
    # transition_score_value = numpy.array([i[1] for i in items])
    # transition_score_value += 1
    # loged = numpy.log(transition_score_value) / numpy.log(numpy.max(transition_score_value))
    #
    # for i in range(len(keys)):
    #     new_transition_score[keys[i]] = loged[i]
    #
    # transition_score.update(new_transition_score)
    #
    # file = open('transition_score.mdch', 'wb')
    # pickle.dump(transition_score, file)
    # file.close()

    # lib = read_lib()
    # all_lib_names = list(lib.keys())
    # all_names = []
    # all = read_progressions('dict.pcls')
    # count = 0
    # for item in all.items():
    #     prog_list = item[1]
    #     for prog in prog_list:
    #         all_names.append(prog.meta['source'])
    #         count += 1
    #         if count % 10000 == 0:
    #             print(count)
    #         if prog.meta['source'] not in all_lib_names:
    #             original_lib = lib[prog.meta['source'][:-5]]
    #             if prog.meta['source'][-5:] == 'mod/2':
    #                 new_lib = [[i[0] // 2, i[1] // 2, i[2], i[3]] for i in original_lib]
    #             elif prog.meta['source'][-5:] == 'modx2':
    #                 new_lib = [[i[0] * 2, i[1] * 2, i[2], i[3]] for i in original_lib]
    #             else:
    #                 raise Exception
    #             lib[prog.meta['source']] = new_lib
    # print(len(lib))
    #
    # count = 1
    # file = open('source_base' + '.pnt', 'wb')
    # pickle.dump(lib, file)
    # file.close()
    #
    # count = 0
    # items = list(all.items())
    # for item in items:
    #     prog_list = item[1]
    #     new_prog_list = []
    #     for prog in prog_list:
    #         count += 1
    #         if count % 1000 == 0:
    #             print(count)
    #         if prog.meta['source'][-5:] == 'mod/2':
    #             for i in lib[prog.meta['source'][:-5]]:
    #                 if i[0] % 2 != 0 or i[1] % 2 != 0:
    #                     break
    #             else:
    #                 new_prog_list.append(prog)
    #         else:
    #             new_prog_list.append(prog)
    #     if len(new_prog_list) == 0:
    #         del all[item[0]]
    #     else:
    #         all[item[0]] = new_prog_list
    #
    # count = 1
    # for sub_dict in split_huge_progression_dict(all):
    #     file = open('dict' + '.plcs00' + str(count), 'wb')
    #     pickle.dump(sub_dict, file)
    #     file.close()
    #     count += 1
    #
    # file = open('representative.pcls', 'wb')
    # pickle.dump([i[0] for i in all.values()], file)
    # file.close()