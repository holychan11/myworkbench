import { useState, useEffect } from 'react'
import { Tabs, Table, Tag, message } from 'antd'
import api from '../api.js'

const STATUS_COLOR = {
  ok: 'green', approved: 'green', failed: 'red', rejected: 'red', pending: 'gold'
}

function Users() {
  const [rows, setRows] = useState([])
  useEffect(() => {
    api.get('/admin/users').then(setRows).catch(e => message.error(e.message))
  }, [])
  const cols = [
    { title: 'ID', dataIndex: 'id', ellipsis: true },
    { title: '用户名', dataIndex: 'username' },
    { title: '角色', dataIndex: 'role', render: v => <Tag color={v === 'admin' ? 'gold' : 'green'}>{v}</Tag> },
    { title: '状态', dataIndex: 'is_active', render: v => v ? '启用' : '停用' },
    { title: '注册时间', dataIndex: 'created_at' },
  ]
  return <Table rowKey="id" dataSource={rows} columns={cols} pagination={{ pageSize: 20 }} />
}

function AllLogs() {
  const [rows, setRows] = useState([])
  useEffect(() => {
    api.get('/admin/logs').then(setRows).catch(e => message.error(e.message))
  }, [])
  const cols = [
    { title: 'ID', dataIndex: 'id', width: 70 },
    { title: '用户', dataIndex: 'user_id', ellipsis: true },
    { title: '类型', dataIndex: 'kind', width: 90 },
    { title: '命令', dataIndex: 'cmd', ellipsis: true },
    { title: '状态', dataIndex: 'status', width: 90,
      render: v => <Tag color={STATUS_COLOR[v] || 'default'}>{v}</Tag> },
    { title: '时间', dataIndex: 'created_at', width: 180 },
  ]
  return <Table rowKey="id" dataSource={rows} columns={cols} pagination={{ pageSize: 20 }} />
}

export default function Admin() {
  return (
    <div>
      <h2>系统管理</h2>
      <Tabs items={[
        { key: 'users', label: '用户', children: <Users /> },
        { key: 'logs', label: '全量审计日志', children: <AllLogs /> },
      ]} />
    </div>
  )
}
