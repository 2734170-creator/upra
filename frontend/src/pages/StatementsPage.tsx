import { useState, useEffect } from 'react'
import { Table, Button, Upload, Select, message, Modal, Form, Input, Space, Tag } from 'antd'
import { InboxOutlined, CheckOutlined } from '@ant-design/icons'
import api from '../api/client'

const { Dragger } = Upload

export default function StatementsPage() {
  const [lines, setLines] = useState<any[]>([])
  const [accounts, setAccounts] = useState<any[]>([])
  const [categories, setCategories] = useState<any[]>([])
  const [costCenters, setCostCenters] = useState<any[]>([])
  const [counterparties, setCounterparties] = useState<any[]>([])
  const [selectedAccountId, setSelectedAccountId] = useState<number | undefined>()
  const [processing, setProcessing] = useState(false)
  const [editLine, setEditLine] = useState<any>(null)
  const [form] = Form.useForm()

  const fetchRefs = async () => {
    const [accs, cats, ccs, cps] = await Promise.all([
      api.get('/accounts'),
      api.get('/categories'),
      api.get('/cost-centers'),
      api.get('/counterparties'),
    ])
    setAccounts(accs.data)
    setCategories(cats.data)
    setCostCenters(ccs.data)
    setCounterparties(cps.data)
  }

  const fetchLines = async () => {
    try {
      const { data } = await api.get('/bank-statements/unprocessed')
      setLines(data)
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    fetchRefs()
    fetchLines()
  }, [])

  const handleUpload = async (file: File) => {
    if (!selectedAccountId) {
      message.error('Выберите счёт')
      return false
    }
    const formData = new FormData()
    formData.append('file', file)
    formData.append('account_id', String(selectedAccountId))
    try {
      const { data } = await api.post('/bank-statements/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      message.success(`Загружено: ${data.created} строк, пропущено: ${data.skipped}`)
      fetchLines()
    } catch {
      message.error('Ошибка загрузки')
    }
    return false
  }

  const handleProcess = async (values: any) => {
    setProcessing(true)
    try {
      await api.post(`/bank-statements/lines/${editLine.id}/process`, values)
      message.success('Строка проведена')
      setEditLine(null)
      form.resetFields()
      fetchLines()
    } catch {
      message.error('Ошибка проведения')
    } finally {
      setProcessing(false)
    }
  }

  const handleAutoMatch = async (description: string) => {
    try {
      const { data } = await api.get('/bank-statements/rules/auto-match', { params: { description } })
      if (data.category_id) {
        form.setFieldsValue({ category_id: data.category_id, cost_center_id: data.cost_center_id })
      }
    } catch {
      // ignore
    }
  }

  const columns = [
    { title: 'Дата', dataIndex: 'date', key: 'date' },
    { title: 'Сумма', dataIndex: 'amount', key: 'amount', render: (v: number) => v.toLocaleString('ru-RU') },
    { title: 'Описание', dataIndex: 'description', key: 'description', ellipsis: true },
    { title: 'Контрагент', dataIndex: 'counterparty_name', key: 'counterparty_name' },
    {
      title: 'Действие',
      key: 'action',
      render: (_: any, record: any) => (
        <Button onClick={() => { setEditLine(record); handleAutoMatch(record.description) }}>
          Разнести
        </Button>
      ),
    },
  ]

  return (
    <div>
      <h2>Выписки</h2>
      <Space style={{ marginBottom: 16 }}>
        <Select placeholder="Выберите счёт" style={{ width: 200 }} value={selectedAccountId} onChange={setSelectedAccountId} options={accounts.map((a) => ({ value: a.id, label: a.name }))} />
        <Dragger customRequest={({ file }) => handleUpload(file as File)} showUploadList={false} style={{ width: 300 }}>
          <p className="ant-upload-drag-icon"><InboxOutlined /></p>
          <p>Загрузите CSV или XLSX</p>
        </Dragger>
      </Space>
      <Table columns={columns} dataSource={lines} rowKey="id" />
      <Modal title="Разнос строки" open={!!editLine} onCancel={() => { setEditLine(null); form.resetFields() }} onOk={() => form.submit()} confirmLoading={processing}>
        <Form form={form} layout="vertical" onFinish={handleProcess}>
          <Form.Item name="category_id" label="Категория">
            <Select options={categories.map((c) => ({ value: c.id, label: `${c.name} (${c.type})` }))} allowClear />
          </Form.Item>
          <Form.Item name="cost_center_id" label="ЦФО">
            <Select options={costCenters.map((c) => ({ value: c.id, label: c.name }))} allowClear />
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
