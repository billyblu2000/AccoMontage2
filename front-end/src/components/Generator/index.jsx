import React, { Component } from 'react'
import './index.css'
import { LoadingOutlined, CheckCircleOutlined, CaretRightFilled, CaretLeftFilled, PlayCircleOutlined } from '@ant-design/icons';
import { Empty, Spin, Button, Typography, Divider, Card, Form, Slider, Checkbox } from 'antd';
import Icon from '../Icon';
import { myServer, server } from '../../utils';
import ChordProgression from '../ChordProgression';

const { Title } = Typography;
const { Meta } = Card;
const statusText = [
    'Preparing...',
    'Loading melodies, initializing melody meta...',
    'Analyzing melodies, constructing progressions...',
    'Loading library, refining progressions according to styles...',
    'Generating textures...',
    'Synthesizing...',
    'Complete!',
]
function toTop() {
    var scrollToptimer = setInterval(function () {
        var top = document.body.scrollTop || document.documentElement.scrollTop;
        var speed = top / 5;
        if (document.body.scrollTop !== 0) {
            document.body.scrollTop -= speed;
        } else {
            document.documentElement.scrollTop -= speed;
        }
        if (top === 0) {
            clearInterval(scrollToptimer);
        }
    }, 30);
}
export default class Generator extends Component {


    state = {
        generatingStage: 0,
        generated: [],
        generatedChordName: null,
        generatedAccName: null,
        playing: 'stop',
        textureStyleControl: this.props.values['enable_texture_style'],
        styles: []
    }

    count = 0;

    calcDivWidth = () => {

        var card = 0;
        this.state.generated.forEach(function (val, _, __) {
            card += val.progression.length * 75;
        }, 0);
        var total = card + 100 + (this.state.generated.length + 3) * 4 + 2
        return total;
    }


    playMp3 = (e) => {

        if (this.state.playing === 'stop') {
            this.mp3 = new Audio(myServer + `/wav/${Math.random()}`);
            this.mp3.play();
            this.mp3.addEventListener('ended', (event) => {
                this.setState({
                    playing: 'stop'
                })
            });
            this.setState({
                playing: 'playing'
            })
        }
        else if (this.state.playing === 'pause') {
            this.mp3.play();
            this.setState({
                playing: 'playing'
            })
        }
        else if (this.state.playing === 'playing') {
            this.setState({
                playing: 'pause'
            })
            this.mp3.pause();
        }
    }

    askStage = () => {
        server(`/stage_query`, this, null, 'get', null, this.askStageCallback);
        if (this.state.generatingStage === 7) {
            window.clearInterval(this.askStageInterval);
            server(`/generated_query`, this, null, 'get', null, this.generateQueryCallback);
        }
    }

    askStageCallback = (res) => {
        if (res.status === 'ok') {
            this.setState({ generatingStage: parseInt(res.stage) })
        }
    }

    generateQueryCallback = (res) => {
        if (res.status === 'ok') {
            this.setState({ generated: res.log, styles: res.log.map(item => item.style), generatedChordName: res.chord_midi_name, generatedAccName: res.acc_midi_name })
        }
    }

    componentDidMount() {
        this.askStageInterval = setInterval(this.askStage, 2000)
    }
    componentWillUnmount() {
        window.clearInterval(this.askStageInterval);
        this.setState({
            playing: 'stop'
        })
        this.mp3 = null
    }
    regenerate = () => {
        var values = this.props.values;
        values['chord_style'] = this.state.styles;
        values['rhythm_density'] = this.refs.form.getFieldValue('rhythm_density');
        values['voice_number'] = this.refs.form.getFieldValue('voice_number');
        values['enable_texture_style'] = this.refs.form.getFieldValue('enable_texture_style');
        server(`/generate`, this, null, 'post', values)
        this.askStageInterval = setInterval(this.askStage, 500);
        this.setState({
            generated: [],
            generatingStage: 0,
            playing: 'stop'
        })
        toTop();
    }

    tryChangeAllStyle = (newStyle) => {
        var newStyles = [];
        for (let i = 0; i < this.state.generated.length; i++) {
            if (contains(this.state.generated[i].otherStyles, newStyle)) {
                newStyles.push(newStyle);
            }
            else {
                newStyles.push(this.state.styles[i]);
            }
        }
        this.setState({ styles: newStyles });
    }


    render() {
        return (
            <div>
                <div className='upper'>
                    <div style={{ width: '50%', float: 'left', height: '100%' }}>
                        <div className='status'>
                            {statusText.map((item, idx) => {
                                if (idx < this.state.generatingStage || (idx === this.state.generatingStage && this.state.generatingStage === 6)) {
                                    return <p><CheckCircleOutlined style={{ marginRight: '6px' }} />{item}</p>
                                }
                                else if (idx === this.state.generatingStage) {
                                    return <p><LoadingOutlined style={{ marginRight: '6px' }} />{item}</p>
                                }
                                else {
                                    return <p></p>
                                }
                            })}
                        </div>
                    </div>
                    <div style={{ width: '50%', float: 'right', height: '100%' }}>
                        {this.state.generated.length === 0 ?
                            <div style={{ paddingLeft: '50px', paddingRight: '50px', textAlign: 'center' }}>
                                <Title level={1} style={{ float: 'right', fontSize: '25px', color: '#AAAAAA', userSelect: 'none' }}>Generating, please wait...</Title>
                                <Divider></Divider>
                                <Spin size="large" style={{ marginTop: '50px' }} />
                            </div>
                            :
                            <div style={{ paddingLeft: '50px', paddingRight: '50px' }}>
                                <Title level={1} style={{ float: 'right', fontSize: '25px', color: '#AAAAAA', userSelect: 'none' }}>Progression generated!</Title>
                                <Divider></Divider>
                                <a download='chord.mid' href={`http://127.0.0.1:5000/midi/${this.state.generatedChordName}`}>
                                    <Card hoverable style={{ marginTop: '10px', marginBottom: '10px' }}>
                                        <Meta
                                            avatar={<Icon which='midi' />}
                                            title={<div style={{ fontSize: '20px' }}>Download Chords</div>}
                                            description="MIDI consist a melody track and a progression track"
                                        />
                                    </Card>
                                </a>
                                <a download='accompaniment.mid' href={`http://127.0.0.1:5000/midi/${this.state.generatedAccName}`}>
                                    <Card hoverable style={{ marginTop: '10px', marginBottom: '10px' }}>
                                        <Meta
                                            avatar={<Icon which='midi' />}
                                            title={<div style={{ fontSize: '20px' }}>Download Accompaniment</div>}
                                            description="MIDI consist a melody track and a accompaniment track"
                                        />
                                    </Card>
                                </a>
                            </div>
                        }
                    </div>
                </div>
                <div className='down' style={{ marginBottom: '30px' }}>
                    {this.state.generated.length === 0 ?
                        <div style={{ width: '100%' }}>
                            <Empty style={{ marginTop: '150px' }} description='Progression not generated yet.' />
                        </div>
                        :
                        <div style={{ minWidth: this.calcDivWidth() }}>
                            <div style={{ padding: '2px' }}>
                                <div className='card-start'><CaretRightFilled style={{ lineHeight: '485px', fontSize: '25px' }} /></div>
                                {this.state.generated.map((item, idx) => {
                                    return <ChordProgression data={item} father={this} index={idx} style={this.state.styles[idx]}></ChordProgression>
                                })}
                                <div className='card-end'><CaretLeftFilled style={{ lineHeight: '485px', fontSize: '25px' }} /></div>
                            </div>
                        </div>
                    }
                </div>
                <Form ref='form'
                    initialValues={{
                        enable_texture_style: this.props.values['enable_texture_style'],
                        rhythm_density: this.props.values['rhythm_density'],
                        voice_number: this.props.values['voice_number']
                    }}>
                    <Form.Item name="enable_texture_style" label='Enable Texture Style Controlling' valuePropName="checked">
                        <Checkbox checked={this.state.textureStyleControl} onChange={(e) => this.setState({ textureStyleControl: e.target.checked })} />
                    </Form.Item>

                    <Form.Item name="rhythm_density" label="Texture Rhythm Density (RD)"
                        rules={[{ required: true, message: 'Please select a RD!' }]}
                    >
                        <Slider max={4} min={0} step={1} dots disabled={!this.state.textureStyleControl} />
                    </Form.Item>

                    <Form.Item name="voice_number" label="Texture Voice Number (VN)"
                        rules={[{ required: true, message: 'Please select a VN!' }]}
                    >
                        <Slider max={4} min={0} step={1} dots disabled={!this.state.textureStyleControl} />
                    </Form.Item>
                </Form>
                <div style={{ marginTop: '50px', marginLeft: '20%', marginRight: '20%', textAlign: 'center' }}>
                    {this.state.generated.length === 0 ?
                        <Button shape="round" type='primary' size='large' style={{ height: '40px' }} disabled ><div style={{ fontSize: '16px' }}>Re-generate subject to the selected styles</div></Button>
                        :
                        <Button shape="round" type='primary' size='large' style={{ height: '40px' }} onClick={this.regenerate} ><div style={{ fontSize: '16px' }}>Re-generate subject to the selected styles</div></Button>
                    }
                </div>
                <div style={{ minHeight: '50px' }}>

                </div>
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