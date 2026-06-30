import React, { useState, useRef, useEffect, useCallback } from 'react';
import { streamResearch } from '../services/api';

// ── Suggested prompts shown when the chat is empty ─────────────────
const SUGGESTIONS = [
  'Analyse my current portfolio risk and concentration',
  'Compare my allocation to Nifty 50 sector weights',
  'What macroeconomic risks should I watch for my holdings?',
  'Explain the optimizer\'s recommendation vs my current weights',
  'Which of my stocks have the highest downside risk?',
  'Suggest rebalancing steps to reach the optimal allocation',
];

// ── Simple markdown-to-JSX renderer (bold, bullets, headers) ───────
function renderMarkdown(text) {
  const lines = text.split('\n');
  return lines.map((line, i) => {
    // Headers
    if (line.startsWith('### ')) return <div key={i} style={{ color: 'var(--accent)', fontWeight: 700, marginTop: '0.8rem', marginBottom: '0.2rem' }}>{line.slice(4)}</div>;
    if (line.startsWith('## '))  return <div key={i} style={{ color: 'var(--accent)', fontWeight: 700, marginTop: '1rem', marginBottom: '0.3rem', fontSize: '1.05em' }}>{line.slice(3)}</div>;
    if (line.startsWith('# '))   return <div key={i} style={{ color: 'var(--accent)', fontWeight: 700, marginTop: '1rem', marginBottom: '0.4rem', fontSize: '1.1em' }}>{line.slice(2)}</div>;

    // Bullet points
    if (line.match(/^[\-\*•]\s/)) {
      const content = line.slice(2);
      return (
        <div key={i} style={{ display: 'flex', gap: '0.5rem', marginTop: '0.2rem' }}>
          <span style={{ color: 'var(--success)', flexShrink: 0 }}>▸</span>
          <span>{inlineBold(content)}</span>
        </div>
      );
    }

    // Numbered list
    if (line.match(/^\d+\.\s/)) {
      const match = line.match(/^(\d+)\.\s(.*)/);
      return (
        <div key={i} style={{ display: 'flex', gap: '0.5rem', marginTop: '0.2rem' }}>
          <span style={{ color: 'var(--accent)', flexShrink: 0, minWidth: '1.5rem' }}>{match[1]}.</span>
          <span>{inlineBold(match[2])}</span>
        </div>
      );
    }

    // Horizontal rule
    if (line.match(/^---+$/)) return <hr key={i} style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: '0.6rem 0' }} />;

    // Empty line
    if (!line.trim()) return <div key={i} style={{ height: '0.4rem' }} />;

    // Normal text
    return <div key={i}>{inlineBold(line)}</div>;
  });
}

function inlineBold(text) {
  const parts = text.split(/\*\*(.*?)\*\*/g);
  return parts.map((part, i) =>
    i % 2 === 1
      ? <strong key={i} style={{ color: 'var(--accent)' }}>{part}</strong>
      : part
  );
}

// ── Message bubble ──────────────────────────────────────────────────
function Message({ role, text, isStreaming }) {
  const isUser = role === 'user';
  return (
    <div style={{
      marginBottom: '1.2rem',
      paddingBottom: '1rem',
      borderBottom: '1px solid rgba(255,153,0,0.15)',
    }}>
      {/* Role label */}
      <div style={{
        fontSize: '0.7rem',
        marginBottom: '0.4rem',
        color: isUser ? 'var(--text-secondary)' : 'var(--success)',
        letterSpacing: '2px',
      }}>
        {isUser ? '▶ USER' : '◈ AI ANALYST'}
      </div>

      {/* Message body */}
      <div style={{
        fontSize: '0.85rem',
        lineHeight: '1.7',
        color: isUser ? 'var(--text-primary)' : '#e8e8e8',
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
      }}>
        {isUser ? text : renderMarkdown(text)}
        {isStreaming && (
          <span style={{
            display: 'inline-block',
            width: '8px',
            height: '14px',
            background: 'var(--accent)',
            marginLeft: '2px',
            verticalAlign: 'text-bottom',
            animation: 'blink 0.7s step-end infinite',
          }} />
        )}
      </div>
    </div>
  );
}

// ── Main component ──────────────────────────────────────────────────
const ResearchPanel = ({ portfolioContext }) => {
  const [messages, setMessages]       = useState([]);
  const [input, setInput]             = useState('');
  const [isStreaming, setIsStreaming]  = useState(false);
  const [hasContext, setHasContext]   = useState(false);
  const abortRef    = useRef(null);
  const scrollRef   = useRef(null);
  const inputRef    = useRef(null);

  // Track whether we have optimizer results to pass
  useEffect(() => {
    setHasContext(!!portfolioContext);
  }, [portfolioContext]);

  // Auto-scroll to bottom on new content
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendQuery = useCallback((query) => {
    if (!query.trim() || isStreaming) return;

    // Add user message
    const userMsg = { role: 'user', text: query.trim() };
    const aiMsg   = { role: 'assistant', text: '' };

    setMessages(prev => [...prev, userMsg, aiMsg]);
    setInput('');
    setIsStreaming(true);

    // Build history (exclude the empty AI message we just added)
    const history = messages.map(m => ({ role: m.role, text: m.text }));

    // Start streaming
    const abort = streamResearch(
      query.trim(),
      portfolioContext,
      history,
      // onChunk
      (chunk) => {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            text: updated[updated.length - 1].text + chunk,
          };
          return updated;
        });
      },
      // onDone
      () => {
        setIsStreaming(false);
        abortRef.current = null;
      },
      // onError
      (err) => {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            text: `⚠ Error: ${err}`,
          };
          return updated;
        });
        setIsStreaming(false);
        abortRef.current = null;
      },
    );

    abortRef.current = abort;
  }, [isStreaming, messages, portfolioContext]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendQuery(input);
    }
  };

  const handleStop = () => {
    if (abortRef.current) { abortRef.current(); abortRef.current = null; }
    setIsStreaming(false);
  };

  const handleClear = () => {
    if (isStreaming) handleStop();
    setMessages([]);
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      minHeight: '520px',
      maxHeight: '780px',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '1px solid var(--border-color)',
        paddingBottom: '0.6rem',
        marginBottom: '0.8rem',
      }}>
        <div>
          <div style={{ color: 'var(--accent)', fontWeight: 700, fontSize: '1rem' }}>
            ◈ AI RESEARCH
          </div>
          <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            POWERED BY GEMINI 2.0 FLASH
            {hasContext
              ? <span style={{ color: 'var(--success)', marginLeft: '0.5rem' }}>· PORTFOLIO CONTEXT LOADED</span>
              : <span style={{ color: 'var(--text-secondary)', marginLeft: '0.5rem' }}>· RUN OPTIMIZER FOR CONTEXT</span>
            }
          </div>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClear}
            style={{
              background: 'none', border: '1px solid var(--text-secondary)',
              color: 'var(--text-secondary)', cursor: 'pointer',
              fontFamily: 'inherit', fontSize: '0.65rem',
              padding: '3px 8px', letterSpacing: '1px',
            }}
          >
            [ CLR ]
          </button>
        )}
      </div>

      {/* Message area */}
      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          paddingRight: '4px',
          marginBottom: '0.8rem',
          scrollbarWidth: 'thin',
          scrollbarColor: 'var(--border-color) transparent',
        }}
      >
        {messages.length === 0 ? (
          /* Empty state — show suggestions */
          <div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginBottom: '1rem' }}>
              {hasContext
                ? 'PORTFOLIO LOADED. ASK ANYTHING ABOUT YOUR HOLDINGS:'
                : 'ASK ABOUT ANY INDIAN STOCK OR MARKET TOPIC:'}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  onClick={() => sendQuery(s)}
                  disabled={isStreaming}
                  style={{
                    background: 'transparent',
                    border: '1px solid rgba(255,153,0,0.3)',
                    color: 'var(--text-secondary)',
                    cursor: 'pointer',
                    fontFamily: 'inherit',
                    fontSize: '0.75rem',
                    padding: '0.5rem 0.8rem',
                    textAlign: 'left',
                    transition: 'all 0.15s',
                    letterSpacing: '0.3px',
                  }}
                  onMouseEnter={e => {
                    e.target.style.borderColor = 'var(--accent)';
                    e.target.style.color = 'var(--accent)';
                  }}
                  onMouseLeave={e => {
                    e.target.style.borderColor = 'rgba(255,153,0,0.3)';
                    e.target.style.color = 'var(--text-secondary)';
                  }}
                >
                  ▷ {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <Message
              key={i}
              role={msg.role}
              text={msg.text}
              isStreaming={isStreaming && i === messages.length - 1 && msg.role === 'assistant'}
            />
          ))
        )}
      </div>

      {/* Input bar */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        borderTop: '1px solid var(--border-color)',
        paddingTop: '0.7rem',
        alignItems: 'flex-end',
      }}>
        <div style={{
          flex: 1,
          display: 'flex',
          alignItems: 'flex-end',
          border: '1px solid var(--border-color)',
          background: '#0a0a0a',
        }}>
          <span style={{
            color: 'var(--success)',
            padding: '0.5rem 0.4rem 0.5rem 0.6rem',
            fontSize: '0.85rem',
            flexShrink: 0,
            userSelect: 'none',
          }}>▶</span>
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isStreaming}
            placeholder={isStreaming ? 'receiving response...' : 'ask about stocks, sectors, or your portfolio...'}
            rows={1}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-primary)',
              fontFamily: 'inherit',
              fontSize: '0.82rem',
              padding: '0.5rem 0.4rem',
              resize: 'none',
              lineHeight: '1.4',
              maxHeight: '80px',
              overflowY: 'auto',
            }}
            onInput={e => {
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 80) + 'px';
            }}
          />
        </div>

        {isStreaming ? (
          <button
            onClick={handleStop}
            style={{
              background: 'var(--danger)',
              border: 'none',
              color: '#000',
              cursor: 'pointer',
              fontFamily: 'inherit',
              fontWeight: 700,
              fontSize: '0.7rem',
              padding: '0.5rem 0.8rem',
              letterSpacing: '1px',
              flexShrink: 0,
              height: '36px',
            }}
          >
            ■ STOP
          </button>
        ) : (
          <button
            onClick={() => sendQuery(input)}
            disabled={!input.trim()}
            style={{
              background: input.trim() ? 'var(--accent)' : 'transparent',
              border: '1px solid var(--accent)',
              color: input.trim() ? '#000' : 'var(--accent)',
              cursor: input.trim() ? 'pointer' : 'default',
              fontFamily: 'inherit',
              fontWeight: 700,
              fontSize: '0.7rem',
              padding: '0.5rem 0.8rem',
              letterSpacing: '1px',
              flexShrink: 0,
              height: '36px',
              transition: 'all 0.15s',
            }}
          >
            SEND ▶
          </button>
        )}
      </div>

      {/* Hint */}
      <div style={{ fontSize: '0.6rem', color: 'var(--text-secondary)', marginTop: '0.3rem', opacity: 0.7 }}>
        ENTER to send · SHIFT+ENTER for newline · conversations are not stored
      </div>
    </div>
  );
};

export default ResearchPanel;
