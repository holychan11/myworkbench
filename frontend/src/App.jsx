import { useState } from 'react'
import { HashRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Button, Space, Tag } from 'antd'
import {
  RobotOutlined, ApiOutlined, WechatOutlined, LineChartOutlined,
  FileTextOutlined, SettingOutlined, LogoutOutlined
} from '@ant-design/icons'
import Login from './pages/Login.jsx'
import Models from './pages/Models.jsx'
import Bind from './pages/Bind.jsx'
import Stock from './pages/Stock.jsx'
import Logs from './pages/Logs.jsx'
import Admin from './pages/Admin.jsx'

const { Sider, Header, Content } = Layout

function Shell() {
  const nav = useNavigate()
  const loc = useLocation()
  const user = JSON.parse(localStorage.getItem('mw_user') || '{}')
  const items = [
    { key: '/models', icon: <ApiOutlined />, label: '模型管理' },
    { key: '/bind', icon: <WechatOutlined />, label: '微信绑定' },
    { key: '/stock', icon: <LineChartOutlined />, label: 'A股分析' },
    { key: '/logs', icon: <FileTextOutlined />, label: '执行日志' },
  ]
  if (user.role === 'admin') {
    items.push({ key: '/admin', icon: <SettingOutlined />, label: '系统管理' })
  }
  const selected = '/' + (loc.pathname.split('/')[1] || 'models')

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={200}>
        <div style={{ color: '#fff', padding: '18px 16px', fontSize: 16, fontWeight: 600 }}>
          <RobotOutlined /> MyWorkbench
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={[selected]} items={items}
          onClick={({ key }) => nav(key)} />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', display: 'flex', justifyContent: 'flex-end',
          alignItems: 'center', padding: '0 24px' }}>
          <Space>
            <Tag color="blue">{user.username}</Tag>
            <Tag color={user.role === 'admin' ? 'gold' : 'green'}>
              {user.role === 'admin' ? '管理员' : '用户'}
            </Tag>
            <Button icon={<LogoutOutlined />} onClick={() => {
              localStorage.removeItem('mw_token')
              localStorage.removeItem('mw_user')
              window.location.reload()
            }}>退出</Button>
          </Space>
        </Header>
        <Content style={{ margin: 20 }}>
          <Routes>
            <Route path="/models" element={<Models />} />
            <Route path="/bind" element={<Bind />} />
            <Route path="/stock" element={<Stock />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="*" element={<Navigate to="/models" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem('mw_token'))
  if (!authed) return <Login onLogin={() => setAuthed(true)} />
  return (
    <HashRouter>
      <Shell />
    </HashRouter>
  )
}
