import { message } from "antd";
import axios from "axios";

// export const env = 'dev';
export const env = 'staging';
export const prodServer = 'https://billyyi.top/api/chorderator_back_end'
export const publicServer = 'http://127.0.0.1:5000/api';
export const privateServer = 'http://localhost:3000/api';
var comp = env === 'dev' ? privateServer : publicServer;
export const myServer = env === 'prod' ? prodServer : comp;

export function server(add, obj, v, method='get', postData=null, callback=null) {
    if (method === 'get'){
        axios.get(myServer + add).then(
            response => { 
                if (callback !== null){
                    callback(response.data);
                }
                obj.setState({
                    [v]:response.data
                })
            },
            error => { 
                message.warn({content:'Sorry, something wrong happened to the server!', key:'message'})
                console.log(error)
            },
        )
    }
    else{
        axios.post(myServer + add, postData).then(
            response => { 
                if (callback !== null){
                    callback(response.data);
                }
                obj.setState({
                    [v]:response.data
                })
            },
            error => { 
                message.warn({content:'Sorry, something wrong happened to the server!', key:'message'})
                console.log(error)
            },
        )
    }
};
export function getCookie(name){
    var prefix = name + "="
    var start = document.cookie.indexOf(prefix)
 
    if (start === -1) {
        return null;
    }
 
    var end = document.cookie.indexOf(";", start + prefix.length)
    if (end === -1) {
        end = document.cookie.length;
    }
 
    var value = document.cookie.substring(start + prefix.length, end)
    return unescape(value);
}
export const meter = [
    { value:'4/4', ui:'4/4' },
    { value:'3/4', ui:'3/4' },
]
export const mode = [
    { value:'maj', ui:'Major' },
    { value:'min', ui:'Minor' },
]
export const tonic = [ 
    'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F',
    'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'
]
export const progressionStyle = [
    { value:'emotional', ui:'Emotional' },
    { value:'pop', ui:'Pop' },
    { value:'dark', ui:'Dark' },
    { value:'edm', ui:'EDM' },
    { value:'r&b', ui:'R&B' },
]
export const chordStyle = [
    { value:'standard', ui:'Standard' },
    { value:'emotional', ui:'Emotional' },
    { value:'classy', ui:'Classy' },
    { value:'root-note', ui:'Root Note' },
    { value:'cluster', ui:'Cluster' },
    { value:'power-chord', ui:'Power Chord' },
    { value:'power-octave', ui:'Power Octave' },
    { value:'full-octave', ui:'Full Octave' },
    { value:'first-inversion', ui:'First Inversion' },
    { value:'second-inversion', ui:'Second Inversion' },
    { value:'seventh', ui:'Seventh' },
    { value:'sus2', ui:'Sus2' },
    { value:'sus4', ui:'Sus4' },
]
export const style = [
    { value:'pop_standard', ui:'Pop Standard' },
    { value:'pop_complex', ui:'Pop Complex' },
    { value:'dark', ui:'Dark' },
    { value:'r&b', ui:'R&B' },
]
export const rhythm = [
    { value:'fast', ui:'Fast' },
    { value:'slow', ui:'Slow' },
]
export const cycle = [
    { value:'4m', ui:'Less than 4' },
    { value:'4', ui:'4' },
    { value:'8', ui:'8' },
    { value:'12', ui:'12' },
    { value:'16', ui:'16' },
    { value:'16p', ui:'Greater than 16' },
]
export const pattern = [
    { value:'2564', ui:'ii-V-vi-IV' },
    { value:'1536', ui:'I-V-iii-vi' },
    { value:'4165', ui:'IV-I-vi-V' },
    { value:'4265', ui:'IV-ii-vi-V' },
    { value:'4561', ui:'IV-V-vi-I' },
    { value:'6345', ui:'vi-III-IV-V' },
]
export const position = [
    { value:'verse', ui:'Verse' },
    { value:'chorus', ui:'Chorus' },
    { value:'intro', ui:'Intro' },
    { value:'transition', ui:'Transition' },
    { value:'interlude', ui:'Interlude' },
    { value:'bridge', ui:'Bridge' },
    { value:'outro', ui:'Outro' },
    { value:null, ui:'unknown'}
]