import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './index.css';

interface DashboardStats {
  health: { bigquery: number; agent_core_nodes: number; latency_ms: number };
  tasks: Array<{ id: string; type: string; status: string; time: string }>;
  alerts: Array<{ title: string; desc: string }>;
  resources: { compute: number; memory: number; storage: number };
}

interface ChatMessage {
  role: 'user' | 'agent';
  text: string;
  isLoading?: boolean;
}

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  
  // Agent Chat State
  const [chatMessages, setChatMessages] = useState<Array<{role: string, text: string, isLoading?: boolean, chartJson?: any}>>([
    { role: 'agent', text: 'Hệ thống Agent Pipeline đã sẵn sàng. Hãy nhập yêu cầu của bạn (VD: "Phân tích doanh thu").' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [threadId] = useState(`react-thread-${Math.random().toString(36).substring(2, 10)}`);
  const [isHitlMode, setIsHitlMode] = useState(false);
  const [hitlNode, setHitlNode] = useState('');

  // Poll Stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:8001/stats');
        const data = await res.json();
        setStats(data);
      } catch (err) {
        console.error("Error fetching stats:", err);
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  const processChatRequest = async (payloadText: string, isAction: boolean = false) => {
    if (!isAction) {
      setChatMessages(prev => [...prev, { role: 'user', text: payloadText }]);
      setChatInput('');
    }
    
    setChatMessages(prev => [...prev, { role: 'agent', text: '', isLoading: true }]);
    setIsHitlMode(false);
    
    try {
      const res = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: payloadText, thread_id: threadId })
      });
      
      if (!res.body) throw new Error('ReadableStream not supported');
      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      let isDone = false;
      
      while (!isDone) {
        const { value, done } = await reader.read();
        isDone = done;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.replace('data: ', '');
              try {
                const data = JSON.parse(dataStr);
                
                if (data.type === 'status') {
                   setChatMessages(prev => {
                    const newArr = [...prev];
                    const lastMsg = newArr[newArr.length - 1];
                    const msgObj = { role: 'agent', text: `🔹 ${data.content}` };
                    if (lastMsg && lastMsg.isLoading) {
                      newArr[newArr.length - 1] = msgObj;
                    } else {
                      newArr.push(msgObj);
                    }
                    return newArr;
                  });
                } else if (data.type === 'node_finish') {
                   const cleanData = {...data.data};
                   if (cleanData.chart_json) {
                     cleanData.chart_json = "<Plotly JSON Object>";
                   }
                   
                   let chartObj = null;
                   if (data.data && data.data.chart_json && typeof data.data.chart_json === 'string' && data.data.chart_json.trim() !== '') {
                       try {
                           chartObj = JSON.parse(data.data.chart_json);
                       } catch(e) {}
                   }
                   
                   setChatMessages(prev => {
                    const newArr = [...prev];
                    const lastMsg = newArr[newArr.length - 1];
                    const msgObj = { role: 'agent', text: '', node: data.node, nodeData: cleanData, chartJson: chartObj };
                    if (lastMsg && lastMsg.isLoading) {
                      newArr[newArr.length - 1] = msgObj;
                    } else {
                      newArr.push(msgObj);
                    }
                    return newArr;
                  });
                } else if (data.type === 'interrupt') {
                  setHitlNode(data.node);
                  setIsHitlMode(true);
                  setChatMessages(prev => {
                    const newArr = [...prev];
                    const lastMsg = newArr[newArr.length - 1];
                    const msgObj = { role: 'agent', text: `⚠️ TẠM DỪNG TẠI: [${data.node}] - CHỜ HITL DUYỆT` };
                    if (lastMsg && lastMsg.isLoading) {
                      newArr[newArr.length - 1] = msgObj;
                    } else {
                      newArr.push(msgObj);
                    }
                    return newArr;
                  });
                } else if (data.type === 'error') {
                  setChatMessages(prev => {
                    const newArr = [...prev];
                    const lastMsg = newArr[newArr.length - 1];
                    const msgObj = { role: 'agent', text: `❌ LỖI HỆ THỐNG: ${data.content}` };
                    if (lastMsg && lastMsg.isLoading) {
                      newArr[newArr.length - 1] = msgObj;
                    } else {
                      newArr.push(msgObj);
                    }
                    return newArr;
                  });
                } else if (data.type === 'done') {
                   setChatMessages(prev => {
                    const newArr = [...prev];
                    const lastMsg = newArr[newArr.length - 1];
                    const msgObj = { role: 'agent', text: `✅ HOÀN TẤT PIPELINE.` };
                    if (lastMsg && lastMsg.isLoading) {
                      newArr[newArr.length - 1] = msgObj;
                    } else {
                      newArr.push(msgObj);
                    }
                    return newArr;
                  });
                }
              } catch (e) {
                console.error("Parse JSON error for line:", line);
              }
            }
          }
        }
      }
    } catch (err: any) {
      console.error(err);
      setChatMessages(prev => {
        const newArr = [...prev];
        const lastMsg = newArr[newArr.length - 1];
        newArr[newArr.length - 1] = { ...lastMsg, text: lastMsg.text + '\n\n❌ Lỗi kết nối đến Backend.', isLoading: false };
        return newArr;
      });
    }
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || isHitlMode) return;
    await processChatRequest(chatInput.trim(), false);
  };
  
  const handleHitlAction = async (action: string) => {
    setChatMessages(prev => [...prev, { role: 'user', text: `>>> [HITL ACTION]: ${action.toUpperCase()}` }]);
    await processChatRequest(action, true);
  };
  
  // Custom effect to render Plotly
  useEffect(() => {
    chatMessages.forEach((msg, idx) => {
      if (msg.chartJson && document.getElementById(`plot-${idx}`)) {
        try {
          const layout = { 
            ...(msg.chartJson.layout || {}), 
            autosize: true, 
            margin: { l: 40, r: 20, t: 40, b: 60 } 
          };
          // @ts-ignore
          window.Plotly.newPlot(`plot-${idx}`, msg.chartJson.data, layout, { responsive: true, displayModeBar: false });
        } catch(e) {}
      }
    });
  }, [chatMessages]);

  // VIEWS RENDERERS

  const renderMessageContent = (msg: any) => {
    if (msg.isLoading) {
       return <div className="flex items-center gap-2 text-slate-500">...</div>;
    }
    
    if (msg.text && !msg.nodeData) {
       // fallback for text like 🔹 Status, ⚠️ INTERRUPT, etc.
       if (msg.text.includes('❌') || msg.text.includes('⚠️')) {
           return <div className="text-[15px] leading-relaxed whitespace-pre-wrap font-bold text-red-600 overflow-x-auto">{msg.text}</div>;
       }
       if (msg.text.includes('🔹') || msg.text.includes('✅ HOÀN TẤT')) {
           return <div className="text-[15px] leading-relaxed whitespace-pre-wrap font-bold text-blue-600 overflow-x-auto">{msg.text}</div>;
       }
       return <div className="text-[15px] leading-relaxed whitespace-pre-wrap overflow-x-auto">{msg.text}</div>;
    }
    
    // Custom Renderers for specific Nodes
    if (msg.node === 'planner' && msg.nodeData?.plan_json?.subtasks) {
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-blue-800 uppercase text-xs mb-1">📋 Kế Hoạch Phân Tích</h4>
             {msg.nodeData.plan_json.subtasks.map((task: any, idx: number) => (
                <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                   <div className="font-bold text-slate-800">Bước {task.id}: {task.description}</div>
                   <div className="text-slate-500 mt-1">Scope: {task['task scope']}</div>
                </div>
             ))}
          </div>
       );
    }
    if (msg.node === 'supervisor') {
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-indigo-800 uppercase text-xs mb-1">👨‍💼 Giao Việc</h4>
             <div className="bg-indigo-50 text-indigo-900 border border-indigo-200 rounded-lg p-3 font-semibold">
                Đang thực hiện Subtask {msg.nodeData.step_index}: {msg.nodeData.current_subtask}
             </div>
          </div>
       );
    }
    if (msg.node === 'sql_extractor') {
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-green-800 uppercase text-xs mb-1">💻 SQL Query (Data Extractor)</h4>
             {msg.nodeData.sql_query && (
                <pre className="bg-slate-900 text-green-400 p-3 rounded-lg overflow-x-auto text-xs">{msg.nodeData.sql_query}</pre>
             )}
             {msg.nodeData.raw_data && (
                <div className="text-slate-500 italic mt-1 font-semibold">✓ Lấy dữ liệu thành công ({msg.nodeData.raw_data.length > 50 ? "Có dữ liệu" : "Không có dữ liệu"})</div>
             )}
          </div>
       );
    }
    if (msg.node === 'chart_visualizer') {
       const msgIndex = chatMessages.indexOf(msg);
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-pink-800 uppercase text-xs mb-1">📊 Vẽ Biểu Đồ (Visualizer)</h4>
             {msg.chartJson ? (
                <div id={`plot-${msgIndex}`} className="w-full aspect-video min-h-[400px] bg-white rounded border border-pink-100"></div>
             ) : (
                <div className="text-slate-600 bg-pink-50 p-2 rounded border border-pink-100">Không có dữ liệu để vẽ biểu đồ.</div>
             )}
          </div>
       );
    }
    if (msg.node === 'analyst_p2' || msg.node === 'analyst_p1') {
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-orange-800 uppercase text-xs mb-1">📝 Báo Cáo Phân Tích</h4>
             <div className="max-w-none bg-orange-50/50 p-4 rounded-xl border border-orange-100">
                <ReactMarkdown
                  components={{
                    h1: ({node, ...props}) => <h1 className="text-xl font-bold mt-4 mb-2 text-slate-800" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-lg font-bold mt-3 mb-2 text-slate-800" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-base font-bold mt-2 mb-1 text-slate-800" {...props} />,
                    p: ({node, ...props}) => <p className="mb-2 leading-relaxed" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-2" {...props} />,
                    li: ({node, ...props}) => <li className="mb-1" {...props} />,
                    strong: ({node, ...props}) => <strong className="font-bold text-slate-800" {...props} />,
                  }}
                >{msg.nodeData.draft_report || ''}</ReactMarkdown>
             </div>
          </div>
       );
    }
    if (msg.node === 'qa_subtask') {
       const proposal = msg.nodeData.sub_task_proposal;
       let taskObj = null;
       try {
           if (proposal) taskObj = JSON.parse(proposal);
       } catch(e) {}
       
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-teal-800 uppercase text-xs mb-1">🔍 QA Đánh Giá Subtask</h4>
             {taskObj ? (
                 <div className="bg-teal-50 border border-teal-200 rounded-lg p-3">
                     <span className="font-bold text-teal-900">⚠️ Phát hiện điểm bất thường cần Deep-Dive!</span>
                     <p className="mt-2 text-teal-800"><strong>Subtask đề xuất:</strong> {taskObj.description}</p>
                     <p className="text-teal-700 text-xs mt-1">Scope: {taskObj["task scope"]}</p>
                 </div>
             ) : (
                 <div className="bg-slate-50 text-slate-600 border border-slate-200 rounded-lg p-3">
                     ✓ Mọi thứ bình thường, không cần Deep-dive.
                 </div>
             )}
          </div>
       );
    }
    if (msg.node === 'qa_agent') {
       const isApproved = msg.nodeData.qa_status !== 'rejected';
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className={`font-bold uppercase text-xs mb-1 ${isApproved ? 'text-green-800' : 'text-red-800'}`}>
                {isApproved ? '✅ Đạt Yêu Cầu (QA)' : '❌ Cần Làm Lại (QA)'}
             </h4>
             {msg.nodeData.qa_feedback && (
                <div className={`p-3 rounded-lg border ${isApproved ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'}`}>
                   {msg.nodeData.qa_feedback}
                </div>
             )}
          </div>
       );
    }
    
    // Dashboard Nodes
    if (msg.node === 'architect') {
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-purple-800 uppercase text-xs mb-1">📐 Dashboard Blueprint</h4>
             <div className="max-w-none bg-purple-50 p-4 rounded-xl border border-purple-200">
                <ReactMarkdown
                  components={{
                    h1: ({node, ...props}) => <h1 className="text-xl font-bold mt-4 mb-2 text-slate-800" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-lg font-bold mt-3 mb-2 text-slate-800" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-base font-bold mt-2 mb-1 text-slate-800" {...props} />,
                    p: ({node, ...props}) => <p className="mb-2 leading-relaxed" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-2" {...props} />,
                    li: ({node, ...props}) => <li className="mb-1" {...props} />,
                    strong: ({node, ...props}) => <strong className="font-bold text-slate-800" {...props} />,
                  }}
                >{msg.nodeData.draft_report || ''}</ReactMarkdown>
             </div>
          </div>
       );
    }
    if (msg.node === 'section_setup') {
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-indigo-800 uppercase text-xs mb-1">⚙️ Xử Lý Biểu Đồ</h4>
             <div className="bg-slate-50 border border-slate-200 rounded-lg p-3">
                <div className="font-bold text-slate-700">Mục tiêu: {msg.nodeData.current_section_goal}</div>
             </div>
          </div>
       );
    }
    if (msg.node === 'dashboard_filler') {
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-teal-800 uppercase text-xs mb-1">🎨 Cấu Hình Superset</h4>
             <div className="bg-teal-50 border border-teal-200 rounded-lg p-3 text-teal-900">
                <span className="font-bold">Chart: </span> {msg.nodeData.chart_json?.chart_name || "Unknown"} <br/>
                <span className="font-bold">Loại: </span> {msg.nodeData.chart_json?.chart_type || "Unknown"}
             </div>
          </div>
       );
    }
    if (msg.node === 'dashboard_assembler') {
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-orange-800 uppercase text-xs mb-1">🚀 Xuất Bản Dashboard</h4>
             <div className="max-w-none bg-slate-50 p-4 rounded-xl border border-slate-200">
                <ReactMarkdown
                  components={{
                    h1: ({node, ...props}) => <h1 className="text-xl font-bold mt-4 mb-2 text-slate-800" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-lg font-bold mt-3 mb-2 text-slate-800" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-base font-bold mt-2 mb-1 text-slate-800" {...props} />,
                    p: ({node, ...props}) => <p className="mb-2 leading-relaxed" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-2" {...props} />,
                    li: ({node, ...props}) => <li className="mb-1" {...props} />,
                    strong: ({node, ...props}) => <strong className="font-bold text-slate-800" {...props} />,
                  }}
                >{msg.nodeData.draft_report || ''}</ReactMarkdown>
             </div>
          </div>
       );
    }
    if (msg.node === 'router') {
       return (
          <div className="flex flex-col gap-2 text-sm">
             <h4 className="font-bold text-gray-700 uppercase text-xs mb-1">🧭 Router</h4>
             <div className="bg-gray-100 rounded-lg p-2 px-3 inline-block w-max text-gray-800 font-semibold border border-gray-200">
                Intent: {msg.nodeData.current_intent}
             </div>
          </div>
       );
    }
    
    // Default fallback for nodeData
    return (
       <div className="flex flex-col gap-2 text-sm">
          <h4 className="font-bold text-slate-800 uppercase text-xs mb-1">📦 {msg.node}</h4>
          <pre className="bg-slate-50 p-3 rounded-lg overflow-x-auto text-xs text-slate-600 border border-slate-200">
             {JSON.stringify(msg.nodeData, null, 2)}
          </pre>
       </div>
    );
  }

  const renderDashboard = () => {
    if (!stats) {
      return (
        <div className="flex items-center justify-center p-20 text-slate-500">
          <span className="material-symbols-outlined animate-spin text-[48px]">autorenew</span>
        </div>
      );
    }
    return (
      <div className="animate-in fade-in duration-300">
        <header className="mb-section-gap flex justify-between items-end">
          <div>
            <h2 className="text-[48px] leading-[1.1] tracking-[-0.02em] font-bold text-on-background mb-2">Dashboard Overview</h2>
            <p className="text-[18px] leading-[1.6] text-slate-500">Real-time enterprise intelligence and agent operations.</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></span>
            <span className="text-[14px] font-semibold text-slate-500">System Optimal</span>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-section-gap">
          <div className="glass-panel rounded-xl p-card-padding flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <span className="text-[14px] font-semibold text-slate-500">BigQuery Health</span>
              <span className="material-symbols-outlined text-primary-container">database</span>
            </div>
            <div className="text-[32px] leading-[1.2] font-bold text-on-background">{stats.health.bigquery}%</div>
          </div>
          <div className="glass-panel rounded-xl p-card-padding flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <span className="text-[14px] font-semibold text-slate-500">Agent Core</span>
              <span className="material-symbols-outlined text-primary-container">smart_toy</span>
            </div>
            <div className="text-[32px] leading-[1.2] font-bold text-on-background">{stats.health.agent_core_nodes} Nodes</div>
          </div>
          <div className="glass-panel rounded-xl p-card-padding flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <span className="text-[14px] font-semibold text-slate-500">System Latency</span>
              <span className="material-symbols-outlined text-red-500">speed</span>
            </div>
            <div className="text-[32px] leading-[1.2] font-bold text-on-background">{stats.health.latency_ms}ms</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 flex flex-col gap-6">
            <div className="glass-panel rounded-xl p-card-padding">
              <h3 className="text-[24px] font-semibold text-on-background mb-4">Recent Agent Tasks</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-[16px]">
                  <thead>
                    <tr className="text-slate-500 border-b border-slate-200">
                      <th className="py-2 px-4 text-[14px] font-semibold">Task ID</th>
                      <th className="py-2 px-4 text-[14px] font-semibold">Type</th>
                      <th className="py-2 px-4 text-[14px] font-semibold">Status</th>
                      <th className="py-2 px-4 text-[14px] font-semibold">Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.tasks.map(task => (
                      <tr key={task.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-4">{task.id}</td>
                        <td className="py-3 px-4">{task.type}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            task.status === 'Completed' ? 'bg-green-100 text-green-800' :
                            task.status === 'Failed' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
                          }`}>{task.status}</span>
                        </td>
                        <td className="py-3 px-4">{task.time}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div className="flex flex-col gap-6">
            <div className="glass-dark-panel rounded-xl p-card-padding">
              <div className="flex items-center gap-3 mb-4 text-white">
                <span className="material-symbols-outlined text-primary-container">warning</span>
                <h3 className="text-[24px] font-semibold">Live Alerts</h3>
              </div>
              <div className="space-y-4">
                {stats.alerts.map((alert, i) => (
                  <div key={i} className="bg-white/5 p-3 rounded-lg border border-white/10 hover:bg-white/10 transition-colors">
                    <p className="text-[14px] font-semibold text-white mb-1">{alert.title}</p>
                    <p className="text-[12px] text-gray-300">{alert.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderAgentChat = () => (
    <div className="animate-in fade-in duration-300 h-[calc(100vh-200px)] flex flex-col">
      <header className="mb-6 flex justify-between items-end">
        <div>
          <h2 className="text-[48px] leading-[1.1] tracking-[−0.02em] font-bold text-on-background mb-2">Agent Interaction</h2>
          <p className="text-[18px] leading-[1.6] text-slate-500">Giao tiếp trực tiếp với Multi-Agent Pipeline.</p>
        </div>
      </header>
      
      <div className="glass-panel flex-1 rounded-2xl flex flex-col overflow-hidden">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {chatMessages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl p-4 ${
                msg.role === 'user' 
                  ? 'bg-primary-container text-white rounded-br-none shadow-md' 
                  : 'bg-white/80 border border-slate-200 text-slate-800 rounded-bl-none shadow-sm'
              }`}>
                {msg.role === 'agent' && (
                  <div className="flex items-center gap-2 mb-2 border-b border-slate-200/50 pb-2">
                    <span className="material-symbols-outlined text-primary text-sm">smart_toy</span>
                    <span className="font-bold text-xs text-slate-500 uppercase tracking-wider">AI RISSER</span>
                  </div>
                )}
                
                {msg.isLoading ? (
                  <div className="flex items-center gap-2 text-slate-500">
                    <span className="material-symbols-outlined animate-spin">autorenew</span>
                    <span className="text-[14px]">Đang chạy luồng Agent. Vui lòng chờ...</span>
                  </div>
                ) : (
                  renderMessageContent(msg)
                )}
                
                {msg.chartJson && (
                  <div id={`plot-${i}`} className="w-full h-[400px] mt-4 bg-white rounded-xl shadow-sm border border-slate-200 p-2"></div>
                )}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white/50 border-t border-slate-200 flex flex-col gap-4">
          {isHitlMode && (
            <div className="bg-amber-100 border border-amber-300 rounded-xl p-4 shadow-sm flex flex-col gap-3">
              <div className="text-amber-800 font-bold flex items-center gap-2">
                <span className="material-symbols-outlined">warning</span>
                Hệ thống đang tạm dừng tại: [{hitlNode}]
              </div>
              <div className="flex gap-3">
                <button 
                  onClick={() => handleHitlAction('approve')}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-green-700 transition-colors"
                >Duyệt (APPROVE)</button>
                <button 
                  onClick={() => handleHitlAction('reject')}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-red-700 transition-colors"
                >Từ chối (REJECT)</button>
                {hitlNode === 'report_hitl' && (
                  <button 
                    onClick={() => handleHitlAction('subtask')}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold hover:bg-blue-700 transition-colors"
                  >Tạo Subtask mới</button>
                )}
              </div>
            </div>
          )}
          
          <form onSubmit={handleChatSubmit} className="flex gap-4">
            <input 
              type="text" 
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              placeholder={isHitlMode ? "Vui lòng chọn hành động bên trên..." : "Yêu cầu hệ thống phân tích dữ liệu, tạo bảng, build Dashboard..."}
              disabled={isHitlMode}
              className="flex-1 bg-white border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-container text-[16px] shadow-sm disabled:bg-slate-100"
            />
            <button 
              type="submit"
              disabled={chatMessages[chatMessages.length - 1]?.isLoading || !chatInput.trim() || isHitlMode}
              className="bg-primary text-white px-6 py-3 rounded-xl font-bold hover:bg-orange-600 disabled:opacity-50 transition-colors shadow-md flex items-center justify-center"
            >
              <span className="material-symbols-outlined">send</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );

  const renderAirflow = () => (
    <div className="animate-in fade-in duration-300 h-[calc(100vh-200px)] flex flex-col">
      <header className="mb-6 flex justify-between items-end">
        <div>
          <h2 className="text-[48px] leading-[1.1] tracking-[-0.02em] font-bold text-on-background mb-2">Airflow Pipeline</h2>
          <p className="text-[18px] leading-[1.6] text-slate-500">Quản lý các DAGs chạy ngầm.</p>
        </div>
      </header>
      <div className="glass-panel flex-1 rounded-2xl overflow-hidden border border-slate-200">
        <iframe 
          src="https://grant-medline-empire-assessments.trycloudflare.com" 
          className="w-full h-full border-none"
          title="Airflow UI"
        />
      </div>
    </div>
  );

  const renderPlaceholder = (title: string, desc: string, icon: string) => (
    <div className="animate-in fade-in duration-300 flex flex-col items-center justify-center h-[60vh] text-center">
      <div className="w-24 h-24 bg-white/50 rounded-full flex items-center justify-center mb-6 shadow-sm border border-slate-200">
        <span className="material-symbols-outlined text-[48px] text-slate-400">{icon}</span>
      </div>
      <h2 className="text-[32px] font-bold text-slate-700 mb-2">{title}</h2>
      <p className="text-slate-500 max-w-md">{desc}</p>
    </div>
  );

  const renderContent = () => {
    switch (currentView) {
      case 'dashboard': return renderDashboard();
      case 'agent': return renderAgentChat();
      case 'airflow': return renderAirflow();
      case 'superset': return renderPlaceholder('Superset BI', 'Giao diện nhúng từ Superset Cloud sẽ được đặt ở đây.', 'query_stats');
      case 'log': return renderPlaceholder('System Logs', 'Tích hợp Langfuse / System Logs đang được xây dựng.', 'list_alt');
      default: return renderDashboard();
    }
  };

  // Nav Item Helper
  const NavItem = ({ id, icon, label }: { id: string, icon: string, label: string }) => {
    const isActive = currentView === id;
    return (
      <button 
        onClick={() => setCurrentView(id)}
        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all duration-300 ${
          isActive 
            ? 'text-primary font-bold border-r-4 border-primary bg-primary/5' 
            : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
        }`}
      >
        <span className="material-symbols-outlined">{icon}</span>
        <span className="text-[14px] leading-[1.4]">{label}</span>
      </button>
    );
  };

  return (
    <div className="text-on-background min-h-screen overflow-x-hidden flex font-['Plus_Jakarta_Sans']">
      <div className="fixed inset-0 z-[-1] pointer-events-none opacity-30"></div>
      
      {/* SideNavBar */}
      <nav className="glass-panel h-[calc(100vh-5rem)] w-64 rounded-xl m-10 fixed left-0 top-0 flex flex-col gap-stack-md py-page-margin px-gutter z-40 border-white/40 shadow-lg">
        <div className="flex items-center gap-3 mb-8 cursor-pointer" onClick={() => setCurrentView('dashboard')}>
          <img alt="AI RISSER Brand" className="w-12 h-12 rounded-full shadow-sm" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDO7xZEgnUIR5_18eZyLOn0E7eYNbdh7QKWEw1xEmhlhzIMVRdSUPmQCuSXWXrpu6eyajhpsryPQ1GUVy3-L5Wv_t44tfeej9gpzJEt-UJ1T_Rdn1uCwzfiOi6_keN4H8ILjZxBz94ANHd_THmFqZty7JdRd8h3Ym19QVzWpm7XJvURVUwoEKaw-VwjjooBH7A_B1SlnTCU9kO9TqXHj3-ITCSTBZcrhCLGduk01wwMKa6FyS2m_cKXncCNJxIhS764va8" />
          <div>
            <h1 className="text-[24px] leading-[1.3] font-bold tracking-tight">AI RISSER</h1>
            <p className="text-[12px] text-primary font-semibold tracking-wider">ENTERPRISE</p>
          </div>
        </div>
        
        <button 
          onClick={() => setCurrentView('agent')}
          className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-orange-500 to-orange-400 text-white text-[14px] font-bold mb-6 hover:shadow-lg hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2"
        >
          <span className="material-symbols-outlined text-[18px]">forum</span> New Analysis
        </button>
        
        <div className="flex-1 flex flex-col gap-2">
          <NavItem id="dashboard" icon="dashboard" label="Dashboard" />
          <NavItem id="log" icon="list_alt" label="Log Monitor" />
          <NavItem id="agent" icon="smart_toy" label="Agent Chat" />
          <NavItem id="airflow" icon="air" label="Airflow DAGs" />
          <NavItem id="superset" icon="query_stats" label="Superset BI" />
        </div>
      </nav>

      {/* TopNavBar */}
      <nav className="glass-panel h-20 rounded-xl mx-10 mt-10 fixed top-0 right-0 left-80 flex justify-between items-center px-card-padding z-40 border-white/40 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="relative group">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary transition-colors">search</span>
            <input className="bg-white/60 border border-slate-200 rounded-full py-2 pl-10 pr-4 text-[15px] focus:outline-none focus:ring-2 focus:ring-primary/50 w-64 transition-all" placeholder="Search..." type="text" />
          </div>
        </div>
        <div className="hidden md:flex gap-6 items-center">
          <a className="text-primary font-bold border-b-2 border-primary pb-1 text-[14px]" href="#">Overview</a>
          <a className="text-slate-500 font-medium hover:text-slate-800 transition-colors text-[14px]" href="#">System Health</a>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="ml-[340px] mt-[136px] p-10 w-full max-w-7xl">
        {renderContent()}
      </main>

    </div>
  );
}

export default App;
