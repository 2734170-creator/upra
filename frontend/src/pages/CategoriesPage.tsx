import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, Select, Space, message, Popconfirm, Divider, Checkbox } from 'antd'
import { PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons'
import api from '../api/client'

const MOVEMENT_TYPES = [
  { value: 'inflow', label: 'Поступление' },
  { value: 'outflow', label: 'Выбытие' },
]

const DDS_SECTIONS = [
  { value: 'operating', label: 'Операционная деятельность' },
  { value: 'investing', label: 'Инвестиционная деятельность' },
  { value: 'financing', label: 'Финансовая деятельность' },
  { value: 'internal', label: 'Внутренние перемещения' },
]

const PNL_IMPACTS = [
  { value: 'income', label: 'Доход' },
  { value: 'expense', label: 'Расход' },
  { value: 'none', label: 'Не влияет' },
]

export default function CategoriesPage() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<any>(null)
  const [form] = Form.useForm()
  const [categories, setCategories] = useState<any[]>([])
  const [currencies, setCurrencies] = useState<any[]>([])

  const fetchData = async () => {
    setLoading(true)
    try {
      const { data: items } = await api.get('/categories')
      setData(items)
    } finally {
      setLoading(false)
    }
  }

  const fetchRefs = async () => {
    const [cats, curs] = await Promise.all([
      api.get('/categories'),
      api.get('/currencies'),
    ])
    setCategories(cats.data)
    setCurrencies(curs.data)
  }

  useEffect(() => {
    fetchData()
    fetchRefs()
  }, [])

  const handleSubmit = async (values: any) => {
    try {
      if (editing) {
        await api.put(`/categories/${editing.id}`, values)
        message.success('Обновлено')
      } else {
        await api.post('/categories', values)
        message.success('Создано')
      }
      setModalOpen(false)
      setEditing(null)
      fetchData()
      fetchRefs()
    } catch {
      message.error('Ошибка')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/categories/${id}`)
      message.success('Удалено')
      fetchData()
      fetchRefs()
    } catch {
      message.error('Ошибка удаления')
    }
  }

  const handleOpenModal = () => {
    setEditing(null)
    setModalOpen(true)
    setTimeout(() => {
      form.resetFields()
      form.setFieldsValue({ is_active: true, pnl_impact: 'none' })
    }, 100)
  }

  const columns = [
    { title: 'Код', dataIndex: 'code', key: 'code', width: 100 },
    { title: 'Название', dataIndex: 'name', key: 'name', ellipsis: true },
    {
      title: 'Раздел ДДС',
      dataIndex: 'dds_section',
      key: 'dds_section',
      width: 180,
      render: (v: string) => DDS_SECTIONS.find((s) => s.value === v)?.label || '—',
    },
    {
      title: 'Движение',
      dataIndex: 'movement_type',
      key: 'movement_type',
      width: 120,
      render: (v: string) => MOVEMENT_TYPES.find((t) => t.value === v)?.label || '—',
    },
    {
      title: 'Статья БДР',
      dataIndex: 'pnl_article_name',
      key: 'pnl_article_name',
      ellipsis: true,
      render: (v: string) => v || '—',
    },
    {
      title: 'Влияние на БДР',
      dataIndex: 'pnl_impact',
      key: 'pnl_impact',
      width: 120,
      render: (v: string) => PNL_IMPACTS.find((p) => p.value === v)?.label || '—',
    },
    {
      title: 'Активна',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (v: boolean) => (v ? 'Да' : 'Нет'),
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 100,
      fixed: 'right' as const,
      render: (_: any, record: any) => (
        <Space>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => {
              setEditing(record)
              form.setFieldsValue(record)
              setModalOpen(true)
            }}
          />
          <Popconfirm title="Удалить?" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const parentOptions = categories.map((c) => ({
    value: c.id,
    label: c.code ? `${c.code} ${c.name}` : c.name,
  }))

  const pnlArticleOptions = categories
    .filter((c) => c.is_pnl)
    .map((c) => ({
      value: c.id,
      label: c.code ? `${c.code} ${c.name}` : c.name,
    }))

  const currencyOptions = currencies.map((c) => ({
    value: c.id,
    label: c.symbol ? `${c.name_ru} (${c.symbol})` : c.name_ru,
  }))

  return (
    <div>
      <Button type="primary" icon={<PlusOutlined />} style={{ marginBottom: 16 }} onClick={handleOpenModal}>
        Добавить
      </Button>
      <Table columns={columns} dataSource={data} rowKey="id" loading={loading} size="small" scroll={{ x: 1200 }} />
      <Modal
        title={editing ? 'Редактировать статью' : 'Добавить статью'}
        open={modalOpen}
        onCancel={() => {
          setModalOpen(false)
          setEditing(null)
        }}
        onOk={() => form.submit()}
        width={700}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="name" label="Название *" rules={[{ required: true }]}>
            <Input />
          </Form.Item>

          <Form.Item name="movement_type" label="Тип движения *" rules={[{ required: true }]}>
            <Select options={MOVEMENT_TYPES} dropdownMatchSelectWidth={false} listHeight={250} />
          </Form.Item>

          <Form.Item name="dds_section" label="Раздел ДДС *" rules={[{ required: true }]}>
            <Select options={DDS_SECTIONS} dropdownMatchSelectWidth={false} listHeight={250} />
          </Form.Item>

          <Form.Item name="parent_id" label="Родительская группа">
            <Select options={parentOptions} allowClear placeholder="Выберите родительскую группу" dropdownMatchSelectWidth={false} listHeight={300} />
          </Form.Item>

          <Divider style={{ margin: '12px 0' }}>Связь с БДР</Divider>

          <Space size="middle" style={{ width: '100%' }}>
            <Form.Item name="pnl_article_id" label="Статья БДР" style={{ flex: 1 }}>
              <Select options={pnlArticleOptions} allowClear placeholder="Выберите статью БДР" dropdownMatchSelectWidth={false} listHeight={300} />
            </Form.Item>
            <Form.Item name="pnl_impact" label="Тип влияния на БДР" style={{ flex: 1 }}>
              <Select
                options={PNL_IMPACTS}
                dropdownMatchSelectWidth={false}
                onChange={(val) => {
                  if (val === 'none') {
                    form.setFieldValue('pnl_article_id', null)
                  }
                }}
              />
            </Form.Item>
          </Space>

          <Divider style={{ margin: '12px 0' }}>Дополнительно</Divider>

          <Space size="middle" style={{ width: '100%' }}>
            <Form.Item name="code" label="Код" style={{ flex: 1 }}>
              <Input placeholder="Например: 11.01" />
            </Form.Item>
            <Form.Item name="currency_id" label="Валюта" style={{ flex: 1 }}>
              <Select options={currencyOptions} allowClear dropdownMatchSelectWidth={false} />
            </Form.Item>
          </Space>

          <Form.Item name="is_active" valuePropName="checked">
            <Checkbox>Активна</Checkbox>
          </Form.Item>

          <Form.Item name="comment" label="Комментарий">
            <Input.TextArea rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
