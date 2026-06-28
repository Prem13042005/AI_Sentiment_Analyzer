import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { 
  Database, 
  Brain, 
  BarChart2, 
  TrendingUp, 
  ShieldCheck, 
  Smile, 
  ClipboardCheck,
  CheckCircle,
  FileText,
  Star
} from 'lucide-react'
import Logo from '../components/Logo'
import SemiCircleGauge from '../components/SemiCircleGauge'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  ResponsiveContainer 
} from 'recharts'

const Landing = () => {
  const navigate = useNavigate()

  const trendData = [
    { name: 'Day 1', score: 8.0 },
    { name: 'Day 2', score: 5.6 },
    { name: 'Day 3', score: 7.7 },
    { name: 'Day 4', score: 8.6 },
    { name: 'Day 5', score: 7.7 },
    { name: 'Day 6', score: 5.6 },
    { name: 'Day 7', score: 7.9 },
    { name: 'Day 8', score: 7.7 },
    { name: 'Day 9', score: 9.3 },
    { name: 'Day 10', score: 8.8 },
    { name: 'Day 11', score: 8.0 },
    { name: 'Day 12', score: 7.3 },
    { name: 'Day 13', score: 8.6 },
    { name: 'Day 14', score: 9.1 },
    { name: 'Day 15', score: 6.2 },
    { name: 'Day 16', score: 9.3 },
    { name: 'Day 17', score: 9.7 },
    { name: 'Day 18', score: 8.6 },
    { name: 'Day 19', score: 7.5 }
  ]

  return (
    <div className="min-h-screen bg-gray-bg flex flex-col font-sans">
      <style>{`
        @keyframes float-slow {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-15px) rotate(2deg); }
        }
        @keyframes float-fast {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-8px) rotate(-2deg); }
        }
        .animate-float-slow {
          animation: float-slow 6s ease-in-out infinite;
        }
        .animate-float-fast {
          animation: float-fast 4s ease-in-out infinite;
        }
      `}</style>

      {/* Header / Navbar */}
      <header className="bg-navy px-6 py-4 flex items-center justify-between border-b border-navy-mid sticky top-0 z-50 shadow-md">
        <Logo size="lg" className="text-white" />
        <nav className="flex items-center gap-6">
          <Link to="/" className="bg-teal text-white px-4 py-1.5 rounded-full text-sm font-semibold transition-all">
            Home
          </Link>
          <a href="#features" className="text-text-muted hover:text-white text-sm font-medium transition-colors">
            About Us
          </a>
          <Link to="/register" className="text-text-muted hover:text-white text-sm font-medium transition-colors">
            Register
          </Link>
          <Link to="/login" className="text-text-muted hover:text-white text-sm font-medium transition-colors">
            Login
          </Link>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-navy to-navy-mid py-24 text-center px-6 border-b border-navy-mid flex flex-col items-center">
        
        {/* Floating Icons Left Side */}
        <div className="absolute left-10 top-16 hidden lg:flex flex-col gap-10">
          <div className="w-14 h-14 bg-teal/10 rounded-2xl flex items-center justify-center border border-teal/20 shadow-lg animate-float-slow text-teal">
            <Smile className="h-7 w-7" />
          </div>
          <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center border border-blue-500/20 shadow-lg animate-float-fast text-blue-400 translate-x-8">
            <Database className="h-6 w-6" />
          </div>
          <div className="w-14 h-14 bg-teal/10 rounded-2xl flex items-center justify-center border border-teal/20 shadow-lg animate-float-slow text-teal translate-x-4">
            <ShieldCheck className="h-7 w-7" />
          </div>
        </div>

        {/* Center Content */}
        <div className="max-w-3xl z-10">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
            Unlock the Emotional Pulse <br className="hidden sm:inline" /> of Your Data
          </h1>
          <p className="mt-6 text-lg text-text-muted max-w-2xl mx-auto leading-relaxed">
            Instantly analyze customer feedback, reviews, and social media with advanced NLP models powered by BiLSTM, GRU, CNN-LSTM and DistilBERT.
          </p>
          <div className="mt-10 flex justify-center">
            <button 
              onClick={() => navigate('/register')}
              className="bg-teal hover:bg-teal-dark text-white font-semibold px-8 py-3.5 rounded-lg shadow-lg hover:shadow-teal/20 transition-all duration-300 transform hover:-translate-y-0.5"
            >
              Get Started Free
            </button>
          </div>
        </div>

        {/* Floating Icons Right Side */}
        <div className="absolute right-10 top-16 hidden lg:flex flex-col gap-10">
          <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center border border-blue-500/20 shadow-lg animate-float-fast text-blue-400">
            <TrendingUp className="h-6 w-6" />
          </div>
          <div className="w-14 h-14 bg-teal/10 rounded-2xl flex items-center justify-center border border-teal/20 shadow-lg animate-float-slow text-teal -translate-x-8">
            <Brain className="h-7 w-7" />
          </div>
          <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center border border-blue-500/20 shadow-lg animate-float-fast text-blue-400">
            <Star className="h-6 w-6" />
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section className="bg-white py-20 px-6 border-b border-gray-border" id="features">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-text-dark">How Sentix AI Works</h2>
          <p className="mt-3 text-text-muted max-w-xl mx-auto">
            Get comprehensive, explainable NLP predictions in three simple steps.
          </p>
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            <div className="bg-gray-bg border border-gray-border rounded-xl p-8 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-teal/10 text-teal flex items-center justify-center mb-6">
                <Database className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-text-dark">(1) Collect Data</h3>
              <p className="mt-3 text-sm text-text-mid leading-relaxed">
                Paste text, upload a CSV file containing reviews, or connect using our secure developer API.
              </p>
            </div>
            <div className="bg-gray-bg border border-gray-border rounded-xl p-8 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-teal/10 text-teal flex items-center justify-center mb-6">
                <Brain className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-text-dark">(2) Analyze Input</h3>
              <p className="mt-3 text-sm text-text-mid leading-relaxed">
                Our 5-model ensemble processes your content in milliseconds using deep learning architectures.
              </p>
            </div>
            <div className="bg-gray-bg border border-gray-border rounded-xl p-8 hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-lg bg-teal/10 text-teal flex items-center justify-center mb-6">
                <BarChart2 className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-bold text-text-dark">(3) Generate Insights</h3>
              <p className="mt-3 text-sm text-text-mid leading-relaxed">
                Receive sentiment scores, confidence stats, and word-level contributions powered by LIME.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Real-time Insights Showcase */}
      <section className="bg-gray-bg py-20 px-6 border-b border-gray-border">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-text-dark text-center mb-16">Real-Time Insights</h2>
          
          <div className="bg-white rounded-2xl border border-gray-border shadow-sm p-8 max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-around gap-12">
            
            {/* Left element: Dashboard & Analyzer representation */}
            <div className="flex items-center gap-6 md:w-1/2 border-b md:border-b-0 md:border-r border-gray-border pb-8 md:pb-0 md:pr-8">
              <div className="p-4 bg-teal/10 text-teal rounded-2xl flex-shrink-0">
                <ClipboardCheck className="h-12 w-12" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-text-dark">Dashboard & Analyzer</h3>
                <p className="text-sm text-text-muted mt-2 leading-relaxed">
                  Real-time sentiment score auditing and deep explanation overlays.
                </p>
              </div>
            </div>

            {/* Right element: Two Gauges */}
            <div className="flex flex-col sm:flex-row gap-8 items-center justify-center md:w-1/2">
              <SemiCircleGauge value={85} label="Positive" />
              <SemiCircleGauge value={92} label="Ensemble Acc" />
            </div>
          </div>
        </div>
      </section>

      {/* Key Features & Benefits */}
      <section className="bg-white py-20 px-6 border-b border-gray-border">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-text-dark text-center mb-16">Key Features & Benefits</h2>
          <div className="flex flex-col lg:flex-row items-center gap-12">
            
            {/* Left side: Rating display card */}
            <div className="w-full lg:w-2/5 flex justify-center">
              <div className="bg-gray-bg border border-gray-border rounded-2xl p-8 w-full max-w-[320px] shadow-sm flex flex-col items-center">
                <div className="flex items-center gap-2 mb-4">
                  <div className="flex text-yellow-400">
                    <Star className="h-6 w-6 fill-current" />
                    <Star className="h-6 w-6 fill-current" />
                    <Star className="h-6 w-6 fill-current" />
                    <Star className="h-6 w-6 fill-current" />
                    <Star className="h-6 w-6 fill-current opacity-30" />
                  </div>
                </div>
                <div className="text-4xl font-extrabold text-text-dark">3.8 / 5</div>
                <p className="text-xs text-text-muted mt-2 font-medium">AVERAGE SENTIMENT SCORE</p>
                <div className="w-full bg-gray-200 h-2.5 rounded-full mt-6 overflow-hidden">
                  <div className="bg-teal h-full rounded-full" style={{ width: '76%' }}></div>
                </div>
                <span className="text-[11px] text-text-muted mt-3 font-semibold">76% POSITIVE RATIO</span>
              </div>
            </div>

            {/* Right side: Benefits rows */}
            <div className="w-full lg:w-3/5 flex flex-col gap-8">
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-teal/10 text-teal flex items-center justify-center flex-shrink-0">
                  <CheckCircle className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="font-bold text-text-dark text-md">Improved Customer Understanding</h4>
                  <p className="text-sm text-text-muted mt-1 leading-relaxed">
                    Analyze reviews, feedback forms, and social posts at scale to recognize customer friction points.
                  </p>
                </div>
              </div>
              
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-teal/10 text-teal flex items-center justify-center flex-shrink-0">
                  <ShieldCheck className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="font-bold text-text-dark text-md">Proactive Reputation Management</h4>
                  <p className="text-sm text-text-muted mt-1 leading-relaxed">
                    Monitor brand sentiment in real-time across channels to react before public PR escalations.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-teal/10 text-teal flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="font-bold text-text-dark text-md">Real-Time Market Trends</h4>
                  <p className="text-sm text-text-muted mt-1 leading-relaxed">
                    Track daily sentiment variations surrounding campaigns, competitor actions, or product features.
                  </p>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Sample Sentiment Trends Section */}
      <section className="bg-gray-bg py-20 px-6 border-b border-gray-border">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-text-dark text-center mb-6">Sample Sentiment Trends</h2>
          <p className="text-center text-text-muted max-w-lg mx-auto mb-12">
            Historical overview of aggregate client satisfaction indices captured across model pipelines.
          </p>

          <div className="bg-white border border-gray-border rounded-2xl p-6 md:p-8 shadow-sm">
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis 
                    dataKey="name" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#8896ab', fontSize: 10 }}
                  />
                  <YAxis 
                    domain={[5, 10]} 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#8896ab', fontSize: 10 }}
                  />
                  <Bar 
                    dataKey="score" 
                    fill="#00b8a9" 
                    radius={[4, 4, 0, 0]} 
                    barSize={20}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Footer Banner */}
      <section className="bg-teal py-16 px-6 text-center text-white">
        <h2 className="text-3xl font-bold tracking-tight">Ready to Analyze Sentiment at Enterprise Scale?</h2>
        <p className="mt-4 text-white/80 max-w-xl mx-auto leading-relaxed">
          Create an operator account and start analyzing feedback in seconds. Zero credit cards required.
        </p>
        <button 
          onClick={() => navigate('/register')}
          className="mt-8 bg-navy hover:bg-[#060b13] text-white font-semibold px-8 py-3.5 rounded-lg shadow-lg hover:shadow-navy/20 transition-all duration-300"
        >
          Get Started Free
        </button>
      </section>

      {/* Main Footer */}
      <footer className="bg-white border-t border-gray-border px-6 py-12 text-sm text-text-muted mt-auto">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between gap-10">
          {/* Logo & Copyright */}
          <div className="flex flex-col gap-4">
            <Logo size="sm" />
            <p className="text-xs">&copy; {new Date().getFullYear()} Sentix AI. All rights reserved.</p>
          </div>

          {/* About */}
          <div className="max-w-xs">
            <h5 className="font-bold text-text-dark mb-3">About Sentix AI</h5>
            <p className="leading-relaxed text-xs">
              Sentix AI is an enterprise-grade NLP sentiment intelligence platform performing explainable classification in real-time.
            </p>
          </div>

          {/* Legal Links */}
          <div className="flex flex-col gap-2.5">
            <h5 className="font-bold text-text-dark mb-1">Company</h5>
            <a href="mailto:support@sentix.ai" className="hover:text-text-dark transition-colors text-xs">Contact Support</a>
            <a href="#privacy" className="hover:text-text-dark transition-colors text-xs">Privacy Policy</a>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Landing
