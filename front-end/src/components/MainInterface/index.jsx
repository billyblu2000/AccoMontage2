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

    0:{ title:'Set Parameters', des:'Upload melodies.'},
    1:{ title:'Generate Accompaniment', des:'Choose the best.'} 

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
                    <a href='/accomontage2-online'><Title level={1} style={{float:'left', marginTop:'0px', fontSize:'55px'}} className='title'><span style={{color:'#003b76'}}>A</span>cco<span style={{color:'#003b76'}}>M</span>ontage<span style={{color:'#003b76'}}>2</span></Title></a>
                    <Steps current={this.state.step} style={{maxWidth:'500px', float:'right', marginTop:'10px', marginBottom:'20px'}}>
                        <Step title={stepText['0'].title} description={stepText['0'].des} >
                        </Step>
                        <Step title={stepText['1'].title} description={stepText['1'].des} />
                    </Steps>
                </div>
                <Divider style={{marginBottom:'50px', backgroundColor:'#003b76'}}/ >
                {this.state.step === 0 ? <ParaSetter></ParaSetter> : <Generator values={this.state.values}></Generator>}
            </div>
        )
    }
}
