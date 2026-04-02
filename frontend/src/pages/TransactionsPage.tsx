import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, Select, DatePicker, Space, message } from 'antd'
import { PlusOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import api from '../api/client'

const { RangePicker } = DatePicker

export default function TransactionsPage() {
  const [data, setData] = useState<any[]>([])
  const [categories, setCategories] = useState<any[]>([])
  const [accounts, setAccounts] = useState<any[]>([])
  const [counterparties, setCounterparties] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()
  const [dates, setDates] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().startOf('month'),
    dayjs().endOf('month'),
  ])

  const fetchData = async () => {
    setLoading(true)
    try {
      const { data: txs } = await api.get('/transactions', {
        params: { date_from: dates[0].format('YYYY-MM-DD'), date_to: dates[1].format('YYYY-MM-DD') },
      })
      setData(txs)
    } finally {
      setLoading(false)
    }
  }

  const fetchRefs = async () => {
    const [cats, accs, cps] = await Promise.all([
      api.get('/categories'),
      api.get('/accounts'),
      api.get('/counterparties'),
    ])
    setCategories(cats.data)
    setAccounts(accs.data)
    setCounterparties(cps.data)
  }

  useEffect(() => {
    fetchRefs()
  }, [])

  useEffect(() => {
    fetchData()
  }, [dates])

  const handleSubmit = async (values: any) => {
    try {
      await api.post('/transactions', { ...values, date: values.date.format('YYYY-MM-DD') })
      message.success('Транзакция создана')
      setModalOpen(false)
      form.resetFields()
      fetchData()
    } catch {
      message.error('Ошибка создания')
    }
  }

  const columns = [
    { title: 'Дата', dataIndex: 'date', key: 'date' },
    { title: 'Сумма', dataIndex: 'amount', key: 'amount', render: (v: number) => v.toLocaleString('ru-RU') },
    {
      title: 'Тип',
      dataIndex: 'type',
      key: 'type',
      render: (v: string) => ({ income: 'Доход', expense: 'Расход', transfer: 'Перевод' }[v] || v),
    },
    {
      title: 'Категория',
      dataIndex: 'category_id',
      key: 'category_id',
      render: (id: number) => categories.find((c) => c.id === id)?.name || '—',
    },
    { title: 'Комментарий', dataIndex: 'comment', key: 'comment' },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <RangePicker value={dates} onChange={(v) => v && setDates(v as [dayjs.Dayjs, dayjs.Dayjs])} />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          Новая операция
        </Button>
      </div>
      <Table columns={columns} dataSource={data} rowKey="id" loading={loading} />
      <Modal title="Новая операция" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="date" label="Дата" rules={[{ required: true }]}>
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="amount" label="Сумма" rules={[{ required: true }]}>
            <Input type="number" />
          </Form.Item>
          <Form.Item name="type" label="Тип" rules={[{ required: true }]}>
            <Select options={[{ value: 'income', label: 'Доход' }, { value: 'expense', label: 'Расход' }, { value: 'transfer', label: 'Перевод' }]} />
          </Form.Item>
          <Form.Item name="account_id" label="Счёт" rules={[{ required: true }]}>
            <Select options={accounts.map((a) => ({ value: a.id, label: a.name }))} />
          </Form.Item>
          <Form.Item name="category_id" label="Категория">
            <Select options={categories.map((c) => ({ value: c.id, label: c.name }))} allowClear />
          </Form.Item>
          <Form.Item name="counterparty_id" label="Контрагент">
            <Select options={counterparties.map((c) => ({ value: c.id, label: c.name }))} allowClear />
          </Form.Item>
          <Form.Item name="comment" label="Комментарий">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
