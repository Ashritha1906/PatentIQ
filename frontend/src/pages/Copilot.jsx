import React, { useState, useEffect, useRef } from 'react';
import PatentCard from '../components/PatentCard';
import { chatCopilot, deleteCopilotSession } from '../services/api';

const STARTER_PROMPTS = [
  'Find patents for AI systems that detect forest fires using satellite images',
  'Search patents related to non-invasive blood glucose monitoring',
  'Which patent is closest to my idea and why?',
  'Explain the closest patent in simple words',
  'What technology areas are not well covered in the retrieved prior art?',
  'How can I make my idea more differentiated?'
];

export default function Copilot() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'copilot',
      content: 'Welcome to **PatentIQ Research Copilot**. I can help you search prior art, analyze concept whitespace, explain complex claims, and identify technology gaps grounded strictly in patent data.',
      timestamp: Date.now(),
      suggestedFollowups: [
        'Find patents for AI wildfire detection using satellite images',
        'Search patents related to non-invasive glucose monitoring'
      ]
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sourceMode, setSourceMode] = useState('hybrid');
  const [researchContext, setResearchContext] = useState({
    current_query: null,
    intent: 'IDLE',
    patents_count: 0,
    source_mode: 'hybrid',
    selected_patent_id: null,
    technical_concepts: []
  });

  // Voice Interaction State
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);
  const [voiceStatus, setVoiceStatus] = useState('');
  const recognitionRef = useRef(null);

  // Text to Speech State
  const [speakingMsgId, setSpeakingMsgId] = useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    // Generate or load session ID
    const stored = localStorage.getItem('patentiq_copilot_session');
    if (stored) {
      setSessionId(stored);
    } else {
      const newId = 'session_' + Math.random().toString(36).substring(2, 11);
      setSessionId(newId);
      localStorage.setItem('patentiq_copilot_session', newId);
    }

    // Initialize Web Speech API if supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        setVoiceStatus('Listening... Speak now');
      };

      recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        setInputMessage(transcript);
        setVoiceStatus('Transcribing...');
      };

      recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        setIsListening(false);
        setVoiceStatus(event.error === 'not-allowed' ? 'Microphone permission denied.' : 'Voice recognition error.');
        setTimeout(() => setVoiceStatus(''), 4000);
      };

      recognition.onend = () => {
        setIsListening(false);
        setVoiceStatus('');
      };

      recognitionRef.current = recognition;
    } else {
      setSpeechSupported(false);
    }

    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend = null) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isLoading) return;

    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setSpeakingMsgId(null);
    }

    const userMsg = {
      id: 'usr_' + Date.now(),
      role: 'user',
      content: text,
      timestamp: Date.now()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const res = await chatCopilot({
        message: text,
        sessionId,
        sourceMode,
        topK: 5
      });

      if (res.session_id) {
        setSessionId(res.session_id);
        localStorage.setItem('patentiq_copilot_session', res.session_id);
      }

      if (res.research_context) {
        setResearchContext(res.research_context);
      }

      const copilotMsg = {
        id: 'cop_' + Date.now(),
        role: 'copilot',
        content: res.message,
        intent: res.intent,
        patents: res.patents || [],
        selectedPatent: res.selected_patent,
        analysis: res.analysis,
        provenance: res.provenance,
        suggestedFollowups: res.suggested_followups || [],
        disclaimer: res.disclaimer,
        timestamp: Date.now()
      };

      setMessages((prev) => [...prev, copilotMsg]);
    } catch (err) {
      console.error('Copilot request failed:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: 'err_' + Date.now(),
          role: 'copilot',
          isError: true,
          content: 'I encountered an issue processing your query: ' + err.message + '. Please try again or rephrase your inquiry.',
          timestamp: Date.now()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleVoiceInput = () => {
    if (!speechSupported) {
      setVoiceStatus('Voice input unavailable in this browser — please type your question.');
      setTimeout(() => setVoiceStatus(''), 4000);
      return;
    }
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      try {
        recognitionRef.current?.start();
      } catch (e) {
        console.warn('Recognition start error:', e);
      }
    }
  };

  const toggleTextToSpeech = (msgId, text) => {
    if (!window.speechSynthesis) return;

    if (speakingMsgId === msgId) {
      window.speechSynthesis.cancel();
      setSpeakingMsgId(null);
      return;
    }

    window.speechSynthesis.cancel();
    // Clean markdown symbols for cleaner TTS narration
    const cleanText = text
      .replace(/[#*`_~]/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/>\s*/g, '');

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.onend = () => setSpeakingMsgId(null);
    utterance.onerror = () => setSpeakingMsgId(null);

    setSpeakingMsgId(msgId);
    window.speechSynthesis.speak(utterance);
  };

  const handleResetSession = async () => {
    if (sessionId) {
      await deleteCopilotSession(sessionId);
    }
    const newId = 'session_' + Math.random().toString(36).substring(2, 11);
    setSessionId(newId);
    localStorage.setItem('patentiq_copilot_session', newId);
    setResearchContext({
      current_query: null,
      intent: 'IDLE',
      patents_count: 0,
      source_mode: sourceMode,
      selected_patent_id: null,
      technical_concepts: []
    });
    setMessages([
      {
        id: 'welcome_reset',
        role: 'copilot',
        content: 'Session cleared. What patent topic or invention idea would you like to investigate?',
        timestamp: Date.now(),
        suggestedFollowups: STARTER_PROMPTS.slice(0, 3)
      }
    ]);
  };

  return (
    <div className="copilot-container" style={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
      {/* MAIN CONVERSATIONAL COLUMN */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', minWidth: 0 }}>
        {/* TOP BAR / HEADER */}
        <header style={{
          padding: '16px 24px',
          borderBottom: '1px solid var(--border-neutral)',
          background: 'var(--bg-surface)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '20px' }}>🤖</span>
              <h1 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text-primary)' }}>
                PatentIQ Research Copilot
              </h1>
              <span style={{
                fontSize: '11px',
                fontWeight: 600,
                color: 'var(--primary-light)',
                background: 'var(--primary-glow)',
                border: '1px solid var(--border-active)',
                padding: '2px 8px',
                borderRadius: '4px'
              }}>
                Phase 6B Federated RAG
              </span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Ask questions about patents, prior art, technology gaps, and your innovation.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Source Mode Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Source:</span>
              <select
                value={sourceMode}
                onChange={(e) => setSourceMode(e.target.value)}
                style={{
                  background: 'var(--bg-surface-secondary)',
                  border: '1px solid var(--border-neutral)',
                  color: 'var(--text-primary)',
                  fontSize: '12px',
                  padding: '6px 10px',
                  borderRadius: 'var(--border-radius-sm)',
                  cursor: 'pointer'
                }}
              >
                <option value="hybrid">Federated Hybrid (Local + EPO Live)</option>
                <option value="local">Local Corpus (~115k Records)</option>
                <option value="live">EPO Live Only</option>
              </select>
            </div>

            {/* Clear Session Button */}
            <button
              onClick={handleResetSession}
              style={{
                background: 'transparent',
                border: '1px solid var(--border-neutral)',
                color: 'var(--text-secondary)',
                fontSize: '12px',
                padding: '6px 12px',
                borderRadius: 'var(--border-radius-sm)',
                cursor: 'pointer',
                transition: 'all var(--transition-fast)'
              }}
              title="Reset conversation context"
            >
              🔄 New Session
            </button>
          </div>
        </header>

        {/* MESSAGES SCROLL AREA */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }}>
          {messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
                width: '100%'
              }}
            >
              {/* Message Label / Role */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '6px',
                fontSize: '11px',
                color: 'var(--text-muted)'
              }}>
                <span>{msg.role === 'user' ? 'You' : 'PatentIQ Copilot'}</span>
                {msg.intent && (
                  <span style={{
                    fontSize: '10px',
                    color: 'var(--primary-light)',
                    background: 'rgba(99, 102, 241, 0.1)',
                    padding: '1px 6px',
                    borderRadius: '3px'
                  }}>
                    {msg.intent}
                  </span>
                )}
                {/* TTS Speaker Button for Copilot */}
                {msg.role === 'copilot' && !msg.isError && (
                  <button
                    onClick={() => toggleTextToSpeech(msg.id, msg.content)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: speakingMsgId === msg.id ? 'var(--primary-light)' : 'var(--text-muted)',
                      cursor: 'pointer',
                      fontSize: '13px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '3px'
                    }}
                    title={speakingMsgId === msg.id ? 'Stop Narration' : 'Listen with Speech Synthesis'}
                  >
                    {speakingMsgId === msg.id ? '⏹ Stop' : '🔊 Listen'}
                  </button>
                )}
              </div>

              {/* Message Bubble */}
              <div style={{
                maxWidth: msg.role === 'user' ? '75%' : '90%',
                background: msg.role === 'user'
                  ? 'rgba(99, 102, 241, 0.15)'
                  : 'var(--bg-surface)',
                border: msg.role === 'user'
                  ? '1px solid rgba(99, 102, 241, 0.3)'
                  : msg.isError
                    ? '1px solid var(--error)'
                    : '1px solid var(--border-neutral)',
                color: 'var(--text-primary)',
                padding: '16px 20px',
                borderRadius: 'var(--border-radius-md)',
                fontSize: '14px',
                lineHeight: 1.6,
                whiteSpace: 'pre-wrap',
                boxShadow: 'var(--shadow-sm)'
              }}>
                {msg.content}

                {/* Grounding Disclaimer */}
                {msg.disclaimer && (
                  <div style={{
                    marginTop: '12px',
                    paddingTop: '8px',
                    borderTop: '1px solid var(--border-neutral)',
                    fontSize: '11px',
                    color: 'var(--text-muted)',
                    fontStyle: 'italic'
                  }}>
                    ⚖️ {msg.disclaimer}
                  </div>
                )}
              </div>

              {/* Embedded Patent Results if present */}
              {msg.patents && msg.patents.length > 0 && (
                <div style={{ marginTop: '16px', width: '100%', maxWidth: '90%' }}>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    Retrieved Prior Art Documents ({msg.patents.length}):
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {msg.patents.map((p, idx) => (
                      <PatentCard
                        key={p.publication_number || idx}
                        patent={p}
                        highlightClass={idx === 0 ? 'top-match' : ''}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Suggested Follow-Up Prompts */}
              {msg.suggestedFollowups && msg.suggestedFollowups.length > 0 && (
                <div style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '8px',
                  marginTop: '10px',
                  maxWidth: '90%'
                }}>
                  {msg.suggestedFollowups.map((fPrompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(fPrompt)}
                      style={{
                        background: 'var(--bg-surface-secondary)',
                        border: '1px solid var(--border-neutral)',
                        color: 'var(--text-secondary)',
                        fontSize: '12px',
                        padding: '6px 12px',
                        borderRadius: '20px',
                        cursor: 'pointer',
                        transition: 'all var(--transition-fast)'
                      }}
                      onMouseOver={(e) => {
                        e.currentTarget.style.borderColor = 'var(--primary-light)';
                        e.currentTarget.style.color = 'var(--text-primary)';
                      }}
                      onMouseOut={(e) => {
                        e.currentTarget.style.borderColor = 'var(--border-neutral)';
                        e.currentTarget.style.color = 'var(--text-secondary)';
                      }}
                    >
                      💬 {fPrompt}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}

          {/* Loading Indicator */}
          {isLoading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-muted)', fontSize: '13px' }}>
              <div className="spinner-sm" style={{ width: '16px', height: '16px' }}></div>
              <span>PatentIQ Copilot is analyzing patents & prior art context...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* INPUT FOOTER AREA */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid var(--border-neutral)',
          background: 'var(--bg-surface)'
        }}>
          {/* Voice Status Alert */}
          {voiceStatus && (
            <div style={{
              fontSize: '12px',
              color: isListening ? 'var(--primary-light)' : 'var(--warning)',
              marginBottom: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: isListening ? 'var(--primary)' : 'var(--warning)',
                display: 'inline-block',
                animation: isListening ? 'pulse 1.2s infinite' : 'none'
              }}></span>
              {voiceStatus}
            </div>
          )}

          <div style={{
            display: 'flex',
            alignItems: 'flex-end',
            gap: '12px',
            background: 'var(--bg-base)',
            border: '1px solid var(--border-neutral)',
            borderRadius: 'var(--border-radius-md)',
            padding: '8px 12px'
          }}>
            <textarea
              ref={textareaRef}
              rows={2}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask PatentIQ anything about your research... (Enter to send, Shift+Enter for new line)"
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-body)',
                fontSize: '14px',
                resize: 'none',
                outline: 'none',
                lineHeight: 1.5
              }}
            />

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {/* Voice Microphone Button */}
              <button
                type="button"
                onClick={toggleVoiceInput}
                style={{
                  background: isListening ? 'rgba(239, 68, 68, 0.2)' : 'var(--bg-surface-secondary)',
                  border: isListening ? '1px solid var(--error)' : '1px solid var(--border-neutral)',
                  color: isListening ? 'var(--error)' : 'var(--text-secondary)',
                  width: '36px',
                  height: '36px',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '16px',
                  transition: 'all var(--transition-fast)'
                }}
                title={isListening ? 'Stop Listening' : 'Speak Question (Speech-to-Text)'}
              >
                {isListening ? '🔴' : '🎙️'}
              </button>

              {/* Submit Button */}
              <button
                type="button"
                onClick={() => handleSendMessage()}
                disabled={isLoading || !inputMessage.trim()}
                style={{
                  background: inputMessage.trim() ? 'var(--primary)' : 'var(--bg-surface-secondary)',
                  border: 'none',
                  color: inputMessage.trim() ? '#fff' : 'var(--text-muted)',
                  width: '36px',
                  height: '36px',
                  borderRadius: '50%',
                  cursor: inputMessage.trim() && !isLoading ? 'pointer' : 'default',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '15px',
                  transition: 'all var(--transition-fast)'
                }}
                title="Send Research Query"
              >
                ➤
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* RESEARCH CONTEXT PANEL (STEP 21) */}
      <aside style={{
        width: '300px',
        borderLeft: '1px solid var(--border-neutral)',
        background: 'var(--bg-surface)',
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
        padding: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <span style={{ fontSize: '16px' }}>📊</span>
          <h2 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
            Research Context
          </h2>
        </div>

        {/* Current Query */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>
            Active Query
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text-primary)', background: 'var(--bg-surface-secondary)', padding: '8px 12px', borderRadius: '4px', wordBreak: 'break-word' }}>
            {researchContext.current_query || 'No active search topic'}
          </div>
        </div>

        {/* Active Intent */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>
            Current Intent
          </div>
          <div style={{
            fontSize: '12px',
            color: 'var(--primary-light)',
            background: 'var(--primary-glow)',
            border: '1px solid var(--border-active)',
            padding: '4px 8px',
            borderRadius: '4px',
            display: 'inline-block'
          }}>
            {researchContext.intent}
          </div>
        </div>

        {/* Patents in Scope */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>
            Prior Art Context
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text-primary)' }}>
            <strong>{researchContext.patents_count}</strong> patents retrieved
          </div>
        </div>

        {/* Source Mode */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>
            Retrieval Provider
          </div>
          <span style={{
            fontSize: '11px',
            fontWeight: 600,
            color: '#38bdf8',
            background: 'rgba(56, 189, 248, 0.1)',
            padding: '3px 8px',
            borderRadius: '4px',
            border: '1px solid rgba(56, 189, 248, 0.2)'
          }}>
            {researchContext.source_mode.toUpperCase()}
          </span>
        </div>

        {/* Selected Patent */}
        {researchContext.selected_patent_id && (
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>
              Focused Patent
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', background: 'var(--bg-surface-secondary)', padding: '6px 10px', borderRadius: '4px' }}>
              📌 {researchContext.selected_patent_id}
            </div>
          </div>
        )}

        {/* Technical Concepts */}
        {researchContext.technical_concepts && researchContext.technical_concepts.length > 0 && (
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
              Concepts Under Analysis
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {researchContext.technical_concepts.map((concept, idx) => (
                <span
                  key={idx}
                  style={{
                    fontSize: '11px',
                    color: 'var(--text-secondary)',
                    background: 'var(--bg-surface-secondary)',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    border: '1px solid var(--border-neutral)'
                  }}
                >
                  {concept}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Starter Prompts Sidebar Section */}
        <div style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid var(--border-neutral)' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
            Quick Prompts
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {STARTER_PROMPTS.slice(2, 6).map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(prompt)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-secondary)',
                  fontSize: '12px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  padding: '4px 0',
                  lineHeight: 1.4
                }}
                onMouseOver={(e) => e.currentTarget.style.color = 'var(--primary-light)'}
                onMouseOut={(e) => e.currentTarget.style.color = 'var(--text-secondary)'}
              >
                ▸ {prompt}
              </button>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
