import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Avatar, Dropdown } from 'antd'
import {
  DashboardOutlined,
  TransactionOutlined,
  FileTextOutlined,
  BarChartOutlined,
  BookOutlined,
  LogoutOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../stores/authStore'

const { Sider, Content, Header } = Layout

const menuItems = [
  { key: '/dashboard', icon: <DashboardOutlined />, label: 'Дашборд' },
  { key: '/transactions', icon: <TransactionOutlined />, label: 'Операции' },
  { key: '/statements', icon: <FileTextOutlined />, label: 'Выписки' },
  { key: '/reports', icon: <BarChartOutlined />, label: 'Отчёты' },
  { key: '/references', icon: <BookOutlined />, label: 'Справочники' },
]

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const userMenu = {
    items: [
      { key: 'logout', icon: <LogoutOutlined />, label: 'Выйти', onClick: handleLogout },
    ],
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div style={{ height: 32, margin: 16, color: '#fff', fontSize: 16, textAlign: 'center', fontWeight: 'bold' }}>
          {collapsed ? 'УУ' : 'Управ. учёт'}
        </div>
        <Menu theme="dark" selectedKeys={[location.pathname]} onClick={({ key }) => navigate(key)} items={menuItems} />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <Dropdown menu={userMenu}>
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.email}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: 16 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
