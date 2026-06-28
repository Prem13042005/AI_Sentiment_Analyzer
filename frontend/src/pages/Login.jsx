import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { login as loginApi, loginWithGoogle as loginWithGoogleApi, getMe, getErrorMessage } from '../services/api'
import Logo from '../components/Logo'
import { ShieldCheck, Brain, Zap, KeyRound } from 'lucide-react'

const Login = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // 1. Authenticate credentials
      const authData = await loginApi(username, password)
      
      // 2. Update Auth state and save to storage
      login(authData)
      
      // 3. Navigate to dashboard
      navigate('/dashboard', { replace: true })
    } catch (err) {
      console.error(err)
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = () => {
    const width = 500
    const height = 650
    const left = window.screen.width / 2 - width / 2
    const top = window.screen.height / 2 - height / 2

    const popup = window.open(
      '',
      'GoogleLoginPopup',
      `width=${width},height=${height},top=${top},left=${left}`
    )
    
    if (!popup) {
      setError('Popup blocker is active. Please enable popups to sign in with Google.')
      return
    }

    popup.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Sign in - Google Accounts</title>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap" rel="stylesheet">
          <style>
            body {
              font-family: 'Roboto', sans-serif;
              background-color: #131314;
              color: #e3e3e3;
              margin: 0;
              display: flex;
              flex-direction: column;
              height: 100vh;
              justify-content: space-between;
              box-sizing: border-box;
              padding: 40px;
            }
            .container {
              max-width: 450px;
              width: 100%;
              margin: 0 auto;
              flex-grow: 1;
              display: flex;
              flex-direction: column;
              justify-content: flex-start;
            }
            .header {
              display: flex;
              align-items: center;
              gap: 12px;
              margin-bottom: 32px;
              font-size: 14px;
              color: #e3e3e3;
            }
            .google-icon {
              width: 20px;
              height: 20px;
            }
            h1 {
              font-size: 28px;
              font-weight: 400;
              margin: 0 0 16px 0;
              color: #e3e3e3;
              text-align: left;
            }
            .subtitle {
              font-size: 14px;
              color: #c4c7c5;
              margin-bottom: 32px;
              text-align: left;
            }
            .subtitle a {
              color: #8ab4f8;
              text-decoration: none;
            }
            .account-list {
              display: flex;
              flex-direction: column;
              border-bottom: 1px solid #444746;
              margin-bottom: 24px;
            }
            .account-item {
              display: flex;
              align-items: center;
              padding: 16px 0;
              border-top: 1px solid #444746;
              cursor: pointer;
              transition: background-color 0.2s;
            }
            .account-item:hover {
              background-color: rgba(255, 255, 255, 0.04);
            }
            .avatar {
              width: 36px;
              height: 36px;
              border-radius: 50%;
              margin-right: 16px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-weight: 500;
              font-size: 16px;
              color: white;
              text-transform: uppercase;
            }
            .account-details {
              display: flex;
              flex-direction: column;
            }
            .account-name {
              font-size: 14px;
              font-weight: 500;
              color: #e3e3e3;
            }
            .account-email {
              font-size: 12px;
              color: #c4c7c5;
              margin-top: 2px;
            }
            .use-other {
              display: flex;
              align-items: center;
              padding: 16px 0;
              border-top: 1px solid #444746;
              cursor: pointer;
              color: #8ab4f8;
              font-size: 14px;
              font-weight: 500;
              transition: background-color 0.2s;
            }
            .use-other:hover {
              background-color: rgba(255, 255, 255, 0.04);
            }
            .use-other-icon {
              width: 36px;
              height: 36px;
              border-radius: 50%;
              margin-right: 16px;
              display: flex;
              align-items: center;
              justify-content: center;
              color: #c4c7c5;
            }
            .form-container {
              display: none;
              margin-top: 16px;
            }
            .input-group {
              margin-bottom: 20px;
              display: flex;
              flex-direction: column;
              gap: 6px;
            }
            label {
              font-size: 12px;
              color: #c4c7c5;
              font-weight: 500;
            }
            input {
              background-color: #1e1f20;
              border: 1px solid #8e918f;
              border-radius: 4px;
              padding: 14px;
              font-size: 14px;
              color: #e3e3e3;
              outline: none;
              box-sizing: border-box;
            }
            input:focus {
              border-color: #8ab4f8;
            }
            .btn {
              background-color: #a8c7fa;
              color: #062e6f;
              border: none;
              padding: 14px;
              border-radius: 100px;
              font-size: 14px;
              font-weight: 500;
              cursor: pointer;
              width: 100%;
              margin-top: 12px;
              transition: background-color 0.2s;
            }
            .btn:hover {
              background-color: #c2e7ff;
            }
            .footer-text {
              font-size: 12px;
              color: #c4c7c5;
              line-height: 1.6;
              margin-top: auto;
            }
            .footer-text a {
              color: #8ab4f8;
              text-decoration: none;
            }
            .bottom-bar {
              display: flex;
              justify-content: space-between;
              align-items: center;
              font-size: 12px;
              color: #c4c7c5;
              border-top: 1px solid transparent;
              margin-top: 40px;
            }
            .bottom-links {
              display: flex;
              gap: 24px;
            }
            .bottom-links a {
              color: #c4c7c5;
              text-decoration: none;
            }
            .bottom-links a:hover {
              color: #e3e3e3;
            }
            .lang-select {
              cursor: pointer;
              display: flex;
              align-items: center;
              gap: 4px;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <svg class="google-icon" viewBox="0 0 24 24" width="20" height="20">
                <path fill="#ea4335" d="M12.24 10.285V14.4h6.887c-.648 2.41-2.519 4.114-5.136 4.114A5.94 5.94 0 0 1 8 12.56a5.94 5.94 0 0 1 5.991-5.96 5.86 5.86 0 0 1 4.12 1.656l3.076-3.076A9.873 9.873 0 0 0 13.991 2C8.473 2 4 6.473 4 11.99s4.473 9.99 9.991 9.99c5.787 0 9.771-4.068 9.771-9.94a8.91 8.91 0 0 0-.164-1.755H12.24Z"/>
              </svg>
              <span>Sign in with Google</span>
            </div>
            
            <div id="accountChooser" style="display: none;">
              <h1>Choose an account</h1>
              <div class="subtitle">to continue to <a href="#">Sentix AI</a></div>
              
              <div class="account-list" id="accountsContainer">
                <!-- Dynamic accounts rendered here -->
              </div>
              
              <div class="use-other" onclick="showForm()">
                <div class="use-other-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                  </svg>
                </div>
                <span>Use another account</span>
              </div>
            </div>

            <div id="formContainer" class="form-container">
              <h1>Sign In</h1>
              <div class="subtitle">to continue to <a href="#">Sentix AI</a></div>
              <form id="loginForm">
                <div class="input-group">
                  <label>Name</label>
                  <input type="text" id="name" required placeholder="Enter name">
                </div>
                <div class="input-group">
                  <label>Email</label>
                  <input type="email" id="email" required placeholder="name@gmail.com">
                </div>
                <button type="submit" class="btn">Next</button>
              </form>
            </div>

            <div class="footer-text">
              Before using this app, you can review Sentix AI's <a href="#">Privacy Policy</a> and <a href="#">Terms of Service</a>.
            </div>
          </div>
          
          <div class="bottom-bar">
            <div class="lang-select">
              English (United States)
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M7 10l5 5 5-5H7z"/></svg>
            </div>
            <div class="bottom-links">
              <a href="#">Help</a>
              <a href="#">Privacy</a>
              <a href="#">Terms</a>
            </div>
          </div>

          <script>
            // Color pool for avatar backgrounds
            const colors = ['#3f51b5', '#7b1fa2', '#12b5cb', '#e91e63', '#009688', '#ff5722'];
            
            let accounts = [];
            try {
              accounts = JSON.parse(localStorage.getItem('google_accounts') || '[]');
            } catch (e) {
              accounts = [];
            }

            if (accounts.length > 0) {
              renderAccounts();
              document.getElementById('accountChooser').style.display = 'block';
            } else {
              document.getElementById('formContainer').style.display = 'block';
            }

            function renderAccounts() {
              const container = document.getElementById('accountsContainer');
              container.innerHTML = '';
              accounts.forEach((acc, index) => {
                const firstLetter = acc.name.charAt(0);
                const color = colors[index % colors.length];
                
                const item = document.createElement('div');
                item.className = 'account-item';
                item.onclick = function() {
                  selectAccount(acc.email, acc.name);
                };
                item.innerHTML = \`
                  <div class="avatar" style="background-color: \${color};">\${firstLetter}</div>
                  <div class="account-details">
                    <span class="account-name">\${acc.name}</span>
                    <span class="account-email">\${acc.email}</span>
                  </div>
                \`;
                container.appendChild(item);
              });
            }

            function selectAccount(email, name) {
              // Save/Update account in list
              let list = [];
              try {
                list = JSON.parse(localStorage.getItem('google_accounts') || '[]');
              } catch (e) {}
              
              if (!list.some(a => a.email === email)) {
                list.push({ email, name });
                localStorage.setItem('google_accounts', JSON.stringify(list));
              }

              window.opener.postMessage(
                { type: 'GOOGLE_AUTH_SUCCESS', email: email, name: name },
                window.location.origin
              );
              window.close();
            }
            
            function showForm() {
              document.getElementById('accountChooser').style.display = 'none';
              document.getElementById('formContainer').style.display = 'block';
            }

            document.getElementById('loginForm').addEventListener('submit', function(e) {
              e.preventDefault();
              const email = document.getElementById('email').value;
              const name = document.getElementById('name').value;
              selectAccount(email, name);
            });
          </script>
        </body>
      </html>
    `)
    popup.document.close()

    const handleMessage = async (event) => {
      if (event.origin !== window.location.origin) return
      if (event.data?.type === 'GOOGLE_AUTH_SUCCESS') {
        window.removeEventListener('message', handleMessage)
        
        setError('')
        setLoading(true)
        try {
          const authData = await loginWithGoogleApi(event.data.email, event.data.name)
          login(authData)
          navigate('/dashboard', { replace: true })
        } catch (err) {
          console.error(err)
          setError(getErrorMessage(err))
        } finally {
          setLoading(false)
        }
      }
    }
    
    window.addEventListener('message', handleMessage)
  }

  return (
    <div className="flex min-h-screen bg-gray-bg select-none">
      
      {/* Left panel: Navy branding info (visible on desktop) */}
      <div className="hidden lg:flex w-[40%] bg-navy flex-col justify-between p-12 text-white border-r border-[#162035]">
        <div>
          <Logo size="lg" className="text-white" />
          <h2 className="mt-16 text-3xl font-bold leading-tight">
            Enterprise Sentiment <br /> Analytics Platform
          </h2>
          <p className="mt-4 text-sm text-text-muted leading-relaxed">
            Harness the power of neural network ensembles and explainable artificial intelligence to understand customer opinion instantly.
          </p>

          {/* Core platform value propositions */}
          <div className="mt-16 flex flex-col gap-6">
            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal/10 text-teal border border-teal/20">
                <Brain className="h-5 w-5" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">Ensemble Inference</h4>
                <p className="text-xs text-text-muted mt-1 leading-relaxed">
                  Weighted combination of BiLSTM, GRU, CNN-LSTM, and DistilBERT architectures.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal/10 text-teal border border-teal/20">
                <Zap className="h-5 w-5" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">Word Attribution</h4>
                <p className="text-xs text-text-muted mt-1 leading-relaxed">
                  Real-time explainable LIME analysis highlighting exact positive/negative contributions.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal/10 text-teal border border-teal/20">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <div>
                <h4 className="font-semibold text-sm">Auditable Logs</h4>
                <p className="text-xs text-text-muted mt-1 leading-relaxed">
                  Fully indexed history tables with CSV export templates for compliance.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="text-xs text-text-muted font-medium">
          &copy; {new Date().getFullYear()} Sentix AI. Enterprise Class NLP.
        </div>
      </div>

      {/* Right panel: Login credentials form */}
      <div className="flex-1 flex flex-col justify-center items-center px-6 sm:px-12 py-12 bg-white">
        <div className="w-full max-w-[420px] flex flex-col">
          {/* Mobile view Logo */}
          <div className="lg:hidden mb-8 self-center">
            <Logo size="lg" />
          </div>

          <h3 className="text-2xl font-bold text-text-dark">Welcome Back</h3>
          <p className="text-sm text-text-muted mt-2">Sign in to your Sentix AI portal</p>

          {/* Form container */}
          <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-5">
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-xs font-semibold text-red-600">
                {error}
              </div>
            )}

            {/* Username Input */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="username" className="text-xs font-bold text-text-dark uppercase tracking-wider">
                Username
              </label>
              <input
                id="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                className="w-full rounded-lg border border-gray-border px-4 py-3 text-sm text-text-dark bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal transition-all"
              />
            </div>

            {/* Password Input */}
            <div className="flex flex-col gap-1.5">
              <div className="flex justify-between items-center">
                <label htmlFor="password" className="text-xs font-bold text-text-dark uppercase tracking-wider">
                  Password
                </label>
              </div>
              <div className="relative">
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full rounded-lg border border-gray-border pl-11 pr-4 py-3 text-sm text-text-dark bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal transition-all"
                />
                <KeyRound className="absolute left-4 top-3.5 h-4.5 w-4.5 text-text-muted" />
              </div>
            </div>

            {/* Submit CTA */}
            <button
              type="submit"
              disabled={loading}
              className="mt-4 bg-teal hover:bg-teal-dark text-white font-semibold py-3.5 rounded-lg shadow-md hover:shadow-teal/20 transition-all flex items-center justify-center disabled:opacity-50"
            >
              {loading ? (
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
              ) : (
                'Sign In'
              )}
            </button>

            {/* Google OAuth Button */}
            <button
              type="button"
              onClick={handleGoogleLogin}
              className="mt-2 flex items-center justify-center gap-2 border border-gray-border hover:bg-gray-50 text-text-dark font-semibold py-3 rounded-lg text-sm transition-all"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Sign In with Google
            </button>
          </form>

          {/* Register reference Link */}
          <p className="mt-8 text-center text-sm text-text-muted">
            Don't have an account?{' '}
            <Link to="/register" className="text-teal font-semibold hover:underline">
              Register here
            </Link>
          </p>
        </div>
      </div>

    </div>
  )
}

export default Login
