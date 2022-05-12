import React, { Component } from 'react'
import ParaSetter from '../ParaSetter'
import Generator from '../Generator'
import { Steps } from 'antd';
import PubSub from 'pubsub-js'
import { Typography, Divider } from 'antd';
import './index.css'

const { Step } = Steps;
const { Title } = Typography;

const stepText = {
    0:{
        0:{ title:'Set Parameters', des:'Upload melodies.'},
        1:{ title:'Generate Progressions', des:'Choose the best.'} 
    },
    1:{
        0:{ title:'Set Parameters', des:'Upload melodies.'},
        1:{ title:'Generate Progressions', des:'Choose the best.'}
    }
}

function toTop(){
    var scrollToptimer = setInterval(function () {
        var top = document.body.scrollTop || document.documentElement.scrollTop;
        var speed = top / 4;
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

export default class MainInterface extends Component {

    constructor(){
        super()
        this.state = {
            step:0,
            values:[]
        }
        PubSub.subscribe('submit', this.onSubmit)
    }

    onSubmit = (name, msg) => {
        this.setState({
            step:1,
            values:msg
        })
        toTop();
    }

    render() {
        return (
            <div>
                <div className='head'>
                    <a href='/'><Title level={1} style={{float:'left', marginTop:'0px', fontSize:'55px'}} className='title'><span style={{color:'#1890FF'}}>A</span>uto <span style={{color:'#1890FF'}}>C</span>hord <span style={{color:'#1890FF'}}>G</span>enerator</Title></a>
                    <Steps current={this.state.step} style={{maxWidth:'500px', float:'right', marginTop:'10px'}}>
                        <Step title={stepText[this.state.step]['0'].title} description={stepText[this.state.step]['0'].des} >
                        </Step>
                        <Step title={stepText[this.state.step]['1'].title} description={stepText[this.state.step]['1'].des} />
                    </Steps>
                </div>
                <Divider style={{marginBottom:'50px', backgroundColor:'#1890FF'}}/ >
                {this.state.step === 0 ? <ParaSetter></ParaSetter> : <Generator values={this.state.values}></Generator>}
                
            </div>
        )
    }
}
