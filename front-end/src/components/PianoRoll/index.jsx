import React from "react";
import './index.css';

const mm = require('@magenta/music');
const soundFontURL = 'https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus';

export default function PianoRoll({ midiURL, id, midiWithoutMelodyURL, additionalVisualizer, setAdditionalVisualizer, noteHeight, pixelsPerTimeStep, color, backgroundColor }) {

    const [noteSequence, setNoteSequence] = React.useState(null);
    const [noteSequenceWithoutMelody, setNoteSequenceWithoutMelody] = React.useState(null); 
    const [player, setPlayer] = React.useState(null);
    const [visualizer, setVisualizer] = React.useState(null);

    React.useEffect(() => {
        mm.urlToNoteSequence(midiURL).then((ns) => setNoteSequence(ns))
        if (midiWithoutMelodyURL !== undefined){
            mm.urlToNoteSequence(midiWithoutMelodyURL).then((ns) => setNoteSequenceWithoutMelody(ns))
        }
    }, [midiURL, midiWithoutMelodyURL]);

    React.useEffect(() => {
        if ((midiWithoutMelodyURL === undefined && noteSequence !== null) || 
            (midiWithoutMelodyURL !== undefined && noteSequence !== null && noteSequenceWithoutMelody !== null)) {
            var viz = new mm.Visualizer(midiWithoutMelodyURL? noteSequenceWithoutMelody: noteSequence, document.getElementById(id), {
                noteHeight: noteHeight || 6,
                pixelsPerTimeStep: pixelsPerTimeStep || 26,
                noteSpacing: 1,
                noteRGB: color || '0, 59, 118',
                activeNoteRGB: '225, 111, 34',
            });
            var vizPlayer = new mm.SoundFontPlayer(soundFontURL, undefined, undefined, undefined, {
                run: (note) => {
                    viz.redraw(note);
                    if (additionalVisualizer){
                        additionalVisualizer.redraw(note);
                    }
                },
                stop: () => {
                    viz.redraw();
                    if (additionalVisualizer){
                        additionalVisualizer.redraw();
                    }
                },
            });
            setVisualizer(viz);
            if (setAdditionalVisualizer){
                setAdditionalVisualizer(viz);
            }
            setPlayer(vizPlayer);
        }
    }, [noteSequence, noteSequenceWithoutMelody, additionalVisualizer, setAdditionalVisualizer, midiWithoutMelodyURL, id, noteHeight, pixelsPerTimeStep, color]);

    const handleClick = () => {
        if (player.getPlayState() === 'stopped') {
            player.start(noteSequence);
        }
        else {
            player.stop();
            visualizer.redraw();
            if (additionalVisualizer){
                additionalVisualizer.redraw();
            }
        }
    }

    return (
        <canvas id={id} onClick={() => handleClick()} style={{display:'block', backgroundColor:backgroundColor?backgroundColor:true}}/>
    )
}