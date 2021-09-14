from settings import *
from chords.ChordProgression import read_progressions, print_progression_list
from utils.constants import *
from utils.utils import MIDILoader
from utils.utils import pick_progressions, np, listen
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # POP909 = 'progressions_from_pop909.txt'
    DEFAULT = 'progressions.txt'

    # pick out all progressions with metre = 4/4
    prog_list = read_progressions(progression_file = DEFAULT)
    print('total:', len(prog_list))
    prog_4 = []
    for i in prog_list:
        if len(i.progression[0]) == 8:
            prog_4.append(i)
    print('progressions with metre = 4/4: #', len(prog_4))

    # pick out all 8-bar progressions with metre = 4/4
    sub_prog = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8:
            sub_prog.append(i)
    print('8-bar progressions with metre = 4/4: #',len(sub_prog))

    sub_dict = {}
    for i in prog_list:
        if len(i.progression[0]) == 8:
            try:
                sub_dict[len(i.progression)] += 1
            except:
                sub_dict[len(i.progression)] = 1
    print(sub_dict)

    new_sub = {k: v for k, v in reversed(sorted(sub_dict.items(), key=lambda item: item[1]))}

    plt.bar(new_sub.keys(), new_sub.values())
    plt.title('# bars progressions with metre = 4/4, Total # 2172')
    plt.show()



    # stats w.r.t. prog len, metre, type(loc), mode

    print('----------------------------------------')

    prog_84M = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta[
            'mode'] == 'M':
            prog_84M.append(i)
    print('8-bar progressions with metre = 4/4, All, Major: #', len(prog_84M))

    prog_84m = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta[
            'mode'] == 'm':
            prog_84m.append(i)
    print('8-bar progressions with metre = 4/4, All, minor: #', len(prog_84m))


    prog_84cM = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'chorus' and i.meta['mode'] == 'M':
            prog_84cM.append(i)
    print('8-bar progressions with metre = 4/4, Chorus, Major: #', len(prog_84cM))

    prog_84cm = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'chorus' and i.meta['mode'] == 'm':
            prog_84cm.append(i)
    print('8-bar progressions with metre = 4/4, Chorus, minor: #', len(prog_84cm))

    prog_84vM = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'verse' and i.meta['mode'] == 'M':
            prog_84vM.append(i)
    print('8-bar progressions with metre = 4/4, Verse, Major: #', len(prog_84vM))

    prog_84vm = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'verse' and i.meta[
            'mode'] == 'm':
            prog_84vm.append(i)
    print('8-bar progressions with metre = 4/4, Verse, minor: #', len(prog_84vm))

    prog_84iM = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'intro' and i.meta[
            'mode'] == 'M':
            prog_84iM.append(i)
    print('8-bar progressions with metre = 4/4, Intro, Major: #', len(prog_84iM))

    prog_84im = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'intro' and i.meta[
            'mode'] == 'm':
            prog_84im.append(i)
    print('8-bar progressions with metre = 4/4, Intro, minor: #', len(prog_84im))

    prog_84bM = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'bridge' and i.meta[
            'mode'] == 'M':
            prog_84bM.append(i)
    print('8-bar progressions with metre = 4/4, Bridge, Major: #', len(prog_84bM))

    prog_84bm = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'bridge' and i.meta[
            'mode'] == 'm':
            prog_84bm.append(i)
    print('8-bar progressions with metre = 4/4, Bridge, minor: #', len(prog_84bm))

    prog_84pM = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'pre-chorus' and i.meta[
            'mode'] == 'M':
            prog_84pM.append(i)
    print('8-bar progressions with metre = 4/4, Pre-chorus, Major: #', len(prog_84pM))

    prog_84pm = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'pre-chorus' and i.meta[
            'mode'] == 'm':
            prog_84pm.append(i)
    print('8-bar progressions with metre = 4/4, Pre-chorus, minor: #', len(prog_84pm))

    prog_84itM = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'interlude' and i.meta[
            'mode'] == 'M':
            prog_84itM.append(i)
    print('8-bar progressions with metre = 4/4, Interlude, Major: #', len(prog_84itM))

    prog_84itm = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'interlude' and i.meta[
            'mode'] == 'm':
            prog_84itm.append(i)
    print('8-bar progressions with metre = 4/4, Interlude, minor: #', len(prog_84itm))

    prog_84sM = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'solo' and i.meta[
            'mode'] == 'M':
            prog_84sM.append(i)
    print('8-bar progressions with metre = 4/4, Solo, Major: #', len(prog_84sM))

    prog_84sm = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'solo' and i.meta[
            'mode'] == 'm':
            prog_84sm.append(i)
    print('8-bar progressions with metre = 4/4, Solo, minor: #', len(prog_84sm))

    prog_84tM = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'transition' and i.meta[
            'mode'] == 'M':
            prog_84tM.append(i)
    print('8-bar progressions with metre = 4/4, Transition, Major: #', len(prog_84tM))

    prog_84tm = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 8 and i.meta['type'] == 'transition' and i.meta[
            'mode'] == 'm':
            prog_84tm.append(i)
    print('8-bar progressions with metre = 4/4, Transition, minor: #', len(prog_84tm))

    print('8-bar progressions with metre = 4/4, Other, Major: #', len(prog_84M) - 144 - 124 - 59 - 60 - 19 - 13 - 36 - 1)
    print('8-bar progressions with metre = 4/4, Other, minor: #', len(prog_84m) - 56 - 32 - 21 - 16 - 10 - 7 - 7)

    print('----------------------------------------')

    prog_44M = []
    for i in prog_list:
        if len(i.progression) == 4 and len(i.progression[0]) == 8 and i.meta[
            'mode'] == 'M':
            prog_44M.append(i)
    print('4-bar progressions with metre = 4/4, All, Major: #', len(prog_44M))

    prog_44m = []
    for i in prog_list:
        if len(i.progression) == 4 and len(i.progression[0]) == 8 and i.meta[
            'mode'] == 'm':
            prog_44m.append(i)
    print('4-bar progressions with metre = 4/4, All, minor: #', len(prog_44m))

    print('----------------------------------------')

    prog_164M = []
    for i in prog_list:
        if len(i.progression) == 16 and len(i.progression[0]) == 8 and i.meta[
            'mode'] == 'M':
            prog_164M.append(i)
    print('16-bar progressions with metre = 4/4, All, Major: #', len(prog_164M))

    prog_164m = []
    for i in prog_list:
        if len(i.progression) == 16 and len(i.progression[0]) == 8 and i.meta[
            'mode'] == 'm':
            prog_164m.append(i)
    print('16-bar progressions with metre = 4/4, All, minor: #', len(prog_164m))

    print('----------------------------------------')

    prog_124M = []
    for i in prog_list:
        if len(i.progression) == 12 and len(i.progression[0]) == 8 and i.meta[
            'mode'] == 'M':
            prog_124M.append(i)
    print('12-bar progressions with metre = 4/4, All, Major: #', len(prog_124M))

    prog_124m = []
    for i in prog_list:
        if len(i.progression) == 12 and len(i.progression[0]) == 8 and i.meta[
            'mode'] == 'm':
            prog_124m.append(i)
    print('12-bar progressions with metre = 4/4, All, minor: #', len(prog_124m))

    print('----------------------------------------')

    prog_83M = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 6 and i.meta[
            'mode'] == 'M':
            prog_83M.append(i)
    print('8-bar progressions with metre = 3/4, All, Major: #', len(prog_83M))

    prog_83m = []
    for i in prog_list:
        if len(i.progression) == 8 and len(i.progression[0]) == 6 and i.meta[
            'mode'] == 'm':
            prog_83m.append(i)
    print('8-bar progressions with metre = 3/4, All, minor: #', len(prog_83m))

    print('----------------------------------------')

    prog_43M = []
    for i in prog_list:
        if len(i.progression) == 4 and len(i.progression[0]) == 6 and i.meta[
            'mode'] == 'M':
            prog_43M.append(i)
    print('4-bar progressions with metre = 3/4, All, Major: #', len(prog_43M))

    prog_43m = []
    for i in prog_list:
        if len(i.progression) == 4 and len(i.progression[0]) == 6 and i.meta[
            'mode'] == 'm':
            prog_43m.append(i)
    print('4-bar progressions with metre = 3/4, All, minor: #', len(prog_43m))

    print('----------------------------------------')

    prog_163M = []
    for i in prog_list:
        if len(i.progression) == 16 and len(i.progression[0]) == 6 and i.meta[
            'mode'] == 'M':
            prog_163M.append(i)
    print('16-bar progressions with metre = 3/4, All, Major: #', len(prog_163M))

    prog_163m = []
    for i in prog_list:
        if len(i.progression) == 16 and len(i.progression[0]) == 6 and i.meta[
            'mode'] == 'm':
            prog_163m.append(i)
    print('16-bar progressions with metre = 3/4, All, minor: #', len(prog_163m))





    d = {'84cM':144, '84cm':56, '84vM':124, '84vm':32, '84bM':60, '84bm':16, '84iM':59, '84im':21,
         '84pM':19, '84pm':10, '84itM':13, '84itm':7, '84sM':26, '84sm':7, '84oM':18, '84sm':14}

    new = {k: v for k, v in reversed(sorted(d.items(), key=lambda item: item[1]))}

    plt.bar(new.keys(),new.values())
    plt.title('8-bar progressions with metre = 4/4, Total # 636')
    plt.show()