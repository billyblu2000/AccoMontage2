import './App.css';
import MainInterface from './components/MainInterface'

function App() {
  return (
    <div>
      <div className="App">
        <MainInterface/>
      </div>
      <div style={{minHeight:'100px', textAlign:'center', backgroundColor:'#002766'}}>
          <h4 style={{color:'white', paddingTop:'30px'}}>Interface by Billy and Johnny</h4>
      </div>
    </div>
  );
}
export default App;
