import React, { useState, useRef, useEffect } from 'react'
import MarkdownRenderer from './MarkdownRenderer'
import './AIChat.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
}

interface AIChatProps {
  flightId?: string
  flightData?: any
  onClose?: () => void
  minimized?: boolean
  onMinimize?: () => void
  isOpen?: boolean
  onToggle?: () => void
}

const AIChat: React.FC<AIChatProps> = ({
  flightId,
  flightData,
  onClose,
  minimized = false,
  onMinimize,
  isOpen = false,
  onToggle
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI cargo analytics assistant. I can help you:\n\n- Answer questions about flights and cargo capacity\n- Explain predictions and insights\n- Find flights with specific criteria\n- Provide cargo optimization recommendations\n- Generate alerts and reports\n\nHow can I help you today?'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiStatus, setAiStatus] = useState<string>('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    
    // Determine AI status based on user query
    const query = userMessage.content.toLowerCase()
    let status = 'Analyzing your request...'
    
    if (query.includes('flight') || query.includes('show') || query.includes('find')) {
      status = 'Searching flight database...'
    } else if (query.includes('capacity') || query.includes('cargo') || query.includes('predict')) {
      status = 'Calculating cargo capacity...'
    } else if (query.includes('route') || query.includes('statistics') || query.includes('stats')) {
      status = 'Analyzing route data...'
    } else if (query.includes('airport') || query.includes('airport')) {
      status = 'Fetching airport information...'
    } else if (query.includes('optimize') || query.includes('recommend')) {
      status = 'Generating recommendations...'
    } else if (query.includes('explain') || query.includes('why') || query.includes('how')) {
      status = 'Generating explanation...'
    } else if (query.includes('risk') || query.includes('alert')) {
      status = 'Assessing risk levels...'
    } else {
      status = 'Processing your query...'
    }
    
    setAiStatus(status)

    try {
      const conversationHistory = messages.map(m => ({
        role: m.role,
        content: m.content
      }))

      const context: any = {}
      if (flightId) {
        context.flight_id = flightId
      }
      if (flightData) {
        context.flight_data = flightData
      }

      const response = await fetch('http://localhost:8000/api/v1/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_history: conversationHistory,
          context: context
        })
      })

      if (!response.ok) {
        // Try to get error details from response
        let errorMessage = 'Failed to get response'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          errorMessage = `Server error: ${response.status} ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      
      if (!data.response) {
        throw new Error('Invalid response format from server')
      }
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
      const errorText = error instanceof Error ? error.message : 'Unknown error occurred'
      const errorMessage: Message = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorText}. Please check your API key configuration or try again later.`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
      setAiStatus('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const quickActions = [
    { label: 'High Risk Flights', query: 'Show me flights with high overbooking risk next week' },
    { label: 'Low Capacity', query: 'Find flights with low available capacity' },
    { label: 'Explain Prediction', query: 'Explain the cargo capacity prediction for this flight' },
    { label: 'Optimize Cargo', query: 'What cargo mix would optimize revenue for this flight?' }
  ]

  const handleQuickAction = (query: string) => {
    setInput(query)
    setTimeout(() => {
      sendMessage()
    }, 100)
  }

  // Don't render minimized state for sidebar mode
  if (minimized && !isOpen) {
    return null
  }

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className={`ai-chat-overlay ${isOpen ? 'open' : ''}`}
          onClick={onToggle}
          aria-label="Close AI Assistant"
        />
      )}
      
      {/* Sidebar */}
      <div className={`ai-chat-sidebar ${isOpen ? 'open' : ''}`}>
        <div className="ai-chat-container">
      <div className="ai-chat-header">
        <div className="chat-header-left">
          <span className="chat-icon">🤖</span>
          <div>
            <h3>AI Assistant</h3>
            <span className="chat-status">Online</span>
          </div>
        </div>
        <div className="chat-header-actions">
          <button 
            className="chat-close-btn" 
            onClick={() => {
              onClose?.()
              onToggle?.()
            }} 
            title="Close"
            aria-label="Close AI Assistant"
          >
            ×
          </button>
        </div>
      </div>

      <div className="ai-chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`chat-message chat-message-${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-text">
                {message.role === 'assistant' ? (
                  <MarkdownRenderer content={message.content} />
                ) : (
                  message.content.split('\n').map((line, i) => (
                    <React.Fragment key={i}>
                      {line}
                      {i < message.content.split('\n').length - 1 && <br />}
                    </React.Fragment>
                  ))
                )}
              </div>
              {message.timestamp && (
                <div className="message-timestamp">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="chat-message chat-message-assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="message-text">
                <div className="ai-status-container">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  {aiStatus && (
                    <div className="ai-status-text">
                      {aiStatus}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 1 && (
        <div className="chat-quick-actions">
          <p className="quick-actions-label">Quick Actions:</p>
          <div className="quick-actions-grid">
            {quickActions.map((action, index) => (
              <button
                key={index}
                className="quick-action-btn"
                onClick={() => handleQuickAction(action.query)}
                disabled={loading}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="ai-chat-input-container">
        <textarea
          ref={inputRef}
          className="ai-chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything about cargo capacity, flights, or predictions..."
          rows={1}
          disabled={loading}
        />
        <button
          className="chat-send-btn"
          onClick={sendMessage}
          disabled={!input.trim() || loading}
          title="Send message (Enter)"
        >
          {loading ? '⏳' : '➤'}
        </button>
      </div>
        </div>
      </div>
    </>
  )
}

export default AIChat
