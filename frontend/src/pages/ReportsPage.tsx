import { useState, useEffect } from 'react'
import { Tabs, Table, DatePicker, Space, Card, Statistic, Row, Col } from 'antd'
import dayjs from 'dayjs'
import api from '../api/client'

const { RangePicker } = DatePicker

export default function ReportsPage() {
  const [dates, setDates] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().startOf('month'),
    dayjs().endOf('month'),
  ])
  const [cashflow, setCashflow] = useState<any>(null)
  const [pnl, setPnl] = useState<any>(null)
  const [budget, setBudget] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const params = { date_from: dates[0].format('YYYY-MM-DD'), date_to: dates[1].format('YYYY-MM-DD') }

  const fetchReports = async () => {
    setLoading(true)
    try {
      const [cf, p, b] = await Promise.all([
        api.get('/reports/cashflow', { params }),
        api.get('/reports/pnl', { params }),
        api.get('/reports/budget', { params }),
      ])
      setCashflow(cf.data)
      setPnl(p.data)
      setBudget(b.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReports()
  }, [])

  const cfColumns = [
    { title: 'Категория', dataIndex: 'category_name', key: 'category_name' },
    { title: 'Доход', dataIndex: 'income', key: 'income', render: (v: number) => v.toLocaleString('ru-RU') },
    { title: 'Расход', dataIndex: 'expense', key: 'expense', render: (v: number) => v.toLocaleString('ru-RU') },
    { title: 'Нетто', dataIndex: 'net', key: 'net', render: (v: number) => v.toLocaleString('ru-RU') },
  ]

  const pnlColumns = [
    { title: 'Категория', dataIndex: 'category_name', key: 'category_name' },
    { title: 'Сумма', dataIndex: 'amount', key: 'amount', render: (v: number) => v.toLocaleString('ru-RU') },
  ]

  const budgetColumns = [
    { title: 'Категория', dataIndex: 'category_id', key: 'category_id' },
    { title: 'План', dataIndex: 'planned', key: 'planned', render: (v: number) => v.toLocaleString('ru-RU') },
    { title: 'Факт', dataIndex: 'actual', key: 'actual', render: (v: number) => v.toLocaleString('ru-RU') },
    { title: 'Отклонение', dataIndex: 'deviation', key: 'deviation', render: (v: number) => v.toLocaleString('ru-RU') },
    { title: '%', dataIndex: 'deviation_pct', key: 'deviation_pct', render: (v: number) => `${v}%` },
  ]

  return (
    <div>
      <h2>Отчёты</h2>
      <Space style={{ marginBottom: 16 }}>
        <RangePicker value={dates} onChange={(v) => v && (setDates(v as [dayjs.Dayjs, dayjs.Dayjs]), fetchReports())} />
      </Space>
      <Tabs
        items={[
          {
            key: 'cashflow',
            label: 'ДДС',
            children: (
              <Card loading={loading}>
                <Row gutter={16} style={{ marginBottom: 16 }}>
                  <Col span={8}><Statistic title="Остаток на начало" value={cashflow?.opening_balance || 0} precision={2} /></Col>
                  <Col span={8}><Statistic title="Остаток на конец" value={cashflow?.closing_balance || 0} precision={2} /></Col>
                </Row>
                <Table columns={cfColumns} dataSource={cashflow?.items || []} rowKey="category_id" pagination={false} />
              </Card>
            ),
          },
          {
            key: 'pnl',
            label: 'ОПиУ',
            children: (
              <Card loading={loading}>
                <Row gutter={16} style={{ marginBottom: 16 }}>
                  <Col span={8}><Statistic title="Доходы" value={pnl?.income || 0} precision={2} /></Col>
                  <Col span={8}><Statistic title="Расходы" value={pnl?.expense || 0} precision={2} /></Col>
                  <Col span={8}><Statistic title="Прибыль" value={pnl?.profit || 0} precision={2} /></Col>
                </Row>
                <Table columns={pnlColumns} dataSource={pnl?.items || []} rowKey="category_id" pagination={false} />
              </Card>
            ),
          },
          {
            key: 'budget',
            label: 'БДР',
            children: (
              <Card loading={loading}>
                <Table columns={budgetColumns} dataSource={budget?.items || []} rowKey="category_id" pagination={false} />
              </Card>
            ),
          },
        ]}
      />
    </div>
  )
}
