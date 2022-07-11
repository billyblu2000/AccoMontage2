import React, { Component } from 'react'
import { Typography, Select, Divider, Button } from 'antd'
import { style, myServer } from '../../utils';
import PianoRoll from '../PianoRoll';
import './index.css'

const { Title, Paragraph } = Typography;
const { Option } = Select;

function ChordText({ index, progression }) {

    function parseChord(chord){
        var parsed = chord[0];
        if (chord[1] !== ' '){
            parsed = parsed + chord[1];
        }
        if (chord[2] === '1'){
            parsed = parsed + 'm';
        }
        return parsed;
    }

    React.useEffect(() => {

        var allChords = [];
        for (let i=0; i<progression.length; i++){
            allChords = allChords.concat(progression[i]);
        }

        const pixelsPerEighthNote = 8.4;
        var allChordsPositions = [];
        var last = '';
        for (let i=0; i<allChords.length; i++){
            if (allChords[i] !== last){
                last = allChords[i];
                allChordsPositions.push([parseChord(allChords[i]), pixelsPerEighthNote*i]);
            }
        }

        var myChordTextCanvas = document.getElementById('chord-text' + index);
        var ctx = myChordTextCanvas.getContext('2d');
        ctx.font = '20px Times New Roman';
        for (let i=0; i<allChordsPositions.length; i++){
            ctx.fillText(allChordsPositions[i][0], allChordsPositions[i][1], 18);
        }
    }, []);

    return (
        <canvas id={'chord-text' + index} width={540} height={20} style={{ backgroundColor: '#fff7e6' }}></canvas>
    )
}

export default class ChordProgression extends Component {

    state = {
        style: this.props.style,
        melodyVis: null,
    }

    setMelodyVis = (melodyVis) => {
        this.setState({ melodyVis: melodyVis })
    }

    handleStyleChange = (value) => {
        var prevStyles = this.props.father.state.styles;
        prevStyles[this.props.index] = value;
        this.props.father.setState({ styles: prevStyles })
    }

    static getDerivedStateFromProps(nextProps, prevState) {
        return { style: nextProps.style }
    }

    render() {
        var otherStyles = this.props.data['otherStyles'];
        return (
            <div className='card' style={{ width: `${this.props.data['progression'].length * 75}px` }}>
                <div style={{ textAlign: 'center' }}>
                    <Title level={3} style={{ color: 'gray', marginBottom: '0px' }} >
                        <a id='b' href={true}>PROGRESSION</a>
                    </Title>
                </div>
                <div style={{ width: '50%', float: 'left', marginTop: '20px' }}>
                    <Paragraph style={{ fontSize: '10px', color: 'gray', marginLeft: '12px' }}>Style</Paragraph>
                    <Select value={this.state.style} autoFocus={false} bordered={false} style={{ fontSize: '25px' }} onSelect={this.handleStyleChange}>
                        {style.map((item) => {
                            return <Option value={item.value} disabled={!contains(otherStyles, item.value)}>{item.ui}</Option>
                        })}
                    </Select>

                </div>
                {/* 
                <div style={{ textAlign: 'center', marginTop: '120px', backgroundColor: '#fff7e6', borderRadius: '10px' }}>
                    <div>
                        <Title level={3} style={{ fontSize: '20px' }}>
                            {this.props.data['progression'].map((item, idx) => {
                                return (<span>
                                    <Divider type='vertical' style={{ backgroundColor: 'black', marginRight:'16px', marginLeft: idx === 0 ? '0px' : '16px', display:'space-around' }} />
                                    <span style={{display:'space-around'}}>{displayChord(item[0])}</span>
                                </span>)
                            })}
                        </Title>
                    </div>
                </div> */}
                <div style={{marginTop:'110px'}}></div>
                <PianoRoll midiURL={myServer.slice(0, -4) + '/midi/' + this.props.data.midi_name.melody} id={this.props.index + 'melody'} pixelsPerTimeStep={35} setAdditionalVisualizer={this.setMelodyVis}></PianoRoll>
                <div style={{ marginTop: '20px' }}></div>
                <div style={{ marginTop: '10px' }}>
                    <ChordText index={this.props.index} progression={this.props.data.progression_full}></ChordText>
                </div>
                <PianoRoll midiURL={myServer.slice(0, -4) + '/midi/' + this.props.data.midi_name.chord} midiWithoutMelodyURL={myServer.slice(0, -4) + '/midi/' + this.props.data.midi_name.chord_WM} id={this.props.index + 'chord'} pixelsPerTimeStep={35} noteHeight={3} additionalVisualizer={this.state.melodyVis}></PianoRoll>
                <div style={{ marginTop: '5px' }}></div>
                <PianoRoll midiURL={myServer.slice(0, -4) + '/midi/' + this.props.data.midi_name.acc} midiWithoutMelodyURL={myServer.slice(0, -4) + '/midi/' + this.props.data.midi_name.acc_WM} id={this.props.index + 'acc'} pixelsPerTimeStep={35} noteHeight={3} additionalVisualizer={this.state.melodyVis}></PianoRoll>
                <Button type='dashed' style={{ bottom: '20px', position: 'absolute', width: '80%', left: '10%' }} onClick={() => this.props.father.tryChangeAllStyle(this.state.style)}>Change all styles to current style</Button>
            </div>
        )
    }
}
function contains(arr, obj) {
    var i = arr.length;
    while (i--) {
        if (arr[i] === obj) {
            return true;
        }
    }
    return false;
}
function displayChord(ori) {
    var property = ''
    if (ori.slice(2, 3) === '1') {
        property = 'm'
    }
    if (ori.slice(1, 2) === ' ') {
        return ori.slice(0, 1) + property;
    }
    else {
        return ori.slice(0, 2) + property;
    }
}