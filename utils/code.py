import json
import os
import pandas


if __name__ == '__main__':
    data_root_dir = "/Users/billyyi/dataset/Niko/Niko's Ultimate MIDI Pack/"
    all = []
    for root, dirs, files in os.walk(data_root_dir):
        if '2 - Best Chords' in root \
                or ('3 - Rest Of Pack' in root and 'Basslines' not in root):
            for file in files:
                if file[0] != '.':
                    progression_class = {
                        'name':'unknown',
                        'type': 'unknown',  # positions, e.g., 'verse', 'chorus', ...
                        'pattern': 'unknown',  # e.g., 'I-vi-IV-V', ...
                        'cycle': 'unknown',  # 'no-cycle', 'short', 'mid', 'long', ...?
                        'progression-style': 'unknown',  # 'pop', 'edm', 'dark', ...
                        'chord-style': 'unknown',  # 'classy', 'emotional', 'standard'
                        'performing-style':'unknown',
                        'rhythm': 'unknown',  # 'fast-back-and-force', 'fast-same-time', 'slow'
                        'epic-endings': 'unknown',  # 'True', 'False'
                    }
                    if '2 - Best Chords' in root:
                        if 'Dark_HipHop_Trap' in root:
                            progression_class['progression-style'] = 'dark'
                        elif 'EDM' in root:
                            progression_class['progression-style'] = 'edm'
                        elif 'Emotional' in root:
                            progression_class['progression-style'] = 'emotional'
                        elif 'Pop' in root:
                            progression_class['progression-style'] = 'pop'
                        elif 'R&B_Neosoul' in root:
                            progression_class['progression-style'] = 'r&b'
                        if 'Classy_7th_9th' in root:
                            progression_class['chord-style'] = 'classy'
                        elif 'Emotional' in root:
                            progression_class['chord-style'] = 'emotional'
                        elif 'Standard' in root:
                            progression_class['chord-style'] = 'standard'
                    elif '3 - Rest Of Pack' in root:
                        root_list = root.split('/')
                        for item in root_list:
                            if '(' in item:
                                pattern = item
                                break
                        else:
                            raise Exception
                        pattern = pattern.split('(')[1].rstrip(')')
                        progression_class['pattern'] = pattern
                        if 'Arps' in root:
                            progression_class['performing-style'] = 'arpeggio'
                        elif 'Epic Endings' in root:
                            progression_class['epic-endings'] = 'True'
                        elif 'Back & Forth' in root:
                            progression_class['rhythm'] = 'fast-back-and-force'
                        elif 'Same Time' in root:
                            progression_class['rhythm'] = 'fast-same-time'
                        elif 'Slow Chord Rhythm' in root:
                            progression_class['rhythm'] = 'slow'
                        elif 'Melodies' in root:
                            progression_class['melodic'] = 'True'
                    progression_class['name'] = file
                    all.append(progression_class)

    pandas.DataFrame(all).to_excel('out.xlsx', index=False)
