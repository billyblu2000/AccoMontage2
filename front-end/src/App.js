import './App.css';
import MainInterface from './components/MainInterface';
import { Button, Modal, Tabs, Typography } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons'
import React from 'react';

const help1 = (
  <div style={{paddingLeft:'5%', paddingRight:'5%'}}>
    <Typography.Title level={4}>What are required before generation?</Typography.Title>
    <Typography.Title level={5}>Melody</Typography.Title>
    <Typography.Paragraph>AccoMonatage2 needs a leading melody to generate accompaniment. Please drag the melody to the box or click to upload your melody piece. Melody must be a single-track MIDI file (or multi-track with the melody piece at the first track).</Typography.Paragraph>
    <Typography.Title level={5}>Phrases (segmentation)</Typography.Title>
    <Typography.Paragraph>You must also specify the phrases of the uploaded melody. Each phrase has a name and a length. Phrases with the same name are considered as similar phrases when generating textures. Currently, the length of the phrases only supports 4-bar and 8-bar. Please make sure your melody can fit in the phrase structures.</Typography.Paragraph>
    <Typography.Title level={5}>{'Tonic & mode & meter'}</Typography.Title>
    <Typography.Paragraph>You must specify a tonic, mode, and meter for the melody. For example, a melody piece in C Major key and four fourths beat has tonic=C, mode=Major, meter=4/4. Note that currently only 4/4 is supported.</Typography.Paragraph>
    <Typography.Title level={5}>Chord style</Typography.Title>
    <Typography.Paragraph>The chord style control is optional. You can click on <Typography.Text code>Enable Chord Style Controlling</Typography.Text> to activate chord style control. Currently, there are 4 styles in total, AccoMonatage2 will tend to use the selected style to harmonize the melody (but not guaranteed).</Typography.Paragraph>
    <Typography.Title level={5}>Texture style</Typography.Title>
    <Typography.Paragraph>The texture style control is also optional. Five levels of rhythm density and voice number are available.</Typography.Paragraph>
  </div>
)
const help2 = (
  <div style={{paddingLeft:'5%', paddingRight:'5%'}}>
    <Typography.Title level={4}>When generating...</Typography.Title>
    <Typography.Paragraph>Please wait patiently, the generating process might take 1 minute. You can view the process on the left part.</Typography.Paragraph>
    <Typography.Title level={4}>After generated</Typography.Title>
    <Typography.Title level={5}>Listen and download</Typography.Title>
    <Typography.Paragraph>You may click to listen to the generated audio or download the generated MIDI file. You can aslo listen to the audio of each phrase separately by clicking the piano roll.</Typography.Paragraph>
    <Typography.Title level={5}>Change style and re-generate</Typography.Title>
    <Typography.Paragraph>The choosen chord style of each phrase is displayed. You can click on and choose a new style. Some styles may not be available. You can also change the texture style of the whole melody. Click on the button at the bottom to re-generate based on new styles.</Typography.Paragraph>
  </div>
)

const help3 = (
  <div style={{paddingLeft:'5%', paddingRight:'5%'}}>
    <Typography.Title level={5}>Why the generation result is not satisfying?</Typography.Title>
    <Typography.Paragraph>There might be multiple reasons. Please go through the following check list to improve the output result.</Typography.Paragraph>
    <Typography.Paragraph>
      <ul>
        <li><Typography.Text strong>Blank melody at the begining. </Typography.Text>AccoMontage2 marks the first bar of the melody as the begining of the first phrase. If your melody have a piece of blank at the begining and you are not willing to make it part of your phrase, please remove it (including anacrusis).</li>
        <li><Typography.Text strong>Melody is too sparse. </Typography.Text>AccoMontage2 generates only based on the melody. Please make sure the melody have enough notes for reference. Sparce melody might also produce dissatisfying results.</li>
        <li><Typography.Text strong>Melody not homophonic. </Typography.Text>AccoMontage2 prefers homophonic music. That is to say, the melody is expected to have at most one note playing at any moment.</li>
        <li><Typography.Text strong>Tempo too large or too small. </Typography.Text>In most cases, AccoMonatage2 will harmonize a bar with a single chord. If this is not your wish, you can modify the tempo to a suitable range (usually tempo between 70-120 will produce good results).</li>
        <li><Typography.Text strong>Wrong tonic/mode/meter. </Typography.Text>This might cause the algorithm to generate someting that is completely wrong.</li>
      </ul>
    </Typography.Paragraph>
    <Typography.Paragraph>If you are very sure that the above problem is already solved, you can also try other chord styles and texture styles, or even phrase structures (e.g., split an 8-bar phrase into two 4-bar phrases).</Typography.Paragraph>
    <Typography.Title level={5}>Why the generation fails?</Typography.Title>
    <Typography.Paragraph>Please make sure the phrase label is correct. Currently, a limitation is the melody cannot exceed the labeled phrases. Please make sure your last note is within the provided phrases. Other bugs please contact <a href={true}>anonymous@anonymous.com</a>.</Typography.Paragraph>
    <Typography.Title level={5}>Why the piano roll cannot show up?</Typography.Title>
    <Typography.Paragraph>Piano roll is supported by <a href='https://github.com/googlecreativelab/chrome-music-lab'>Chrome Music Lab</a>. If your region do not have access to Google, the piano roll might fails to render. We are also updating the technolody to overcome this predicament.</Typography.Paragraph>
  </div>
)

function App() {
  const [isModalVisible, setIsModalVisible] = React.useState(false)

  const closeModal = () => {
    setIsModalVisible(false)
  }

  return (
    <div>
      <Button shape='link' style={{ marginLeft: '92%', marginTop: '20px' }} onClick={() => setIsModalVisible(true)}><QuestionCircleOutlined />Help</Button>
      <div className="App">
        <MainInterface />
      </div>
      <div style={{ minHeight: '70px', textAlign: 'center', backgroundColor: '#003b76' }}>
        <h4 style={{ color: 'white', paddingTop: '20px' }}>Interface for AccoMontage2</h4>
      </div>
      <Modal title="AccoMonatage2 GUI Help" visible={isModalVisible} width={800} onOk={closeModal} onCancel={closeModal} footer={[<Button type="primary" onClick={closeModal}>Ok</Button>]}>
        <Tabs defaultActiveKey="1" centered>
          <Tabs.TabPane tab="Set Parameters Page" key="1">
            {help1}
          </Tabs.TabPane>
          <Tabs.TabPane tab="Generating Page" key="2">
            {help2}
          </Tabs.TabPane>
          <Tabs.TabPane tab={'Other Q&A'} key="3">
            {help3}
          </Tabs.TabPane>
        </Tabs>
      </Modal>
    </div>
  );
}
export default App;
