# Chorderator Important Ideas

## Model

## Dataset

### Niko

#### Attribute: Reliability

According to the label of the dataset, assign a reliability to each kinds of source.

| Reliability | Source                                                       |
| ----------- | ------------------------------------------------------------ |
| 1.0         | Niko: best chords                                            |
| 0.9         | Niko: chordprog                                              |
| 0.8         | Niko: chord break down                                       |
| 0.7         | Niko: slow chord rhythm                                      |
| 0.6         | Niko: fast chord rhythm-same time                            |
| 0.5         | Niko: arps-back and force, fast chord rhythm-back and force  |
| 0.4         | Niko: melody, epic endings, arps-heaven, arps-triplets, arps-rolling |
| 0.3         | Billboard: all                                               |

#### How to pick templates?

All information about a progression:

| Info              | Description                                     | Ideas                                     |
| ----------------- | ----------------------------------------------- | ----------------------------------------- |
| Source            | Name of the source MIDI                         | Ignore                                    |
| Type              | Positions. e.g., chorus                         | DP                                        |
| Tonic             | Tonic                                           | Ignore                                    |
| Metre             | Metre, usually '4/4'                            | Exactly match the melody (transformation) |
| Mode              | Mode, 'M' or 'm'                                | Exactly match the melody                  |
| Pattern           | Pattern of chord progression. e.g., 'vi-IV-I-V' | Human Interaction?                        |
| Cycle             | The most possible cycle                         | Human Interaction? + Analyze melody style |
| Length            | Length of progression. Number of eighth-note    | Exactly match the melody                  |
| Progression-style | e.g., 'pop', 'edm'                              | Human Interaction                         |
| Chord-style       | e.g., 'classy', 'emotional'                     | Human Interaction                         |
| Rhythm            | Fast or slow                                    | Human Interaction?                        |
| Epic-endings      | True, False, unknown                            | Delete True                               |
| Melodic           | True, False, unknown                            | Delete True                               |
| Folder-id         | The folder ID of the source                     | DP?                                       |


1. deal with interface issue in dp
2. consider squeeze and stretch score (for later)

