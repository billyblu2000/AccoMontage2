import React, { Component } from 'react'
import {
    Form,
  Select,
  InputNumber,
  Button,
  Upload,
  Divider,
  Space
} from 'antd';
import { InboxOutlined, PlusOutlined,MinusCircleOutlined } from '@ant-design/icons';
import { server, meter, tonic, style, mode, getCookie } from '../../utils';
import PubSub from 'pubsub-js';
const { Option } = Select;

const formItemLayout = {
    labelCol: { span: 6 },
    wrapperCol: { span: 14 },
};

export default class ParaSetter extends Component {

    onFinish = (values) => {
        server(`/api/chorderator_back_end/generate?sessionID=${getCookie("sessionID")}`, this, null, 'post', values)
        PubSub.publish('submit', values)
    }

    normFile = (e) => {
        console.log('Upload event:', e);
        if (Array.isArray(e)) {
          return e;
        }
        return e && e.fileList;
    };

    add = () => {

    }

    render(){
        return (
            <div>
                <Form
                name="validate_other"
                {...formItemLayout}
                onFinish={this.onFinish}
                initialValues={{
                    tonic:'C',
                    meter:'4/4',
                    mode:'maj',
                    style:'pop_standard',
                    tempo:120
                }}
                >
                <Divider orientation="left">Set Melody</Divider>
                <Form.Item 
                    label="Upload Melody MIDI"
                    name="midi" 
                    valuePropName="fileList" 
                    getValueFromEvent={this.normFile} 
                    hasFeedback
                    rules={[
                    {
                        required: true,
                        message: 'Please upload your melody MIDI!',
                    },
                    ]}
                >
                    <Upload.Dragger name="midi" action="/api/chorderator_back_end/upload_melody" accept='.mid' maxCount={1} >
                        <p className="ant-upload-drag-icon">
                        <InboxOutlined />
                        </p>
                        <p className="ant-upload-text">Click or drag MIDI file to this area to upload</p>
                    </Upload.Dragger>
                </Form.Item>

                <Divider orientation="left">Set Phrase</Divider>
                <Form.Item name="phrases" label='Phrases'>
                <Form.List name="phrases">
                    {(fields, { add, remove }) => (
                    <>
                        {fields.map(field => (
                        <Space key={field.key} align="baseline" size={120} >
                            <Form.Item
                            noStyle
                            shouldUpdate={(prevValues, curValues) =>
                                prevValues.area !== curValues.area || prevValues.sights !== curValues.sights
                            }
                            >
                            {() => (
                                <Form.Item
                                {...field}
                                label="Start"
                                name={[field.name, 'start']}
                                fieldKey={[field.fieldKey, 'start']}
                                rules={[{ required: true, message: 'Missing start' }]}
                                >
                                <InputNumber style={{width:'160%'}}/>
                                </Form.Item>
                            )}
                            </Form.Item>
                            <Form.Item
                            {...field}
                            label="End"
                            name={[field.name, 'end']}
                            fieldKey={[field.fieldKey, 'end']}
                            rules={[{ required: true, message: 'Missing end' }]}
                            >
                            <InputNumber style={{width:'160%'}}/>
                            </Form.Item>

                            <MinusCircleOutlined onClick={() => remove(field.name)} />
                        </Space>
                        ))}

                        <Form.Item>
                        <Button type="dashed" onClick={() => add()} icon={<PlusOutlined />}>
                            Add Phrase
                        </Button>
                        </Form.Item>
                    </>
                    )}
                </Form.List>
                </Form.Item>

                <Divider orientation="left">Set Meta</Divider>
                
                <Form.Item name="tonic" label="Tonic" hasFeedback
                    rules={[{ required: true, message: 'Please select a tonic!' }]}
                >
                    <Select placeholder="Please select a tonic">
                    {tonic.map((item) => {
                        return <Option value={item}>{item}</Option>
                    })}
                    </Select>
                </Form.Item>

                <Form.Item name="mode" label="Mode" hasFeedback
                    rules={[{ required: true, message: 'Please select a mode!' }]}
                >
                    <Select placeholder="Please select a mode">
                    {mode.map((item) => {
                        return <Option value={item.value}>{item.ui}</Option>
                    })}
                    </Select>
                </Form.Item>

                <Form.Item name="meter" label="Meter" hasFeedback
                    rules={[{ required: true, message: 'Please select a meter!' }]}
                >
                    <Select placeholder="Please select a meter">
                    {meter.map((item) => {
                        return <Option value={item.value}>{item.ui}</Option>
                    })}
                    </Select>
                </Form.Item>

                <Divider orientation="left">Set Style</Divider>

                <Form.Item name="style" label="Output Style" hasFeedback
                    rules={[{ required: true, message: 'Please select a style!' }]}
                >
                    <Select placeholder="Please select a style">
                    {style.map((item) => {
                        return <Option value={item.value}>{item.ui}</Option>
                    })}
                    </Select>
                </Form.Item>

                <Form.Item
                    wrapperCol={{
                    span: 12,
                    offset: 6,
                    }}
                >
                    <Button type="primary" htmlType="submit">
                    Next
                    </Button>
                </Form.Item>
                </Form>
                <div style={{minHeight:'150px'}}></div>
            </div>
        )
    }
}
