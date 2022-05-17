import './App.css';
import MainInterface from './components/MainInterface';
import pianoRoll from 'pianoroll/build/PianoRoll';


function App() {
  return (
    <div>
      <div className="App">
        <MainInterface/>
      </div>
      <div style={{minHeight:'100px', textAlign:'center', backgroundColor:'#002766'}}>
          <h4 style={{color:'white', paddingTop:'30px'}}>Interface for AccoMontage2</h4>
      </div>
    </div>
  );
}
export default App;
