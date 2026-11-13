import { useState, useEffect, useRef } from 'react'
import { Card, Button, Input, Space, message, Tag, Alert, Divider } from 'antd'
import { SendOutlined, QrcodeOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons'
import api from '../api.js'

export default function Bind() {
  const [status, setStatus] = useState({ bound: false })
  const [code, setCode] = useState('')
  const [wxId, setWxId] = useState('wx_test_01')
  const [text, setText] = useState('')
  const [convo, setConvo] = useState([])
  const [sending, setSending] = useState(false)
  const boxRef = useRef(null)

  const load = async () => setStatus(await api.get('/bind/status'))
  useEffect(() => { load() }, [])

  const gen = async () => {
    const r = await api.post('/bind/code')
    setCode(r.bind_code)
  }
  const unbind = async () => { await api.post('/bind/unbind'); message.success('已解绑'); load() }

  const send = async (msg) => {
    const payload = msg !== undefined ? msg : text
    if (!payload) { message.warning('请输入消息'); return }
    setSending(true)
    try {
      await api.post('/gateway/simulate', { wx_id: wxId, text: payload })
      const out = await api.get('/gateway/outbox', { params: { wx_id: wxId } })
      setConvo(c => [
        ...c, { dir: 'in', text: payload },
        ...out.map(m => ({ dir: 'out', text: m.text }))
      ])
      setText('')
      load()
    } catch (e) { message.error(e.message) }
    finally { setSending(false) }
  }

  useEffect(() => { boxRef.current?.scrollTo(0, 999999) }, [convo])

  const quick = [
    { label: '/status', cmd: '/status' },
    { label: '/help', cmd: '/help' },
    { label: '危险操作示例', cmd: 'del /q C:\\Users\\86189\\Desktop\\myworkbench\\workspace\\test_del.txt' },
  ]

  return (
    <div>
      <h2>微信绑定</h2>
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            绑定状态：
            {status.bound
              ? <Tag color="green">已绑定 {status.wx_id}</Tag>
              : <Tag color="orange">未绑定</Tag>}
          </div>
          <Space>
            <Button type="primary" icon={<QrcodeOutlined />} onClick={gen}>生成绑定码</Button>
            {status.bound && <Button danger onClick={unbind}>解绑</Button>}
          </Space>
          {code && (
            <Alert type="success" showIcon
              message={`绑定码：${code}（10 分钟内有效）`}
              description="在下方「模拟微信」里，把微信 ID 填成你自己的 ID，然后把这个绑定码作为消息发给机器人即可完成绑定（真实环境：用手机微信把绑定码发给机器人）。" />
          )}
        </Space>
      </Card>

      <Card title="📱 模拟微信（本地测试通道，无需真实微信）">
        <Alert type="info" showIcon style={{ marginBottom: 12 }}
          message="这是本地测试通道：模拟「手机微信 → 机器人」的完整链路。绑定、发指令、二次确认都在这里验证；接入真实微信后（企业微信/WeChatFerry）体验一致。" />
        <Space style={{ marginBottom: 12 }}>
          <span>微信 ID：</span>
          <Input value={wxId} onChange={e => setWxId(e.target.value)} style={{ width: 180 }} />
        </Space>
        <div style={{
          border: '1px solid #eee', borderRadius: 8, height: 320, overflowY: 'auto',
          padding: 12, marginBottom: 12, background: '#fafafa'
        }} ref={boxRef}>
          {convo.length === 0 && (
            <div style={{ color: '#bbb', textAlign: 'center', marginTop: 120 }}>
              还没有对话，先发送一条消息试试
            </div>
          )}
          {convo.map((m, i) => (
            <div key={i} style={{
              display: 'flex', justifyContent: m.dir === 'in' ? 'flex-end' : 'flex-start',
              marginBottom: 8
            }}>
              <div style={{
                maxWidth: '75%', padding: '8px 12px', borderRadius: 8, whiteSpace: 'pre-wrap',
                background: m.dir === 'in' ? '#1677ff' : '#fff',
                color: m.dir === 'in' ? '#fff' : '#333',
                border: m.dir === 'in' ? 'none' : '1px solid #e5e5e5'
              }}>
                {m.text}
              </div>
            </div>
          ))}
        </div>
        <Space.Compact style={{ width: '100%' }}>
          <Input placeholder="输入指令，如 /status、/help、/run dir" value={text}
            onChange={e => setText(e.target.value)} onPressEnter={() => send()} />
          <Button type="primary" icon={<SendOutlined />} loading={sending} onClick={() => send()}>发送</Button>
        </Space.Compact>
        <Divider style={{ margin: '12px 0' }}>快捷操作</Divider>
        <Space wrap>
          {quick.map(q => (
            <Button key={q.label} onClick={() => send(q.cmd)}>{q.label}</Button>
          ))}
          <Button type="primary" ghost icon={<CheckOutlined />} onClick={() => send('确认')}>确认（二次确认）</Button>
          <Button danger ghost icon={<CloseOutlined />} onClick={() => send('取消')}>取消</Button>
        </Space>
      </Card>
    </div>
  )
}
