import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { 
  User, 
  Settings as SettingsIcon, 
  Key, 
  Eye, 
  EyeOff, 
  Copy, 
  Check, 
  Save,
  Moon,
  Sun,
  Lock
} from 'lucide-react'

const Settings = () => {
  const { user } = useAuth()
  
  // States
  const [defaultModel, setDefaultModel] = useState('ensemble')
  const [enableLime, setEnableLime] = useState(true)
  const [theme, setTheme] = useState('light')
  const [showKey, setShowKey] = useState(false)
  const [copiedKey, setCopiedKey] = useState(false)
  const [copiedCurl, setCopiedCurl] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  
  // Profile password state mocks
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')

  const apiToken = localStorage.getItem('token') || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sentix-mock-token-xyz123'
  
  const handleSavePreferences = (e) => {
    e.preventDefault()
    setSaveSuccess(true)
    setTimeout(() => {
      setSaveSuccess(false)
    }, 3000)
  }

  const handleCopyToken = () => {
    navigator.clipboard.writeText(apiToken)
    setCopiedKey(true)
    setTimeout(() => setCopiedKey(false), 2000)
  }

  const curlSnippet = `curl -X POST "http://localhost:8000/api/v1/predict" \\
  -H "Authorization: Bearer ${apiToken.slice(0, 15)}..." \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Sentix AI ensemble models are incredibly fast!",
    "model_name": "ensemble"
  }'`

  const handleCopyCurl = () => {
    navigator.clipboard.writeText(curlSnippet)
    setCopiedCurl(true)
    setTimeout(() => setCopiedCurl(false), 2000)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start select-none">
      
      {/* Left Navigation Tabs Mock */}
      <div className="lg:col-span-4 bg-white p-5 rounded-xl border border-gray-border shadow-sm flex flex-col gap-2">
        <h3 className="text-xs font-bold text-text-muted uppercase tracking-wider px-3 mb-2">Platform Settings</h3>
        <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold bg-teal/10 text-teal text-left">
          <SettingsIcon className="h-4.5 w-4.5" /> General Preferences
        </button>
        <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-text-mid hover:bg-gray-50 text-left">
          <User className="h-4.5 w-4.5" /> Operator Profile
        </button>
        <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-text-mid hover:bg-gray-50 text-left">
          <Key className="h-4.5 w-4.5" /> API Keys & Webhooks
        </button>
      </div>

      {/* Right Content Panels */}
      <div className="lg:col-span-8 flex flex-col gap-6">
        
        {/* Save success banner */}
        {saveSuccess && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl px-6 py-4 text-xs font-semibold text-emerald-800 flex items-center gap-2">
            <Check className="h-4 w-4 text-emerald-600" />
            <span>Preferences saved successfully! Default settings updated.</span>
          </div>
        )}

        {/* Card 1: Preferences */}
        <div className="bg-white p-6 md:p-8 rounded-xl border border-gray-border shadow-sm flex flex-col gap-6">
          <div>
            <h2 className="text-base font-bold text-text-dark">General Preferences</h2>
            <p className="text-xs text-text-muted mt-1">Configure default analyzer parameters and appearance configurations</p>
          </div>

          <form onSubmit={handleSavePreferences} className="flex flex-col gap-5">
            {/* Preferred Model */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-text-dark uppercase tracking-wider">
                Default Inference Model
              </label>
              <select
                value={defaultModel}
                onChange={(e) => setDefaultModel(e.target.value)}
                className="w-full max-w-md rounded-lg border border-gray-border px-3 py-2.5 text-sm text-text-dark bg-gray-50 focus:bg-white focus:outline-none"
              >
                <option value="ensemble">Ensemble (recommended)</option>
                <option value="distilbert">DistilBERT</option>
                <option value="bilstm">BiLSTM</option>
                <option value="gru">GRU + Attention</option>
                <option value="cnn_lstm">CNN-LSTM</option>
              </select>
            </div>

            {/* Toggle LIME highlights */}
            <div className="flex items-center justify-between border-t border-gray-border pt-4">
              <div className="flex flex-col gap-0.5">
                <span className="text-sm font-semibold text-text-dark">Enable LIME Attribution</span>
                <span className="text-xs text-text-muted">Extract word contribution highlights automatically on execution</span>
              </div>
              <input
                type="checkbox"
                checked={enableLime}
                onChange={(e) => setEnableLime(e.target.checked)}
                className="rounded border-gray-300 text-teal focus:ring-teal cursor-pointer h-4 w-4"
              />
            </div>

            {/* Theme Toggle mockup */}
            <div className="flex items-center justify-between border-t border-gray-border pt-4">
              <div className="flex flex-col gap-0.5">
                <span className="text-sm font-semibold text-text-dark">App Theme</span>
                <span className="text-xs text-text-muted">Toggle background display preferences</span>
              </div>
              <div className="flex items-center border border-gray-border rounded-lg p-0.5 bg-gray-50">
                <button
                  type="button"
                  onClick={() => setTheme('light')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                    theme === 'light' ? 'bg-white text-text-dark shadow-sm' : 'text-text-muted hover:text-text-dark'
                  }`}
                >
                  <Sun className="h-3.5 w-3.5" /> Light
                </button>
                <button
                  type="button"
                  onClick={() => setTheme('dark')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                    theme === 'dark' ? 'bg-navy text-white shadow-sm' : 'text-text-muted hover:text-text-dark'
                  }`}
                >
                  <Moon className="h-3.5 w-3.5" /> Dark
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="self-start mt-2 bg-teal hover:bg-teal-dark text-white font-semibold px-5 py-2.5 rounded-lg text-sm shadow-md transition-all flex items-center gap-1.5"
            >
              <Save className="h-4 w-4" /> Save Preferences
            </button>
          </form>
        </div>

        {/* Card 2: Developer API Keys */}
        <div className="bg-white p-6 md:p-8 rounded-xl border border-gray-border shadow-sm flex flex-col gap-6">
          <div>
            <h2 className="text-base font-bold text-text-dark">API Keys & Integrations</h2>
            <p className="text-xs text-text-muted mt-1">Access your platform credentials to trigger remote model predictions</p>
          </div>

          <div className="flex flex-col gap-4">
            
            {/* Key Field */}
            <div className="flex flex-col gap-2">
              <span className="text-xs font-bold text-text-dark uppercase tracking-wider">Active Operator Token</span>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <input
                    type={showKey ? 'text' : 'password'}
                    readOnly
                    value={apiToken}
                    className="w-full rounded-lg border border-gray-border pl-4 pr-10 py-2.5 text-xs font-mono text-text-dark bg-gray-50 focus:outline-none"
                  />
                  <button
                    onClick={() => setShowKey(!showKey)}
                    className="absolute right-3 top-3 text-text-muted hover:text-text-dark"
                  >
                    {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>

                <button
                  onClick={handleCopyToken}
                  className="bg-white border border-gray-border hover:bg-gray-50 text-text-dark font-semibold px-4 rounded-lg flex items-center justify-center transition-all shadow-sm"
                  title="Copy Token"
                >
                  {copiedKey ? <Check className="h-4 w-4 text-emerald-600" /> : <Copy className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Curl snippet code block */}
            <div className="flex flex-col gap-2 mt-2">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-text-dark uppercase tracking-wider">Sample curl request</span>
                <button
                  onClick={handleCopyCurl}
                  className="text-teal text-xs font-semibold flex items-center gap-1 hover:underline"
                >
                  {copiedCurl ? (
                    <>
                      <Check className="h-3 w-3 text-emerald-600" /> Copied Snippet
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" /> Copy Snippet
                    </>
                  )}
                </button>
              </div>
              <pre className="rounded-xl bg-navy p-4 text-[11px] font-mono text-gray-300 leading-relaxed overflow-x-auto border border-[#162035]">
                {curlSnippet}
              </pre>
            </div>

          </div>
        </div>

        {/* Card 3: Security & Profile */}
        <div className="bg-white p-6 md:p-8 rounded-xl border border-gray-border shadow-sm flex flex-col gap-5">
          <div>
            <h2 className="text-base font-bold text-text-dark">Operator Profile Details</h2>
            <p className="text-xs text-text-muted mt-1">Logged operator context details</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-50 rounded-xl p-4 border border-gray-border text-xs">
            <div className="flex flex-col gap-1">
              <span className="font-bold text-text-muted uppercase">Username</span>
              <span className="font-semibold text-text-dark text-sm">{user ? user.username : 'N/A'}</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="font-bold text-text-muted uppercase">Email Address</span>
              <span className="font-semibold text-text-dark text-sm">{user ? user.email : 'N/A'}</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  )
}

export default Settings
