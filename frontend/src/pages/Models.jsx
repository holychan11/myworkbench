import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Modal, Form, Input, Select, InputNumber, Switch, Space,
  message, Popconfirm, Tag } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import api from '../api.js'

const PROVIDERS = [
  { value: 'deepseek', label: 'DeepSeek', url: 'https://api.deepseek.com/v1' },
  { value: 'zhipu', label: '智谱 GLM', url: 'https://open.bigmodel.cn/api/paas/v4' },
  { value: 'openai', label: 'OpenAI', url: 'https://api.openai.com/v1' },
  { value: 'moonshot', label: 'Kimi (月之暗面)', url: 'https://api.moonshot.cn/v1' },
  { value: 'qwen', label: '通义千问', url: 'https://dashscope.aliyuncs.com/compatible-mode/v1' },
  { value: 'custom', label: '自定义（任意 OpenAI 兼容端点）', url: '' },
]

export default function Models() {
  const [rows, setRows] = useState([])
  const [open, setOpen] = useState(false)
  const [testing, setTesting] = useState(null)
  const [form] = Form.useForm()

  const load = useCallback(async () => {
    setRows(await api.get('/models'))
  }, [])
  useEffect(() => { load().catch(e => message.error(e.message)) }, [load])

  const onProviderChange = (v) => {
    const p = PROVIDERS.find(x => x.value === v)
    if (p && p.url) form.setFieldValue('base_url', p.url)
    form.setFieldValue('provider', v)
  }

  const submit = async () => {
    const v = await form.validateFields()
    await api.post('/models', v)
    message.success('已添加模型')
    setOpen(false)
    form.resetFields()
    load()
  }

  const del = async (id) => { await api.delete('/models/' + id); load() }
  const setDefault = async (id) => { await api.post('/models/' + id + '/default'); load() }
  const test = async (id) => {
    setTesting(id)
    try {
      const r = await api.post('/models/' + id + '/test')
      if (r.ok) message.success('连通正常：' + r.reply)
      else message.error('调用失败：' + r.reply)
    } catch (e) { message.error(e.message) }
    finally { setTesting(null) }
  }

  const columns = [
    { title: '名称', dataIndex: 'display_name' },
    { title: '厂商', dataIndex: 'provider', render: v => <Tag>{v}</Tag> },
    { title: '端点', dataIndex: 'base_url', ellipsis: true },
    { title: '模型名', dataIndex: 'default_model' },
    { title: 'API Key', dataIndex: 'api_key_masked' },
    { title: '默认', dataIndex: 'is_default', render: v => v ? <Tag color="green">默认</Tag> : '' },
    {
      title: '操作', render: (_, r) => (
        <Space>
          <Button size="small" loading={testing === r.id} onClick={() => test(r.id)}>测试</Button>
          <Button size="small" onClick={() => setDefault(r.id)}>设为默认</Button>
          <Popconfirm title="删除该模型？" onConfirm={() => del(r.id)}>
            <Button size="small" danger>删除</Button>
          </Popconfirm>
        </Space>
      )
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>模型管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>添加模型</Button>
      </div>
      <Table rowKey="id" dataSource={rows} columns={columns} pagination={false}
        locale={{ emptyText: '尚未添加模型，点击右上角「添加模型」，填 API Key 即可使用' }} />

      <Modal title="添加模型" open={open} onOk={submit} onCancel={() => setOpen(false)}
        destroyOnClose>
        <Form form={form} layout="vertical"
          initialValues={{ provider: 'deepseek', temperature: 0.7, is_default: false }}>
          <Form.Item name="display_name" label="显示名称" rules={[{ required: true }]}>
            <Input placeholder="如 DeepSeek-V3" />
          </Form.Item>
          <Form.Item name="provider" label="厂商" rules={[{ required: true }]}>
            <Select options={PROVIDERS.map(p => ({ value: p.value, label: p.label }))}
              onChange={onProviderChange} />
          </Form.Item>
          <Form.Item name="base_url" label="API 端点 (base_url)" rules={[{ required: true }]}>
            <Input placeholder="https://..." />
          </Form.Item>
          <Form.Item name="api_key" label="API Key（加密存储，前端永不回显明文）" rules={[{ required: true }]}>
            <Input.Password placeholder="sk-..." />
          </Form.Item>
          <Form.Item name="default_model" label="模型名" rules={[{ required: true }]}>
            <Input placeholder="如 deepseek-chat / glm-4-plus / gpt-4o" />
          </Form.Item>
          <Form.Item name="temperature" label="温度">
            <InputNumber min={0} max={2} step={0.1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="is_default" label="设为默认模型" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
