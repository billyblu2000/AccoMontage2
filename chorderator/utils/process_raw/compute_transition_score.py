transition_dict = {}


def transition_score(cur_template, prev_template, templates):
    transition_bars = prev_template.progression[-1] + cur_template.progression[0]
    if tuple(transition_bars) in transition_dict:
        return transition_dict[tuple(transition_bars)]

    chord_sequence_prev = [prev_template.progression[-1][0]]
    for i in prev_template.progression[-1]:
        chord_sequence_prev.append(i) if i != chord_sequence_prev[-1] else None

    chord_sequence_cur = [cur_template.progression[-1][0]]
    for i in cur_template.progression[0]:
        chord_sequence_cur.append(i) if i != chord_sequence_cur[-1] else None

    prev_part = [chord_sequence_prev[i:] for i in range(len(chord_sequence_prev))]
    cur_part = [chord_sequence_cur[:i + 1] for i in range(len(chord_sequence_cur))]

    # chord_sequences contains all sequences of chord that contains the transition two chords in the transition bars

    chord_sequences_dup = []
    for i in range(len(prev_part)):
        for j in range(len(cur_part)):
            chord_sequences_dup.append(prev_part[i] + cur_part[j])

    chord_sequences = []
    for c in chord_sequences_dup:
        new = [c[0]]
        for i in c:
            new.append(i) if i != new[-1] else None
        chord_sequences.append(new)

    # search the number of occurrence in the template space
    score = 0
    for template in templates:
        unique_temp = [template.get(only_root=True, flattened=True)[0]]
        for i in template.get(only_root=True, flattened=True):
            unique_temp.append(i) if i != unique_temp[-1] else None
        for chord_sequence in chord_sequences:
            # if chord_sequence in unique_temp:
            #     score += 1
            if len(chord_sequence) > len(unique_temp):
                continue
            all_slices = [unique_temp[i:i + len(chord_sequence)]
                          for i in range(len(unique_temp) - len(chord_sequence) + 1)]
            new = []
            for slc in all_slices:
                if len(slc) != 1:
                    new.append(slc)
            all_slices = new
            # print(all_slices, chord_sequence)
            for slc in all_slices:
                if slc == chord_sequence:
                    score += 1
                    break

    # new_score = log_{max_score}(score)

    transition_dict[tuple(transition_bars)] = score

    if cur_template.progression_class['cycle'][1] == 0 or prev_template.progression_class['cycle'][1] == 0:
        cycle_penalty = 1
    else:
        if cur_template.progression_class['cycle'][1] == prev_template.progression_class['cycle'][1]:
            cycle_penalty = 1
        elif cur_template.progression_class['cycle'][1] / prev_template.progression_class['cycle'][1] <= 2 \
                or prev_template.progression_class['cycle'][1] / cur_template.progression_class['cycle'][1] <= 2:
            cycle_penalty = 0.95
        else:
            cycle_penalty = 0.9

    return score * cycle_penalty / len(templates)


if __name__ == '__main__':
    # all = read_progressions('representative.pcls')
    # count = 0
    # for i in all:
    #     print(count)
    #     for j in all:
    #         transition_score(i,j,all)
    #     count += 1
    # file = open('new_transition_score.mdch', 'wb')
    # pickle.dump(transition_dict, file)
    # file.close()
    #
    # trans = pickle.load(open('new_transition_score.mdch', 'rb'))
    # max_score = max(trans.values())
    # for item in trans.items():
    #     trans[item[0]] = math.log(item[1]) / math.log(max_score) if item[1] != 0 else 0
    #
    # file = open('new_new_transition_score.mdch', 'wb')
    # pickle.dump(trans, file)
    # file.close()
    pass


