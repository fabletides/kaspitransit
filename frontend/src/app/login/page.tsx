'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'

const DEMO_ACCOUNTS = [
  { role: 'admin' as const, label: 'Admin', color: 'text-purple-400', bg: 'bg-purple-500/20 hover:bg-purple-500/30 border-purple-500/30' },
  { role: 'analyst' as const, label: 'Analyst', color: 'text-teal-400', bg: 'bg-teal-500/20 hover:bg-teal-500/30 border-teal-500/30' },
  { role: 'shipper' as const, label: 'Shipper', color: 'text-green-400', bg: 'bg-green-500/20 hover:bg-green-500/30 border-green-500/30' },
  { role: 'driver' as const, label: 'Driver', color: 'text-amber-400', bg: 'bg-amber-500/20 hover:bg-amber-500/30 border-amber-500/30' },
]

export default function LoginPage() {
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { quickLogin } = useAuth()
  const router = useRouter()

  const handleQuickLogin = async (role: typeof DEMO_ACCOUNTS[0]['role']) => {
    setError('')
    setLoading(true)
    try {
      await quickLogin(role)
      router.push('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-kt-dark flex items-center justify-center relative overflow-hidden">
      {/* Background grid */}
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: 'linear-gradient(rgba(14,165,233,1) 1px, transparent 1px), linear-gradient(90deg, rgba(14,165,233,1) 1px, transparent 1px)',
        backgroundSize: '60px 60px'
      }} />
      {/* Glow orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-kt-blue/5 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />

      <div className="relative w-full max-w-md mx-4">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-kt-blue to-kt-teal flex items-center justify-center">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
          </div>
          <h1 className="text-4xl font-display font-bold text-white">Keruen</h1>
          <p className="text-slate-400 mt-2 text-sm">Mangystau Digital Logistics Control Center</p>
          <p className="text-slate-500 mt-4 text-xs">Hackathon Demo Mode</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Quick Login Cards */}
        <div className="space-y-3">
          <p className="kt-label mb-4 text-slate-300">Select your role to start</p>
          {DEMO_ACCOUNTS.map((acc) => (
            <button
              key={acc.role}
              onClick={() => handleQuickLogin(acc.role)}
              disabled={loading}
              className={`w-full px-6 py-4 rounded-lg border transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                ${acc.bg}
                flex items-center justify-between group hover:shadow-lg hover:shadow-${acc.role}-500/20
              `}
            >
              <div className="text-left">
                <div className={`font-display font-bold text-lg ${acc.color}`}>
                  {acc.label}
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  {acc.role}@keruen.local
                </div>
              </div>
              <div className="text-right text-slate-400 text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                Click to login →
              </div>
            </button>
          ))}
        </div>

        {/* Info Section */}
        <div className="mt-8 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
          <p className="text-xs text-slate-400 mb-2 font-semibold">Demo Credentials:</p>
          <ul className="text-xs text-slate-500 space-y-1">
            <li>• Email: [role]@keruen.local</li>
            <li>• Password: demo123</li>
            <li>• All demo accounts are pre-configured</li>
          </ul>
        </div>

        <p className="text-center text-xs text-slate-600 mt-8">
          Keruen v1.0 Hackathon MVP · Mangystau Region, Kazakhstan
        </p>
      </div>
    </div>
  )
}
