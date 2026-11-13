import { useState, useEffect } from 'react'
import { Table, Tag, message } from 'antd'
import api from '../api.js'

const RISK_COLOR = { safe: 'green', risky: 'orange', forbidden: 'red' }
const STATUS_COLOR = {
  ok: 'green', approved: 'green', failed: 'red', rejected: 'red',
  pending: 'gold', timed_out: 'default'
}

export default function Logs() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/logs')
      .then(setRows)
      .catch(e => message.error(e.message))
      .finally(() => setLoading(false))
  }, [])

  const columns = [
    { title: 'ID', dataIndex: 'id', width: 70 },
    { title: '类型', dataIndex: 'kind', width: 90, render: v => <Tag>{v}</Tag> },
    { title: '命令/内容', dataIndex: 'cmd', ellipsis: true },
    { title: '风险', dataIndex: 'risk', width: 80,
      render: v => v ? <Tag color={RISK_COLOR[v]}>{v}</Tag> : '' },
    { title: '状态', dataIndex: 'status', width: 90,
      render: v => <Tag color={STATUS_COLOR[v] || 'default'}>{v}</Tag> },
    { title: '结果', dataIndex: 'result', ellipsis: true },
    { title: '时间', dataIndex: 'created_at', width: 180 },
  ]

  return (
    <div>
      <h2>执行日志</h2>
      <Table rowKey="id" dataSource={rows} columns={columns} loading={loading}
        pagination={{ pageSize: 20 }} />
    </div>
  )
}
