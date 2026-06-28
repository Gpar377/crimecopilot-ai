'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Shield, Send, Terminal, Database, Activity, User, Globe, MapPin, 
  Share2, Layers, AlertCircle, FileText, CheckCircle, HelpCircle, Table, Network, Flame,
  Mic, MicOff, BarChart3
} from 'lucide-react';
import dynamic from 'next/dynamic';

const NetworkGraph = dynamic(() => import('../components/NetworkGraph'), {
  ssr: false,
  loading: () => (
    <div className="flex h-[450px] items-center justify-center border border-white/5 bg-[#090b0e] rounded-lg">
      <div className="text-xs font-mono text-[#6b7c93] animate-pulse">Initializing Network Canvas...</div>
    </div>
  )
});

const HotspotMap = dynamic(() => import('../components/HotspotMap'), {
  ssr: false,
  loading: () => (
    <div className="flex h-[450px] items-center justify-center border border-white/5 bg-[#090b0e] rounded-lg">
      <div className="text-xs font-mono text-[#6b7c93] animate-pulse">Loading Map Coordinates...</div>
    </div>
  )
});

const OffenderProfile = dynamic(() => import('../components/OffenderProfile'), {
  ssr: false,
  loading: () => (
    <div className="flex h-[450px] items-center justify-center border border-white/5 bg-[#090b0e] rounded-lg">
      <div className="text-xs font-mono text-[#6b7c93] animate-pulse">Retrieving Offender Records...</div>
    </div>
  )
});

const SociologicalInsights = dynamic(() => import('../components/SociologicalInsights'), {
  ssr: false,
  loading: () => (
    <div className="flex h-[450px] items-center justify-center border border-white/5 bg-[#090b0e] rounded-lg">
      <div className="text-xs font-mono text-[#6b7c93] animate-pulse">Running Correlation Joins...</div>
    </div>
  )
});

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  logs?: string[];
  visualization_type?: string;
  visualization_data?: any;
  evidence_trail?: any[];
}


export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'assistant',
      text: 'Greetings. I am CrimeCopilot AI. Enter an investigation query to analyze Karnataka State Police crime data.'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentLogs, setCurrentLogs] = useState<string[]>([]);
  const [selectedRole, setSelectedRole] = useState<'Investigator' | 'Analyst' | 'Supervisor'>('Analyst');
  const [health, setHealth] = useState<any>(null);
  
  // Voice translation states
  const [isListening, setIsListening] = useState(false);
  const [speechLang, setSpeechLang] = useState<'en-US' | 'kn-IN'>('en-US');

  const handleMicClick = () => {
    if (typeof window === 'undefined') return;
    
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Web Speech API is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = speechLang;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error", event);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
    };

    recognition.start();
  };
  
  // Track currently active visualizer data in right panel
  const [activeVis, setActiveVis] = useState<{
    type: string;
    data: any;
    evidence: any[];
  }>({
    type: 'none',
    data: {},
    evidence: []
  });

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Fetch health check on mount
  useEffect(() => {
    fetchHealth();
  }, []);

  const fetchHealth = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      }
    } catch (e) {
      console.warn("Failed to contact backend health endpoint", e);
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentLogs]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    executeSearch(input);
  };

  const executeSearch = async (userQuery: string) => {
    setInput('');
    setLoading(true);
    setCurrentLogs([]);
    
    // Add user message
    setMessages(prev => [...prev, { sender: 'user', text: userQuery }]);

    let assistantText = '';
    let currentVisualizationType = 'none';
    let currentVisualizationData: any = {};
    let currentEvidenceTrail: any[] = [];

    try {
      // Establish SSE POST stream
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userQuery,
          session_id: "session_001",
          role: selectedRole
        })
      });

      if (!response.body) {
        throw new Error('No readable response body.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last partial line in the buffer
        buffer = lines.pop() || '';

        let currentEvent = '';
        for (const line of lines) {
          if (!line.trim()) continue;

          if (line.startsWith('event:')) {
            currentEvent = line.replace('event:', '').trim();
          } else if (line.startsWith('data:')) {
            const dataStr = line.replace('data:', '').trim();
            try {
              const data = JSON.parse(dataStr);
              
              if (currentEvent === 'log') {
                setCurrentLogs(prev => [...prev, data.message]);
              } else if (currentEvent === 'token') {
                assistantText += data.text;
                // Force state update to render tokens progressively
                setMessages(prev => {
                  const copy = [...prev];
                  const last = copy[copy.length - 1];
                  if (last && last.sender === 'assistant') {
                    // Update current assistant message tokens
                    last.text = assistantText;
                  } else {
                    copy.push({ sender: 'assistant', text: assistantText });
                  }
                  return copy;
                });
              } else if (currentEvent === 'done') {
                currentVisualizationType = data.visualization_type;
                currentVisualizationData = data.visualization_data;
                currentEvidenceTrail = data.evidence_trail;

                // Sync right visualisation panel
                setActiveVis({
                  type: data.visualization_type,
                  data: data.visualization_data,
                  evidence: data.evidence_trail || []
                });
              } else if (currentEvent === 'error') {
                assistantText += `\n[Error: ${data.error}]`;
              }
            } catch (e) {
              console.error("Error parsing event data:", e);
            }
          }
        }
      }

      // Finish chat turn
      setMessages(prev => {
        const copy = [...prev];
        const last = copy[copy.length - 1];
        if (last && last.sender === 'assistant') {
          last.text = assistantText;
          last.logs = currentLogs;
          last.visualization_type = currentVisualizationType;
          last.visualization_data = currentVisualizationData;
          last.evidence_trail = currentEvidenceTrail;
        }
        return copy;
      });

    } catch (e: any) {
      console.error(e);
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: `Error connecting to AI Reasoning server: ${e.message}. Ensure uvicorn is running locally on port 8000.`
      }]);
    } finally {
      setLoading(false);
      setCurrentLogs([]);
      fetchHealth(); // refresh connection status
    }
  };

  // String clean helper
  const cleanString = (str: string) => str.replace(/^\s+|\s+$/g, '');

  return (
    <div className="flex flex-1 h-screen w-screen bg-[#07090b] text-[#f1f3f5] overflow-hidden">
      {/* Official Print Header */}
      <div className="print-only-header">
        <h1>Karnataka State Police</h1>
        <p>CrimeCopilot AI - Case Analysis and Evidence Report | Generated: {new Date().toLocaleString()}</p>
      </div>
      
      {/* 1. LEFT SIDEBAR */}
      <aside className="w-80 flex flex-col border-r border-white/5 bg-[#0a0d11]/80 backdrop-blur-md">
        
        {/* Header Title */}
        <div className="p-6 border-b border-white/5 flex items-center gap-3">
          <Shield className="h-7 w-7 text-brand-yellow text-glow-yellow" />
          <div>
            <h1 className="font-bold text-lg leading-tight tracking-wider text-glow-yellow">CrimeCopilot AI</h1>
            <span className="text-[10px] uppercase font-mono tracking-widest text-[#6b7c93]">KSP Datathon 2026</span>
          </div>
        </div>

        {/* User Role Selector */}
        <div className="p-6 border-b border-white/5 flex flex-col gap-3">
          <label className="text-[11px] font-mono uppercase tracking-wider text-[#6b7c93] flex items-center gap-2">
            <User className="h-3.5 w-3.5" /> Active Role (RBAC)
          </label>
          <div className="grid grid-cols-3 gap-1 bg-[#10141b] p-1 rounded-md border border-white/5">
            {(['Investigator', 'Analyst', 'Supervisor'] as const).map(role => (
              <button
                key={role}
                onClick={() => setSelectedRole(role)}
                className={`py-1.5 rounded text-[11px] font-mono tracking-tight transition-all duration-200 ${
                  selectedRole === role 
                    ? 'bg-brand-yellow text-background font-bold shadow-md shadow-brand-yellow/10' 
                    : 'text-[#9eb1c2] hover:text-[#f1f3f5]'
                }`}
              >
                {role}
              </button>
            ))}
          </div>
        </div>

        {/* System Health Check Status */}
        <div className="p-6 border-b border-white/5 flex flex-col gap-3">
          <span className="text-[11px] font-mono uppercase tracking-wider text-[#6b7c93] flex items-center gap-2">
            <Activity className="h-3.5 w-3.5" /> Engine Telemetry
          </span>
          <div className="bg-[#10141b] rounded-lg p-4 border border-white/5 flex flex-col gap-3 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-[#9eb1c2]">Backend Status:</span>
              <div className="flex items-center gap-1.5">
                <div className={`h-2 w-2 rounded-full ${health ? 'bg-green-500 active-pulse' : 'bg-red-500'}`} />
                <span className="font-mono">{health ? 'ONLINE' : 'OFFLINE'}</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#9eb1c2]">Relational SQL:</span>
              <span className="font-mono uppercase text-[#9eb1c2]">
                {health?.database === 'healthy' ? (
                  <span className="text-green-400">CONNECTED</span>
                ) : (
                  <span className="text-red-400">DISCONNECTED</span>
                )}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#9eb1c2]">Neo4j Graph:</span>
              <span className="font-mono uppercase">
                {health?.environment?.neo4j_configured ? (
                  <span className="text-green-400">ONLINE</span>
                ) : (
                  <span className="text-yellow-400">FALLBACK</span>
                )}
              </span>
            </div>
          </div>
        </div>

        {/* Help Suggestions Panel */}
        <div className="p-6 flex-1 flex flex-col gap-3">
          <span className="text-[11px] font-mono uppercase tracking-wider text-[#6b7c93] flex items-center gap-2">
            <HelpCircle className="h-3.5 w-3.5" /> Sample Queries
          </span>
          <div className="flex flex-col gap-1.5 overflow-y-auto max-h-48 text-[11px] text-[#9eb1c2] font-mono">
            <button 
              onClick={() => setInput("Show vehicle theft cases in Mysuru")}
              className="text-left p-2 rounded bg-white/3 border border-white/5 hover:border-brand-yellow/30 hover:text-[#f1f3f5] transition-all"
            >
              &gt; Vehicle theft in Mysuru
            </button>
            <button 
              onClick={() => setInput("Show connections between vehicle thieves in Bengaluru")}
              className="text-left p-2 rounded bg-white/3 border border-white/5 hover:border-brand-cyan/30 hover:text-[#f1f3f5] transition-all"
            >
              &gt; suspect networks in Bengaluru
            </button>
            <button 
              onClick={() => setInput("Identify crime hotspots near Koramangala")}
              className="text-left p-2 rounded bg-white/3 border border-white/5 hover:border-brand-red/30 hover:text-[#f1f3f5] transition-all"
            >
              &gt; Hotspots near Koramangala
            </button>
          </div>
        </div>
      </aside>

      {/* 2. MIDDLE CHAT PANE */}
      <main className="flex-1 flex flex-col bg-[#07090b]">
        {/* Chat Header */}
        <div className="h-16 border-b border-white/5 px-8 flex items-center justify-between backdrop-blur-md bg-[#07090b]/80">
          <div className="flex items-center gap-2">
            <Terminal className="h-4.5 w-4.5 text-brand-cyan text-glow-cyan" />
            <span className="font-mono text-sm tracking-wider uppercase text-glow-cyan">Copilot Command Console</span>
          </div>
        </div>

        {/* Chat Log History */}
        <div className="flex-1 p-8 overflow-y-auto flex flex-col gap-6 scrollbar">
          {messages.map((m, idx) => (
            <div 
              key={idx} 
              className={`flex flex-col max-w-[85%] rounded-lg p-5 border transition-all ${
                m.sender === 'user'
                  ? 'self-end bg-[#111622] border-white/10 text-right'
                  : 'self-start bg-[#0d1117]/50 border-white/5'
              }`}
            >
              <div className="text-[10px] uppercase font-mono tracking-widest text-[#6b7c93] mb-1.5">
                {m.sender === 'user' ? selectedRole : 'AI Intelligence Analyst'}
              </div>
              <div className="text-sm leading-relaxed whitespace-pre-wrap font-sans text-left">
                {m.text}
              </div>
              
              {/* Evidence trail tags if present */}
              {m.evidence_trail && m.evidence_trail.length > 0 && (
                <div className="mt-3.5 pt-3.5 border-t border-white/5 flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] font-mono text-brand-cyan tracking-wider uppercase flex items-center gap-1.5">
                    <Database className="h-3 w-3" /> Grounds Verified:
                  </span>
                  {m.evidence_trail.filter(ev => ev.type !== 'database_query').map((ev, evIdx) => (
                    <span 
                      key={evIdx}
                      className="px-2 py-0.5 rounded bg-brand-cyan/10 border border-brand-cyan/20 text-[9px] font-mono text-brand-cyan cursor-pointer hover:bg-brand-cyan/20 transition-all"
                      onClick={() => setActiveVis({
                        type: m.visualization_type || 'none',
                        data: m.visualization_data,
                        evidence: m.evidence_trail || []
                      })}
                    >
                      {ev.number || ev.name || ev.id}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}

          {/* Real-time Progress Log SSE updates */}
          {loading && (
            <div className="self-start bg-brand-cyan/5 border border-brand-cyan/15 rounded-lg p-5 flex flex-col gap-2 max-w-[85%] font-mono text-xs text-brand-cyan">
              <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-brand-cyan/80">
                <Activity className="h-3.5 w-3.5 active-pulse" /> Agent Processing Stream
              </div>
              <div className="flex flex-col gap-1 mt-1 text-[#9eb1c2]">
                {currentLogs.map((log, logIdx) => (
                  <div key={logIdx} className="flex items-center gap-2">
                    <span className="text-brand-cyan">&gt;</span> {log}
                  </div>
                ))}
                <div className="flex items-center gap-2 text-brand-cyan/50 italic">
                  <span className="text-brand-cyan">&gt;</span> reasoning in progress...
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Form */}
        <div className="p-8 border-t border-white/5 bg-[#07090b]/80 backdrop-blur-md">
          <form onSubmit={handleSubmit} className="flex flex-col gap-2">
            <div className="flex items-center gap-3">
              {/* Language Selector for Voice */}
              <button
                type="button"
                onClick={() => setSpeechLang(prev => prev === 'en-US' ? 'kn-IN' : 'en-US')}
                className="bg-[#10141b] border border-white/5 hover:border-white/10 rounded-lg px-3 py-3.5 text-xs font-mono text-[#9eb1c2] hover:text-[#f1f3f5] transition-all cursor-pointer select-none"
                title="Toggle Voice Language (English / Kannada)"
              >
                {speechLang === 'en-US' ? 'EN' : 'ಕನ್ನಡ'}
              </button>

              {/* Speech Recognition Button */}
              <button
                type="button"
                onClick={handleMicClick}
                className={`border rounded-lg p-3.5 transition-all cursor-pointer ${
                  isListening 
                    ? 'bg-red-500/10 border-red-500 text-red-500 animate-pulse' 
                    : 'bg-[#10141b] border-white/5 hover:border-white/10 text-[#9eb1c2] hover:text-[#f1f3f5]'
                }`}
                title="Trigger Speech Input"
              >
                {isListening ? <MicOff className="h-4.5 w-4.5" /> : <Mic className="h-4.5 w-4.5" />}
              </button>

              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder={
                  isListening 
                    ? "Listening..." 
                    : speechLang === 'kn-IN'
                      ? "ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಿ (e.g. ವಾಹನ ಕಳ್ಳತನ ಪ್ರಕರಣಗಳನ್ನು ತೋರಿಸಿ)..."
                      : "Ask CrimeCopilot: 'Show vehicle theft cases in Mysuru'..."
                }
                disabled={loading}
                className="flex-1 bg-[#10141b] border border-white/5 rounded-lg py-3.5 px-5 text-sm font-sans focus:outline-none focus:border-brand-cyan/40 transition-colors disabled:opacity-60 placeholder-[#6b7c93]"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="bg-brand-cyan hover:bg-brand-cyan/80 text-background p-3.5 rounded-lg transition-all shadow-md shadow-brand-cyan/10 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                <Send className="h-4.5 w-4.5" />
              </button>
            </div>
            {isListening && (
              <div className="text-[10px] font-mono text-red-400/80 pl-[125px]">
                Speak clearly. Web Speech Engine is recording in {speechLang === 'en-US' ? 'English' : 'Kannada (Karnataka)'}...
              </div>
            )}
          </form>
        </div>
      </main>

      {/* 3. RIGHT INTERACTIVE VISUALIZER PANEL */}
      <section className="w-[500px] border-l border-white/5 flex flex-col bg-[#07090b]/50">
        
        {/* Panel Header */}
        <div className="h-16 border-b border-white/5 px-6 flex items-center justify-between backdrop-blur-md">
          <div className="flex items-center gap-2 font-mono text-sm tracking-wider uppercase text-glow-yellow">
            {activeVis.type === 'table' && <Table className="h-4.5 w-4.5 text-brand-yellow text-glow-yellow" />}
            {activeVis.type === 'graph' && <Network className="h-4.5 w-4.5 text-brand-cyan text-glow-cyan" />}
            {activeVis.type === 'heatmap' && <Flame className="h-4.5 w-4.5 text-brand-red text-glow-red" />}
            {activeVis.type === 'profile' && <User className="h-4.5 w-4.5 text-red-500 text-glow-red" />}
            {activeVis.type === 'insights' && <BarChart3 className="h-4.5 w-4.5 text-brand-cyan text-glow-cyan" />}
            {activeVis.type === 'none' && <Layers className="h-4.5 w-4.5 text-[#6b7c93]" />}
            <span>Workspace Visualizations</span>
          </div>
          <button
            onClick={() => window.print()}
            className="no-print bg-[#10141b] border border-white/5 hover:border-brand-yellow/30 text-xs font-mono text-[#9eb1c2] hover:text-brand-yellow px-3 py-1.5 rounded transition-all cursor-pointer flex items-center gap-1.5"
            title="Export Report to PDF"
          >
            <FileText className="h-3.5 w-3.5" />
            Export PDF
          </button>
        </div>

        {/* Visualizer Display Area */}
        <div className="flex-1 p-6 overflow-y-auto flex flex-col gap-6 scrollbar">
          
          {/* Table Visualizer */}
          {activeVis.type === 'table' && activeVis.data?.rows && (
            <div className="glass-panel rounded-lg overflow-hidden border border-white/5 shadow-2xl flex flex-col">
              <div className="p-4 bg-white/3 border-b border-white/5 font-mono text-xs uppercase text-[#9eb1c2] tracking-wider">
                Relational SQL Records ({activeVis.data.rows.length} rows)
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-white/5 bg-[#10141b]">
                      {activeVis.data.headers?.map((h: string, hIdx: number) => (
                        <th key={hIdx} className="p-3.5 font-semibold text-[#9eb1c2] uppercase tracking-wider font-mono">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {activeVis.data.rows.map((row: any[], rIdx: number) => (
                      <tr key={rIdx} className="border-b border-white/5 hover:bg-white/2">
                        {row.map((cell: any, cIdx: number) => (
                          <td key={cIdx} className="p-3.5 text-[#f1f3f5] font-sans break-words max-w-xs">{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Graph Network Visualizer */}
          {activeVis.type === 'graph' && activeVis.data?.nodes && (
            <NetworkGraph 
              data={activeVis.data} 
              onNodeClick={(id, type, label) => {
                if (type === 'Accused') {
                  const suspectName = label.split(' (')[0];
                  executeSearch(`Show profile for ${suspectName}`);
                }
              }}
            />
          )}

          {/* Heatmap Visualizer */}
          {activeVis.type === 'heatmap' && activeVis.data?.points && (
            <HotspotMap data={activeVis.data} />
          )}

          {/* Profile Visualizer */}
          {activeVis.type === 'profile' && activeVis.data && (
            <OffenderProfile data={activeVis.data} />
          )}

          {/* Insights Visualizer */}
          {activeVis.type === 'insights' && activeVis.data && (
            <SociologicalInsights data={activeVis.data} />
          )}

          {/* Placeholder when None */}
          {activeVis.type === 'none' && (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 border border-dashed border-white/5 rounded-xl h-[400px]">
              <Layers className="h-10 w-10 text-[#6b7c93]/50 mb-3" />
              <h3 className="text-sm font-bold text-[#9eb1c2]">No Active Visualization</h3>
              <p className="text-xs text-[#6b7c93] max-w-[280px] mt-1.5 font-sans leading-relaxed">
                Submit an investigation query (e.g. search cases or connections) to generate SQL and Graph data rendering panels.
              </p>
            </div>
          )}

          {/* 4. GROUNDED EVIDENCE TRAIL */}
          {activeVis.evidence && activeVis.evidence.length > 0 && (
            <div className="flex flex-col gap-3 mt-2">
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#6b7c93] flex items-center gap-2">
                <FileText className="h-3.5 w-3.5" /> Grounded Evidence Trail
              </span>
              
              <div className="bg-[#10141b] rounded-lg border border-white/5 p-4 flex flex-col gap-4 font-mono text-xs max-h-96 overflow-y-auto scrollbar">
                
                {/* SQL/Cypher statements run */}
                {activeVis.evidence.filter(ev => ev.type === 'database_query').map((ev, qIdx) => (
                  <div key={qIdx} className="flex flex-col gap-1.5 pb-3 border-b border-white/5 last:border-b-0">
                    <div className="text-[10px] text-brand-yellow font-bold uppercase tracking-wider flex items-center gap-1.5">
                      <Terminal className="h-3.5 w-3.5" /> Executed Command:
                    </div>
                    <div className="bg-[#090c10] p-3 rounded border border-white/5 text-[11px] text-[#f1f3f5] overflow-x-auto whitespace-pre-wrap leading-relaxed">
                      {ev.query}
                    </div>
                    {ev.parameters && Object.keys(ev.parameters).length > 0 && (
                      <div className="text-[9px] text-[#6b7c93] mt-0.5">
                        Parameters: {JSON.stringify(ev.parameters)}
                      </div>
                    )}
                  </div>
                ))}

                {/* Primary database entities matched */}
                <div className="flex flex-col gap-2 pt-1">
                  <div className="text-[10px] text-brand-cyan font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <CheckCircle className="h-3.5 w-3.5" /> Sourced Records:
                  </div>
                  <div className="flex flex-col gap-1.5">
                    {activeVis.evidence.filter(ev => ev.type !== 'database_query').map((ev, rIdx) => (
                      <div key={rIdx} className="bg-[#090c10] px-3 py-2 rounded border border-white/5 flex items-center justify-between text-[11px]">
                        <span className="text-[#f1f3f5] font-sans">
                          {ev.type === 'fir_record' && `FIR Case: ${ev.number}`}
                          {ev.type === 'accused_record' && `Accused: ${ev.name}`}
                          <span className="text-[10px] text-[#6b7c93] font-mono block mt-0.5">ID Ref: {ev.id}</span>
                        </span>
                        <span className="px-2 py-0.5 rounded bg-green-500/10 border border-green-500/20 text-[9px] text-green-400 font-mono tracking-tight uppercase">
                          VERIFIED
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            </div>
          )}

        </div>
      </section>
      
    </div>
  );
}
