import React, { Component } from 'react'
import { Typography, Select, Divider, Button, Tooltip } from 'antd'
import { cycle, pattern, style, position, rhythm } from '../../utils';
import './index.css'

const { Title , Paragraph} = Typography;
const { Option } = Select;

export default class ChordProgression extends Component {

    state = {
        playing:'stop',
    }

    play = (event) => {

        if (this.state.playing === 'stop'){
            this.mp3 = new Audio("/api/chorderator_back_end/music");
            this.mp3.play();
            this.setState({
                playing:'playing'
            })
        }
        else if (this.state.playing === 'pause'){
            this.mp3.play();
            this.setState({
                playing:'playing'
            })
        }
        else if (this.state.playing === 'playing'){
            this.mp3.pause();
            this.setState({
                playing:'pause'
            })
        }
    }

    handleStyleChange = (value) => {
        this.props.father.styles[this.props.index] = value;
        console.log(this.props.father.styles);
    }

    render() {
        var otherStyles = this.props.data['other_possible_styles'];
        return (
            <div className='card' style={{width:`${this.props.data['progression'].length*75}px`}}>
                <div style={{textAlign:'center'}}>
                    <Title level={3} style={{color:'gray', marginBottom:'0px'}} >
                        <a onClick={this.play} id='b' href={true}>PROGRESSION</a>
                    </Title>
                    {/* <p style={{marginTop:'5px', color:'gray', fontSize:'10px'}}><span style={{marginRight:'17px'}}>———</span>Score: {this.props.data['score']}<span style={{marginLeft:'17px'}}>———</span></p> */}
                </div>
                
                <div style={{width:'50%', float:'left', marginTop:'20px'}}>
                    <Paragraph style={{fontSize:'10px',color:'gray', marginLeft:'12px'}}>Style</Paragraph>
                    <Select defaultValue={this.props.data['style']} autoFocus={false} bordered={false} style={{fontSize:'25px'}} onChange={(value) => this.handleStyleChange(value)}>
                        {style.map((item) => {
                            return <Option value={item.value} disabled={!contains(otherStyles, item.value)}>{item.ui}</Option>
                        })}
                    </Select>
                    {/* <Paragraph style={{fontSize:'10px',color:'gray', marginLeft:'12px', marginTop:'20px'}}>Rhythm</Paragraph>
                    <Select defaultValue={this.props.data['rhythm']} autoFocus={false} bordered={false} style={{fontSize:'25px'}}>
                        {rhythm.map((item) => {
                                return <Option value={item.value} >{item.ui}</Option>
                        })}
                    </Select> */}
                </div>
                {/* <div style={{width:'50%', float:'right', marginTop:'20px'}}>
                    <Paragraph style={{fontSize:'10px',color:'gray', marginLeft:'12px'}}>Pattern</Paragraph>
                    <Select defaultValue={this.props.data['pattern']} autoFocus={false} bordered={false} style={{fontSize:'25px'}}>
                        {pattern.map((item) => {
                                return <Option value={item.value}>{item.ui}</Option>
                        })}
                    </Select>
                    <Paragraph style={{fontSize:'10px',color:'gray', marginLeft:'12px', marginTop:'20px'}}>Cycle</Paragraph>
                    <Select defaultValue={this.props.data['cycle']} autoFocus={false} bordered={false} style={{fontSize:'25px'}}>
                        {cycle.map((item) => {
                                return <Option value={item.value}>{item.ui}</Option>
                        })}
                    </Select>
                    <Paragraph style={{fontSize:'10px',color:'gray', marginLeft:'12px', marginTop:'20px'}}>Position</Paragraph>
                    <Select defaultValue={this.props.data['position']} autoFocus={false} bordered={false} style={{fontSize:'25px'}}>
                        {position.map((item) => {
                                return <Option value={item.value}>{item.ui}</Option>
                        })}
                    </Select>
                </div> */}
                <div style={{textAlign:'center', marginTop:'120px', backgroundColor:'#fff7e6', borderRadius:'10px'}}>

                    {this.props.data['progression'].length === 8 ? 
                    <div>
                    <Title level={3} style={{fontSize:'20px'}}>
                    <Divider type='vertical' style={{backgroundColor:'black', marginRight:'20px'}}/>
                    {this.props.cheat===1?'C':'A'}
                    <Divider type='vertical' style={{backgroundColor:'black', marginRight:'20px', marginLeft:'20px'}}/>
                    {this.props.cheat===1?'A':'D'}
                    <Divider type='vertical' style={{backgroundColor:'black',  marginRight:'20px', marginLeft:'20px'}}/>
                    {this.props.cheat===1?'D':'Em'}
                    <Divider type='vertical' style={{backgroundColor:'black', marginRight:'20px', marginLeft:'20px'}}/>
                    {this.props.cheat===1?'Em':'C'}
                    <Divider type='vertical' style={{backgroundColor:'black', marginRight:'20px', marginLeft:'20px'}}/>
                    {this.props.cheat===1?'C':'A'}
                    <Divider type='vertical' style={{backgroundColor:'black', marginRight:'20px', marginLeft:'20px'}}/>
                    {this.props.cheat===1?'A':'D'}
                    <Divider type='vertical' style={{backgroundColor:'black',  marginRight:'20px', marginLeft:'20px'}}/>
                    {this.props.cheat===1?'D':'Em'}
                    <Divider type='vertical' style={{backgroundColor:'black', marginRight:'20px', marginLeft:'20px'}}/>
                    {this.props.cheat===1?'Em':'C'}
                    <Divider type='vertical' style={{backgroundColor:'black', marginLeft:'20px'}}/>
                    </Title>
                    </div>:<div>
                    <Title level={3} style={{fontSize:'20px'}}>
                    <Divider type='vertical' style={{backgroundColor:'black', marginRight:'20px'}}/>
                    A
                    <Divider type='vertical' style={{backgroundColor:'black', marginRight:'20px', marginLeft:'20px'}}/>
                    D
                    <Divider type='vertical' style={{backgroundColor:'black',  marginRight:'20px', marginLeft:'20px'}}/>
                    Em
                    <Divider type='vertical' style={{backgroundColor:'black', marginRight:'20px', marginLeft:'20px'}}/>
                    C
                    <Divider type='vertical' style={{backgroundColor:'black', marginLeft:'20px'}}/>
                    </Title>
                    </div>}
                </div>
                <Button type='dashed' block style={{marginTop:'180px'}}>Make All Subject To Current</Button>
            </div>
        )
    }
}
function contains(arr, obj){
    var i = arr.length;
    while (i--) {
        if (arr[i] === obj) {
            return true;
        }
    }
    return false;
}