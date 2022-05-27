import React, { Component } from 'react'
import { Typography, Select, Divider, Button } from 'antd'
import { style } from '../../utils';
import './index.css'

const { Title, Paragraph } = Typography;
const { Option } = Select;

export default class ChordProgression extends Component {

    state = {
        style: this.props.style
    }

    handleStyleChange = (value) => {
        var prevStyles = this.props.father.state.styles;
        prevStyles[this.props.index] = value;
        this.props.father.setState({styles:prevStyles})
    }

    static getDerivedStateFromProps(nextProps, prevState){
        return {style: nextProps.style}
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
                </div>
                <iframe title={`pianoroll-${this.props.data['midi_name']}`} src={`/accomontage2/pianoroll/player.html#midi/${this.props.data['midi_name']}`} style={{width:'100%', height:'150px', marginTop:"20px", paddingLeft:'20px', paddingRight:'20px', border:'0px'}}></iframe>
                <Button type='dashed' block style={{ marginTop: '20px' }} onClick={() => this.props.father.tryChangeAllStyle(this.state.style)}>Change all styles to current style</Button>
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