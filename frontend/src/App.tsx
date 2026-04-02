import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider } from 'antd'
import ruRU from 'antd/locale/ru_RU'
import dayjs from 'dayjs'
import 'dayjs/locale/ru'
import LoginPage from './pages/LoginPage'
import MainLayout from './components/MainLayout'
import DashboardPage from './pages/DashboardPage'
import TransactionsPage from './pages/TransactionsPage'
import StatementsPage from './pages/StatementsPage'
import ReportsPage from './pages/ReportsPage'
import ReferencesPage from './pages/ReferencesPage'

dayjs.locale('ru')

const queryClient = new QueryClient()

export default function App() {
  return (
    <ConfigProvider locale={ruRU}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="transactions" element={<TransactionsPage />} />
              <Route path="statements" element={<StatementsPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="references" element={<ReferencesPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ConfigProvider>
  )
}
