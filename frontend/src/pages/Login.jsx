import { useState } from 'react'
import { Card, Form, Input, Button, Tabs, message } from 'antd'
import { RobotOutlined } from '@ant-design/icons'
import api from '../api.js'

export default function Login({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [loading, setLoading] = useState(false)

  const onFinish = async (v) => {
    setLoading(true)
    try {
      const r = await api.post(mode === 'login' ? '/auth/login' : '/auth/register', v)
      localStorage.setItem('mw_token', r.access_token)
      localStorage.setItem('mw_user', JSON.stringify({
        username: r.username, role: r.role, user_id: r.user_id
      }))
      message.success('欢迎，' + r.username)
      window.location.hash = '#/models'
      onLogin()
    } catch (e) {
      message.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: 'linear-gradient(135deg,#111827,#1f2937)'
    }}>
      <Card style={{ width: 380 }}>
        <div style={{ textAlign: 'center', marginBottom: 12 }}>
          <RobotOutlined style={{ fontSize: 40, color: '#1677ff' }} />
          <h2 style={{ margin: '8px 0 0' }}>MyWorkbench</h2>
          <div style={{ color: '#888' }}>个人 AI 工作台</div>
        </div>
        <Tabs activeKey={mode} onChange={setMode} centered items={[
          { key: 'login', label: '登录' },
          { key: 'register', label: '注册' },
        ]} />
        <Form onFinish={onFinish} layout="vertical">
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input placeholder="用户名" autoComplete="username" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password placeholder="密码（至少 6 位）" autoComplete="current-password" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={loading}>
            {mode === 'login' ? '登录' : '注册并登录'}
          </Button>
        </Form>
        <div style={{ marginTop: 12, color: '#aaa', fontSize: 12, textAlign: 'center' }}>
          默认管理员：admin / admin123456
        </div>
      </Card>
    </div>
  )
}
