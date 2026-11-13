import { useState, useEffect, useCallback } from 'react'
import { Card, Button, Switch, Select, Space, message, Table, Tag, Spin, Descriptions } from 'antd'
import { ThunderboltOutlined, BellOutlined } from '@ant-design/icons'
import api from '../api.js'

export default function Stock() {
  const [strategies, setStrategies] = useState([])
  const [prefs, setPrefs] = useState({
    premarket_enabled: false, premarket_strategy: 'premarket_momentum', risk_level: 'medium'
  })
  const [reports, setReports] = useState([])
  const [report, setReport] = useState('')
  const [running, setRunning] = useState(false)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    try {
      const [s, p, r] = await Promise.all([
        api.get('/stock/strategies'), api.get('/stock/prefs'), api.get('/stock/reports')
      ])
      setStrategies(s); setPrefs(p); setReports(r)
    } catch (e) { message.error(e.message) } finally { setLoading(false) }
  }, [])
  useEffect(() => { load() }, [load])

  const savePrefs = async () => {
    await api.put('/stock/prefs', prefs)
    message.success('订阅偏好已保存')
  }

  const run = async () => {
    setRunning(true)
    try {
      const r = await api.post('/stock/run')
      setReport(r.report)
      load()
    } catch (e) { message.error(e.message) }
    finally { setRunning(false) }
  }

  const columns = [
    { title: '日期', dataIndex: 'trade_date' },
    { title: '策略', dataIndex: 'strategy_id', render: v => <Tag>{v}</Tag> },
    { title: '标的数', dataIndex: 'picks', render: v => v.length },
    { title: '生成时间', dataIndex: 'created_at' },
  ]

  return (
    <div>
      <h2>A股智能分析</h2>
      <Spin spinning={loading}>
        <Card title={<span><BellOutlined /> 盘前报告订阅（每交易日 08:30 自动推送）</span>} style={{ marginBottom: 16 }}>
          <Space size="large" wrap>
            <Space>
              <span>订阅盘前报告：</span>
              <Switch checked={prefs.premarket_enabled}
                onChange={v => setPrefs({ ...prefs, premarket_enabled: v })} />
            </Space>
            <Space>
              <span>策略：</span>
              <Select style={{ width: 220 }} value={prefs.premarket_strategy}
                onChange={v => setPrefs({ ...prefs, premarket_strategy: v })}
                options={strategies.map(s => ({ value: s.id, label: s.name }))} />
            </Space>
            <Space>
              <span>风险偏好：</span>
              <Select style={{ width: 140 }} value={prefs.risk_level}
                onChange={v => setPrefs({ ...prefs, risk_level: v })}
                options={[
                  { value: 'low', label: '保守 (+5%)' },
                  { value: 'medium', label: '稳健 (+8%)' },
                  { value: 'high', label: '激进 (+12%)' },
                ]} />
            </Space>
            <Button type="primary" onClick={savePrefs}>保存偏好</Button>
          </Space>
        </Card>

        <Card title={<span><ThunderboltOutlined /> 立即生成报告</span>} style={{ marginBottom: 16 }}>
          <Button type="primary" loading={running} onClick={run}>
            立即运行盘前策略
          </Button>
          {report && (
            <pre style={{
              background: '#111', color: '#e6e6e6', padding: 16, borderRadius: 8,
              marginTop: 12, whiteSpace: 'pre-wrap', fontSize: 13
            }}>{report}</pre>
          )}
        </Card>

        <Card title="历史报告">
          <Table rowKey="id" dataSource={reports} columns={columns} pagination={{ pageSize: 10 }}
            expandable={{
              expandedRowRender: (r) => (
                <Descriptions column={1} size="small" bordered>
                  {r.picks.map((p, i) => (
                    <Descriptions.Item key={i} label={`${p.code} ${p.name}`}>
                      目标价 {p.target_price} · {p.watch_period} · {p.reasons.join(' / ')}
                    </Descriptions.Item>
                  ))}
                </Descriptions>
              )
            }}
            locale={{ emptyText: '暂无报告，点击上方「立即运行」生成一份' }} />
        </Card>
      </Spin>
    </div>
  )
}
