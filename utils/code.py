import json
import os

import numpy as np
if __name__ == '__main__':
    data_root_dir = "/Users/billyyi/dataset/Niko/Niko's Ultimate MIDI Pack/"
    all = []
    for root, dirs, files in os.walk(data_root_dir):
        if '2 - Best Chords' in root:
            for file in files:
                if file[0] != '.':
                    print(file.lstrip('Niko_Kotoulas_').rstrip('_.mid'))
