'use client'
import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi } from './api'

interface User {
  id: number
  email: string
  full_name: string
  role: string
  company?: string
  phone?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  quickLogin: (role: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

// Demo accounts for quick login
const DEMO_ACCOUNTS = {
  admin: { email: "admin@keruen.local", password: "demo123" },
  analyst: { email: "analyst@keruen.local", password: "demo123" },
  shipper: { email: "shipper@keruen.local", password: "demo123" },
  driver: { email: "driver@keruen.local", password: "demo123" },
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const storedToken = localStorage.getItem('kt_token')
    const storedUser = localStorage.getItem('kt_user')
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
        if (storedToken) {
          setToken(storedToken)
        }
      } catch (e) {
        localStorage.removeItem('kt_user')
        localStorage.removeItem('kt_token')
      }
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const res = await authApi.login(email, password)
      const { access_token, user: userData } = res.data
      
      localStorage.setItem('kt_token', access_token)
      localStorage.setItem('kt_user', JSON.stringify(userData))
      setToken(access_token)
      setUser(userData)
    } catch (error) {
      localStorage.removeItem('kt_token')
      localStorage.removeItem('kt_user')
      throw error
    }
  }

  const quickLogin = async (role: keyof typeof DEMO_ACCOUNTS) => {
    const account = DEMO_ACCOUNTS[role]
    if (!account) {
      throw new Error(`Unknown role: ${role}`)
    }
    await login(account.email, account.password)
  }

  const logout = () => {
    localStorage.removeItem('kt_token')
    localStorage.removeItem('kt_user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, quickLogin, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
