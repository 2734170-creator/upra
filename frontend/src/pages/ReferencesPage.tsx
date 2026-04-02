import { useState, useEffect } from 'react'
import { Tabs, Table, Button, Modal, Form, Input, Select, Space, message, Popconfirm } from 'antd'
import { PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons'
import CategoriesPage from './CategoriesPage'
import api from '../api/client'

function CrudPage({
  endpoint,
  columns,
  formFields,
  getDefaults,
}: {
  endpoint: string
  columns: any[]
  formFields: any[]
  getDefaults?: () => Record<string, any>
}) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<any>(null)
  const [form] = Form.useForm()

  const fetchData = async () => {
    setLoading(true)
    try {
      const { data: items } = await api.get(endpoint)
      setData(items)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [endpoint])

  const handleSubmit = async (values: any) => {
    try {
      if (editing) {
        await api.put(`${endpoint}/${editing.id}`, values)
        message.success('Обновлено')
      } else {
        await api.post(endpoint, values)
        message.success('Создано')
      }
      setModalOpen(false)
      setEditing(null)
      fetchData()
    } catch {
      message.error('Ошибка')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`${endpoint}/${id}`)
      message.success('Удалено')
      fetchData()
    } catch {
      message.error('Ошибка удаления')
    }
  }

  const handleOpenModal = () => {
    setEditing(null)
    setModalOpen(true)
    setTimeout(() => {
      form.resetFields()
      if (getDefaults) {
        const d = getDefaults()
        Object.keys(d).forEach((k) => form.setFieldValue(k, d[k]))
      }
    }, 100)
  }

  const allColumns = [
    ...columns,
    {
      title: 'Действия',
      key: 'actions',
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

  return (
    <div>
      <Button type="primary" icon={<PlusOutlined />} style={{ marginBottom: 16 }} onClick={handleOpenModal}>
        Добавить
      </Button>
      <Table columns={allColumns} dataSource={data} rowKey="id" loading={loading} size="small" />
      <Modal
        title={editing ? 'Редактировать' : 'Добавить'}
        open={modalOpen}
        onCancel={() => {
          setModalOpen(false)
          setEditing(null)
        }}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          {formFields.map((f: any) => (
            <Form.Item key={f.name} name={f.name} label={f.label} rules={f.rules}>
              {f.type === 'select' ? (
                <Select options={f.options} showSearch optionFilterProp="label" />
              ) : (
                <Input />
              )}
            </Form.Item>
          ))}
        </Form>
      </Modal>
    </div>
  )
}

export default function ReferencesPage() {
  const [categories, setCategories] = useState<any[]>([])
  const [companies, setCompanies] = useState<any[]>([])
  const [accounts, setAccounts] = useState<any[]>([])
  const [costCenters, setCostCenters] = useState<any[]>([])
  const [counterparties, setCounterparties] = useState<any[]>([])
  const [currencies, setCurrencies] = useState<any[]>([])
  const [companiesFormKey, setCompaniesFormKey] = useState(0)
  const [accountsFormKey, setAccountsFormKey] = useState(0)

  const fetchAll = async () => {
    const [cats, co, a, cc, cp, cur] = await Promise.all([
      api.get('/categories'),
      api.get('/companies'),
      api.get('/accounts'),
      api.get('/cost-centers'),
      api.get('/counterparties'),
      api.get('/currencies'),
    ])
    setCategories(cats.data)
    setCompanies(co.data)
    setAccounts(a.data)
    setCostCenters(cc.data)
    setCounterparties(cp.data)
    setCurrencies(cur.data)
  }

  useEffect(() => {
    fetchAll()
  }, [])

  const currencyOptions = currencies.map((c) => ({
    value: c.id,
    label: c.symbol ? `${c.name_ru} (${c.symbol})` : c.name_ru,
  }))

  const getRubId = () => currencies.find((c) => c.code === 'RUB')?.id

  const companiesFormFields = [
    { name: 'name', label: 'Название', rules: [{ required: true }] },
    { name: 'type', label: 'Тип', type: 'select', rules: [{ required: true }], options: [{ value: 'ooo', label: 'ООО' }, { value: 'ip', label: 'ИП' }] },
  ]

  const accountsFormFields = [
    { name: 'name', label: 'Название', rules: [{ required: true }] },
    { name: 'company_id', label: 'Компания', type: 'select', rules: [{ required: true }], options: companies.map((c) => ({ value: c.id, label: c.name })) },
    { name: 'type', label: 'Тип', type: 'select', rules: [{ required: true }], options: [{ value: 'bank', label: 'Банк' }, { value: 'cash', label: 'Касса' }] },
  ]

  const tabs = [
    {
      key: 'companies',
      label: 'Компании',
      children: (
        <CrudPage
          key={companiesFormKey}
          endpoint="/companies"
          columns={[
            { title: 'Название', dataIndex: 'name', key: 'name' },
            { title: 'Тип', dataIndex: 'type', key: 'type', render: (v: string) => ({ ooo: 'ООО', ip: 'ИП' }[v] || v) },
          ]}
          formFields={companiesFormFields}
          getDefaults={() => ({ type: 'ooo' })}
        />
      ),
    },
    {
      key: 'accounts',
      label: 'Счета',
      children: (
        <CrudPage
          key={accountsFormKey}
          endpoint="/accounts"
          columns={[
            { title: 'Название', dataIndex: 'name', key: 'name' },
            { title: 'Тип', dataIndex: 'type', key: 'type', render: (v: string) => ({ bank: 'Банк', cash: 'Касса' }[v] || v) },
          ]}
          formFields={accountsFormFields}
          getDefaults={() => ({ type: 'bank' })}
        />
      ),
    },
    {
      key: 'categories',
      label: 'Статьи ДДС',
      children: <CategoriesPage />,
    },
    {
      key: 'cost_centers',
      label: 'ЦФО',
      children: (
        <CrudPage
          endpoint="/cost-centers"
          columns={[{ title: 'Название', dataIndex: 'name', key: 'name' }]}
          formFields={[{ name: 'name', label: 'Название', rules: [{ required: true }] }]}
        />
      ),
    },
    {
      key: 'counterparties',
      label: 'Контрагенты',
      children: (
        <CrudPage
          endpoint="/counterparties"
          columns={[
            { title: 'Название', dataIndex: 'name', key: 'name' },
            { title: 'Тип', dataIndex: 'type', key: 'type', render: (v: string) => ({ client: 'Клиент', supplier: 'Поставщик' }[v] || v) },
          ]}
          formFields={[
            { name: 'name', label: 'Название', rules: [{ required: true }] },
            { name: 'type', label: 'Тип', type: 'select', rules: [{ required: true }], options: [{ value: 'client', label: 'Клиент' }, { value: 'supplier', label: 'Поставщик' }] },
          ]}
        />
      ),
    },
    {
      key: 'currencies',
      label: 'Валюты',
      children: (
        <CrudPage
          endpoint="/currencies"
          columns={[
            { title: 'Название', dataIndex: 'name_ru', key: 'name_ru' },
            { title: 'Символ', dataIndex: 'symbol', key: 'symbol' },
          ]}
          formFields={[
            { name: 'name_ru', label: 'Название', rules: [{ required: true }] },
            { name: 'symbol', label: 'Символ (необязательно)' },
          ]}
        />
      ),
    },
    {
      key: 'rules',
      label: 'Правила авторазноса',
      children: (
        <CrudPage
          endpoint="/categorization-rules"
          columns={[
            { title: 'Ключевое слово', dataIndex: 'keyword', key: 'keyword' },
            { title: 'Категория', dataIndex: 'category_id', key: 'category_id', render: (id: number) => categories.find((c) => c.id === id)?.name || '—' },
          ]}
          formFields={[
            { name: 'keyword', label: 'Ключевое слово', rules: [{ required: true }] },
            { name: 'category_id', label: 'Категория', type: 'select', rules: [{ required: true }], options: categories.map((c) => ({ value: c.id, label: c.name })) },
          ]}
        />
      ),
    },
  ]

  return (
    <div>
      <h2>Справочники</h2>
      <Tabs items={tabs} />
    </div>
  )
}
