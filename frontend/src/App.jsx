import { useState, useRef, useEffect } from 'react';
import { Send, Database, AlertCircle } from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = { role: 'user', content: query };
    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage.content }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong');
      }

      setMessages((prev) => [...prev, { 
        role: 'assistant', 
        sql: data.sql, 
        summary: data.summary, 
        results: data.results 
      }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', error: err.message }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4 font-mono">
      {/* Header */}
      <header className="pb-4 border-b border-zinc-300 mb-4">
        <h1 className="text-2xl font-bold uppercase tracking-tighter flex items-center gap-2 text-zinc-900">
          <Database className="w-6 h-6" /> FIFA Data Assistant
        </h1>
        <p className="text-sm text-zinc-500 uppercase tracking-widest mt-1">Vectorless RAG Engine</p>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto space-y-6 pb-4 scrollbar-hide">
        {messages.length === 0 && (
          <div className="text-center text-zinc-400 mt-20 uppercase text-sm tracking-widest">
            Awaiting Query Sequence...
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-[85%] rounded-none border p-4 ${
              msg.role === 'user' 
                ? 'bg-zinc-900 text-zinc-50 border-zinc-900' 
                : 'bg-white border-zinc-300 shadow-sm text-zinc-800'
            }`}>
              
              {/* User Message */}
              {msg.role === 'user' && <p>{msg.content}</p>}

              {/* Error Message */}
              {msg.error && (
                <div className="flex items-center gap-2 text-red-600">
                  <AlertCircle className="w-5 h-5" />
                  <p>{msg.error}</p>
                </div>
              )}

              {/* Assistant Response Area */}
              {msg.results && (
                <div className="w-full">
                  
                  {/* AI Text Summary */}
                  {msg.summary && (
                    <p className="mb-4 text-sm text-zinc-800 leading-relaxed font-semibold">
                      {msg.summary}
                    </p>
                  )}

                  <details className="mb-4 text-xs text-zinc-500 cursor-pointer">
                    <summary className="hover:text-zinc-800 transition-colors uppercase font-bold mb-2">View Compiled SQL</summary>
                    <pre className="p-3 bg-zinc-100 border border-zinc-200 mt-2 overflow-x-auto text-zinc-700">
                      <code>{msg.sql}</code>
                    </pre>
                  </details>
                  
                  {msg.results.length === 0 ? (
                    <p className="text-zinc-500 italic">No matching records found.</p>
                  ) : (
                    <div className="overflow-x-auto border border-zinc-200">
                      <table className="w-full text-sm text-left">
                        <thead className="bg-zinc-100 uppercase text-xs text-zinc-600 border-b border-zinc-200">
                          <tr>
                            {Object.keys(msg.results[0]).map((key) => (
                              <th key={key} className="px-4 py-3 font-bold">{key}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {msg.results.map((row, i) => (
                            <tr key={i} className="border-b border-zinc-100 last:border-0 hover:bg-zinc-50 transition-colors">
                              {Object.values(row).map((val, j) => (
                                <td key={j} className="px-4 py-3">{val}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="text-zinc-400 text-sm animate-pulse uppercase tracking-widest">
            Compiling Logic...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="mt-4 relative flex items-center">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="ENTER QUERY EXECUTABLE..."
          disabled={isLoading}
          className="w-full bg-white border-2 border-zinc-900 px-4 py-4 text-zinc-900 focus:outline-none placeholder:text-zinc-400 uppercase text-sm font-bold"
        />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="absolute right-2 p-2 bg-zinc-900 text-white disabled:bg-zinc-300 disabled:text-zinc-500 hover:bg-zinc-700 transition-colors"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
}