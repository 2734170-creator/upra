import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Table, DatePicker, Space } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined, DollarOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import api from '../api/client'

const { RangePicker } = DatePicker

export default function DashboardPage() {
  const [cashflow, setCashflow] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [dates, setDates] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().startOf('month'),
    dayjs().endOf('month'),
  ])

  const fetchReport = async () => {
    setLoading(true)
    try {
      const { data } = await api.get('/reports/cashflow', {
        params: {
          date_from: dates[0].format('YYYY-MM-DD'),
          date_to: dates[1].format('YYYY-MM-DD'),
        },
      })
      setCashflow(data)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReport()
  }, [])

  const totalIncome = cashflow?.items?.reduce((s: number, i: any) => s + i.income, 0) || 0
  const totalExpense = cashflow?.items?.reduce((s: number, i: any) => s + i.expense, 0) || 0

  const columns = [
    { title: 'Категория', dataIndex: 'category_name', key: 'category_name' },
    { title: 'Доход', dataIndex: 'income', key: 'income', render: (v: number) => v.toLocaleString('ru-RU') },
    { title: 'Расход', dataIndex: 'expense', key: 'expense', render: (v: number) => v.toLocaleString('ru-RU') },
    { title: 'Нетто', dataIndex: 'net', key: 'net', render: (v: number) => v.toLocaleString('ru-RU') },
  ]

  return (
    <div>
      <h2>Дашборд</h2>
      <Space style={{ marginBottom: 16 }}>
        <RangePicker value={dates} onChange={(v) => v && setDates(v as [dayjs.Dayjs, dayjs.Dayjs])} />
      </Space>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic title="Доходы" value={totalIncome} prefix={<ArrowUpOutlined style={{ color: '#52c41a' }} />} precision={2} />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic title="Расходы" value={totalExpense} prefix={<ArrowDownOutlined style={{ color: '#ff4d4f' }} />} precision={2} />
          </Card>
        </Col>
        <Col span={8}>
          <Card loading={loading}>
            <Statistic title="Баланс" value={cashflow?.closing_balance || 0} prefix={<DollarOutlined />} precision={2} />
          </Card>
        </Col>
      </Row>
      <Card title="ДДС за период" loading={loading}>
        <Table columns={columns} dataSource={cashflow?.items || []} rowKey="category_id" pagination={false} />
      </Card>
    </div>
  )
}
