if __name__ == '__main__':
    chord_sequence_prev = [1]
    for i in [1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, ]:
        chord_sequence_prev.append(i) if i != chord_sequence_prev[-1] else None
    print(chord_sequence_prev)