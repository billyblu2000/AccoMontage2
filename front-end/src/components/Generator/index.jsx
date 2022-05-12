import React, { Component } from 'react'
import './index.css'
import { LoadingOutlined, CheckCircleOutlined, CaretRightFilled, CaretLeftFilled, PlayCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import { Empty, Spin, Button, Typography, Divider, Card, Tooltip } from 'antd';
import Icon from '../Icon';
import { myServer, server, getCookie } from '../../utils';
import ChordProgression from '../ChordProgression';

const { Title } = Typography;
const { Meta } = Card;
const statusText = [
    'Preparing...',
    'Loading melodies, initializing melody meta...',
    'Analyzing melodies, constructing progressions...',
    'Loading library, refining progressions according to styles...',
    'Synthesizing MIDI...',
    'Synthesizing WAV...',
    'Complete!',
]
function toTop(){
    var scrollToptimer = setInterval(function () {
        var top = document.body.scrollTop || document.documentElement.scrollTop;
        var speed = top / 5;
        if (document.body.scrollTop!==0) {
            document.body.scrollTop -= speed;
        }else {
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
        generated:[],
        playing:'stop'
    }

    styles = [];
    count = 0;

    calcDivWidth = () => {
        
        var card = 0;
        this.state.generated.forEach(function(val, _, __) {
            console.log(val.progression.length)
            card += val.progression.length*75;
        }, 0);
        var total = card + 100 + (this.state.generated.length + 3) * 4 + 2
        console.log(this.state.generated.length)
        console.log(total)
        return total;
    }


    playMp3 = (e) =>{

        if (this.state.playing === 'stop'){
            this.mp3 = new Audio(`/api/chorderator_back_end/music/generated?sessionID=${getCookie('sessionID')}`);
            this.mp3.play();
            this.fadeIn();
            this.mp3.addEventListener('ended', (event) => {
                this.setState({
                        playing:'stop'
                    })
                });
            this.setState({
                playing:'playing'
            })
        }
        else if (this.state.playing === 'pause'){
            this.mp3.play();
            this.setState({
                playing:'playing'
            })
            this.fadeIn();
        }
        else if (this.state.playing === 'playing'){
            this.setState({
                playing:'pause'
            })
            this.fadeOut();
            this.mp3.pause();
        }
    }
    fadeIn = () => {
        var fadeInTimer = setInterval(() => {
            if (this.mp3.volume >= 0.9){
                window.clearInterval(fadeInTimer)
            }
            if (this.mp3.volume + (this.mp3.volume - this.mp3.volume*this.mp3.volume + 0.02) < 1){
                this.mp3.volume += this.mp3.volume - this.mp3.volume*this.mp3.volume + 0.02;
            }
        }, 50)
    }
    fadeOut = () => {
        var fadeOutTimer = setInterval(() => {
            if (this.mp3.volume <= 0.1 ){
                window.clearInterval(fadeOutTimer)
            }
            if (this.mp3.volume - (this.mp3.volume - this.mp3.volume*this.mp3.volume + 0.02) > 0){
                this.mp3.volume -= this.mp3.volume - this.mp3.volume*this.mp3.volume + 0.02;
            }
        }, 50)
    }
    askStage = () => {
        server(`/api/chorderator_back_end/stage_query?sessionID=${getCookie("sessionID")}`, this, 'generatingStage');
        if (this.state.generatingStage === 6){
            console.log('1')
            window.clearInterval(this.askStageInterval);
            server(`/api/chorderator_back_end/generated_query?sessionID=${getCookie("sessionID")}`, this, 'generated');
        }
    }
    componentDidMount(){
        this.askStageInterval = setInterval(this.askStage,500);
    }
    componentWillUnmount(){
        window.clearInterval(this.askStageInterval);
        this.setState({
            playing:'stop'
        })
        this.mp3 = null
    }
    regenerate = () => {
        var values = this.props.values;
        values['newStyles'] = this.styles;
        console.log(values);
        server(`/api/chorderator_back_end/generate?sessionID=${getCookie("sessionID")}`, this, null, 'post', values)
        this.askStageInterval = setInterval(this.askStage,500);
        this.setState({
            generated:[],
            generatingStage:0
        })
        toTop();
    }

    calcStyles = (generated) => {
        console.log(generated);
        this.styles = generated.map(function (item){
            return item.style;
        });
        console.log(this.styles)
    }

    render() {
        this.calcStyles(this.state.generated);
        return (
            <div>
                <div className='upper'>
                    <div style={{width:'50%', float:'left', height:'100%'}}>
                        <div className='status'>
                        {statusText.map((item, idx) => {
                            if (idx < this.state.generatingStage || (idx === this.state.generatingStage && this.state.generatingStage===6) ){
                                return <p><CheckCircleOutlined style={{marginRight:'6px'}}/>{item}</p>
                            }
                            else if (idx === this.state.generatingStage){
                                return <p><LoadingOutlined style={{marginRight:'6px'}}/>{item}</p>
                            }
                            else{
                                return <p></p>
                            }
                        })}
                        </div>
                    </div>
                    <div style={{width:'50%', float:'right', height:'100%'}}>
                    {this.state.generated.length === 0 ? 
                        <div style={{paddingLeft:'50px', paddingRight:'50px', textAlign:'center'}}>
                            <Title level={1} style={{float:'right', fontSize:'25px', color:'#AAAAAA', userSelect:'none'}}>Generating, please wait...</Title>
                            <Divider></Divider>
                            <Spin size="large" style={{marginTop:'50px'}}/>
                        </div>
                        :
                        <div style={{paddingLeft:'50px', paddingRight:'50px'}}>
                            <Title level={1} style={{float:'right', fontSize:'25px', color:'#AAAAAA', userSelect:'none'}}>Progression generated!</Title>
                            <Divider></Divider>
                            <a download='generated.wav' href={true}>
                                <Card hoverable style={{marginTop:'10px', marginBottom:'10px'}}>
                                    <Meta
                                        avatar={this.state.playing === 'playing'? 
                                            <a href={true} onClick={this.playMp3} style={{color:'#73d13d'}} id='whole'><PlayCircleOutlined style={{fontSize:'32px'}}/></a> 
                                            :
                                            <a href={true} onClick={this.playMp3}><PlayCircleOutlined style={{fontSize:'32px'}} id='whole'/></a>  
                                        }
                                        title="Listen to or download WAV"
                                        description="Click the play button on the left to play"
                                    />
                                </Card>
                            </a>
                            <a download='generated.wav' href={myServer + `/api/chorderator_back_end/midi/generated?sessionID=${getCookie("sessionID")}`}>
                                <Card hoverable style={{marginTop:'10px', marginBottom:'10px'}}>
                                    <Meta
                                        avatar={<Icon which='midi'/>}
                                        title="Download MIDI"
                                        description="MIDI consist a melody track and a progression track"
                                    />
                                </Card>
                            </a>
                            
                        </div>
                    }
                    </div>
                </div>
                <div className='down'>
                    {this.state.generated.length === 0 ?
                        <div style={{width:'100%'}}>
                            <Empty style={{marginTop:'150px'}} description='Progression not generated yet.'/>
                        </div>
                        :
                        <div style={{ minWidth: this.calcDivWidth() }}>
                            <div style={{padding:'2px'}}>
                                <div className='card-start'><CaretRightFilled  style={{lineHeight:'485px', fontSize:'25px'}}/></div>
                                {this.state.generated.map((item, idx) => {
                                    return <ChordProgression data={item} father={this} index={idx}></ChordProgression>
                                })}
                                <div className='card-end'><CaretLeftFilled  style={{lineHeight:'485px', fontSize:'25px'}}/></div>
                            </div>
                        </div>
                    }
                </div>

                <div style={{marginTop:'50px', marginLeft:'20%', marginRight:'20%', textAlign:'center'}}>
                    <Tooltip title="Regenerate with new parameters and styles" overlayStyle={{minWidth:'300px'}}>
                        {this.state.generated.length === 0 ?
                            <Button shape="circle" icon={<ReloadOutlined />} type='primary' size='large' disabled/>
                            :
                            <Button shape="circle" icon={<ReloadOutlined />} type='primary' size='large' onClick={this.regenerate}/>
                        }
                    </Tooltip>
                </div>
                <div style={{minHeight:'50px'}}>
                
                </div>
            </div>
        )
    }
}