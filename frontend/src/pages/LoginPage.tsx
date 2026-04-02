import { useState } from 'react'
import { Form, Input, Button, Card, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuthStore } from '../stores/authStore'

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { setUser, setToken } = useAuthStore()

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      params.append('email', values.email)
      params.append('password', values.password)
      const { data } = await api.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      setToken(data.access_token)
      const { data: user } = await api.get('/auth/me')
      setUser(user)
      message.success('Добро пожаловать!')
      navigate('/dashboard')
    } catch {
      message.error('Неверный email или пароль')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card title="Управленческий учёт" style={{ width: 360 }}>
        <Form onFinish={onFinish}>
          <Form.Item name="email" rules={[{ required: true, message: 'Введите email' }]}>
            <Input prefix={<UserOutlined />} placeholder="Email" size="large" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: 'Введите пароль' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Пароль" size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large">
              Войти
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
