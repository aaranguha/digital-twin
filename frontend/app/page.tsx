// Main Page - The Digital Twin Chat Interface
"use client"

import { useState, useEffect } from 'react'

// TypeScript type for chat messages
type Message = {
  role: 'user' | 'twin'
  content: string
  sources?: string[]
}

// TypeScript type for status from Mood Engine
type Status = {
  availability: string
  energy_estimate: string
  best_contact_method: string
  suggested_wait_time: string
  context_summary: string
  meeting_count: number
  meetings_remaining: number
  in_meeting: boolean
}

export default function Home() {
  // ============== STATE ==============
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // NEW: Status from Mood Engine (calendar analysis)
  const [status, setStatus] = useState<Status | null>(null)

  // ============== FETCH STATUS ON LOAD ==============
  // useEffect runs when the component first loads
  useEffect(() => {
    fetchStatus()
  }, [])  // Empty array = run once on mount

  async function fetchStatus() {
    try {
      const response = await fetch('http://localhost:8000/api/status')
      const data = await response.json()
      setStatus(data)
    } catch (error) {
      console.error('Failed to fetch status:', error)
    }
  }

  // ============== SEND MESSAGE ==============
  async function handleSend() {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')

    // Capture current history BEFORE adding new message
    const history = messages.map(m => ({ role: m.role, content: m.content }))

    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage, history }),
      })
      const data = await response.json()
      setMessages(prev => [...prev, {
        role: 'twin',
        content: data.response,
        sources: data.sources,
      }])
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'twin',
        content: 'Sorry, I encountered an error. Is the backend running?',
      }])
    } finally {
      setIsLoading(false)
    }
  }

  // ============== SUGGESTED QUESTIONS ==============
  const suggestions = [
    "What's your background?",
    "What projects have you built?",
    "Is now a good time to reach you?",
  ]

  function handleSuggestionClick(question: string) {
    setInput(question)
  }

  // ============== HELPER: Get emoji for availability ==============
  function getAvailabilityEmoji(availability: string): string {
    switch (availability) {
      case 'open': return '🟢'
      case 'focused': return '🟡'
      case 'busy': return '🔴'
      case 'winding_down': return '🟠'
      default: return '⚪'
    }
  }

  // ============== RENDER UI ==============
  return (
    <main className="min-h-screen bg-gray-900 text-white p-4">

      {/* Header */}
      <div className="max-w-6xl mx-auto mb-4">
        <h1 className="text-2xl font-bold">🧠 Aaran&apos;s Digital Twin</h1>
      </div>

      {/* Main content - two columns */}
      <div className="max-w-6xl mx-auto flex gap-4">

        {/* LEFT: Chat Interface */}
        <div className="flex-1 bg-gray-800 rounded-lg p-4 flex flex-col h-[600px]">

          {/* Messages */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg ${
                  msg.role === 'user' ? 'bg-blue-600 ml-12' : 'bg-gray-700 mr-12'
                }`}
              >
                <div className="text-xs text-gray-400 mb-1">
                  {msg.role === 'user' ? 'You' : 'Twin'}
                </div>
                <div>{msg.content}</div>
              </div>
            ))}

            {isLoading && (
              <div className="bg-gray-700 p-3 rounded-lg mr-12">
                <div className="text-xs text-gray-400 mb-1">Twin</div>
                <div className="text-gray-400">Thinking...</div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask me anything..."
              className="flex-1 bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSend}
              disabled={isLoading}
              className="bg-blue-600 px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>

        {/* RIGHT: Status Panel & Suggestions */}
        <div className="w-64 space-y-4">

          {/* Status Panel - NOW DYNAMIC! */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h2 className="font-bold mb-3">📊 Current State</h2>

            {status ? (
              // Show real data from Mood Engine
              <div className="space-y-2 text-sm">
                {/* Show "In Meeting" banner if currently in a meeting */}
                {status.in_meeting && (
                  <div className="bg-red-600 text-white px-2 py-1 rounded text-center font-medium">
                    🔴 Currently in Meeting
                  </div>
                )}
                <div>
                  {getAvailabilityEmoji(status.availability)}{' '}
                  {status.availability.charAt(0).toUpperCase() + status.availability.slice(1)}
                </div>
                <div>📅 {status.meetings_remaining} meetings remaining</div>
                <div>⏰ Best: {status.suggested_wait_time}</div>
                <div>🧠 Energy: {status.energy_estimate}</div>
                <div className="text-xs text-gray-400 mt-2">
                  {status.context_summary}
                </div>
              </div>
            ) : (
              // Loading state
              <div className="text-gray-400 text-sm">Loading...</div>
            )}
          </div>

          {/* Suggested Questions */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h2 className="font-bold mb-3">💡 Try Asking</h2>
            <div className="space-y-2">
              {suggestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(question)}
                  className="block w-full text-left text-sm p-2 rounded bg-gray-700 hover:bg-gray-600"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
