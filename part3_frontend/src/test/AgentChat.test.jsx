import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AgentChat from '../pages/AgentChat'
import agentService from '../services/agentService'

// Mock the agentService
vi.mock('../services/agentService', () => ({
  default: {
    createSession: vi.fn(),
    sendMessage: vi.fn(),
    getHistory: vi.fn(),
  },
}))

describe('AgentChat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    agentService.createSession.mockResolvedValue('test-session-123')
  })

  describe('Initialization', () => {
    it('renders the chat container', () => {
      render(<AgentChat />)

      expect(screen.getByText('Librarian Agent')).toBeInTheDocument()
      expect(screen.getByText('Powered by Claude SDK')).toBeInTheDocument()
    })

    it('creates a session on mount', async () => {
      render(<AgentChat />)

      await waitFor(() => {
        expect(agentService.createSession).toHaveBeenCalledTimes(1)
      })
    })

    it('renders the input form', () => {
      render(<AgentChat />)

      expect(screen.getByPlaceholderText('Ask me anything...')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
    })
  })

  describe('Message Sending', () => {
    it('sends a message when form is submitted', async () => {
      const user = userEvent.setup()
      agentService.sendMessage.mockImplementation((sessionId, message, onChunk) => {
        onChunk('Hello ')
        onChunk('there!')
        return Promise.resolve()
      })

      render(<AgentChat />)

      await waitFor(() => {
        expect(agentService.createSession).toHaveBeenCalled()
      })

      const input = screen.getByPlaceholderText('Ask me anything...')
      await user.type(input, 'Hello, how are you?')

      const sendButton = screen.getByRole('button', { name: /send/i })
      await user.click(sendButton)

      await waitFor(() => {
        expect(agentService.sendMessage).toHaveBeenCalledWith(
          'test-session-123',
          'Hello, how are you?',
          expect.any(Function)
        )
      })
    })

    it('clears input after sending', async () => {
      const user = userEvent.setup()
      agentService.sendMessage.mockResolvedValue()

      render(<AgentChat />)

      await waitFor(() => {
        expect(agentService.createSession).toHaveBeenCalled()
      })

      const input = screen.getByPlaceholderText('Ask me anything...')
      await user.type(input, 'Test message')
      await user.click(screen.getByRole('button', { name: /send/i }))

      expect(input).toHaveValue('')
    })

    it('disables input while loading', async () => {
      const user = userEvent.setup()

      // Make sendMessage hang to simulate loading
      agentService.sendMessage.mockImplementation(() => new Promise(() => {}))

      render(<AgentChat />)

      await waitFor(() => {
        expect(agentService.createSession).toHaveBeenCalled()
      })

      const input = screen.getByPlaceholderText('Ask me anything...')
      await user.type(input, 'Test message')
      await user.click(screen.getByRole('button', { name: /send/i }))

      await waitFor(() => {
        expect(input).toBeDisabled()
      })
    })

    it('does not send empty messages', async () => {
      const user = userEvent.setup()

      render(<AgentChat />)

      await waitFor(() => {
        expect(agentService.createSession).toHaveBeenCalled()
      })

      const sendButton = screen.getByRole('button', { name: /send/i })
      await user.click(sendButton)

      expect(agentService.sendMessage).not.toHaveBeenCalled()
    })
  })

  describe('Message Display', () => {
    it('displays user messages', async () => {
      const user = userEvent.setup()
      agentService.sendMessage.mockResolvedValue()

      render(<AgentChat />)

      await waitFor(() => {
        expect(agentService.createSession).toHaveBeenCalled()
      })

      const input = screen.getByPlaceholderText('Ask me anything...')
      await user.type(input, 'Hello from user')
      await user.click(screen.getByRole('button', { name: /send/i }))

      expect(screen.getByText('Hello from user')).toBeInTheDocument()
    })

    it('displays assistant messages from stream', async () => {
      const user = userEvent.setup()
      agentService.sendMessage.mockImplementation((sessionId, message, onChunk) => {
        onChunk('Response ')
        onChunk('from ')
        onChunk('assistant')
        return Promise.resolve()
      })

      render(<AgentChat />)

      await waitFor(() => {
        expect(agentService.createSession).toHaveBeenCalled()
      })

      const input = screen.getByPlaceholderText('Ask me anything...')
      await user.type(input, 'Hello')
      await user.click(screen.getByRole('button', { name: /send/i }))

      await waitFor(() => {
        expect(screen.getByText('Response from assistant')).toBeInTheDocument()
      })
    })

    it('shows typing indicator while loading', async () => {
      const user = userEvent.setup()

      // Keep the promise pending
      let resolvePromise
      agentService.sendMessage.mockImplementation(() =>
        new Promise(resolve => { resolvePromise = resolve })
      )

      render(<AgentChat />)

      await waitFor(() => {
        expect(agentService.createSession).toHaveBeenCalled()
      })

      const input = screen.getByPlaceholderText('Ask me anything...')
      await user.type(input, 'Hello')
      await user.click(screen.getByRole('button', { name: /send/i }))

      // Should show typing indicator
      await waitFor(() => {
        expect(document.querySelector('.typing-indicator')).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('displays error message on failure', async () => {
      const user = userEvent.setup()
      agentService.sendMessage.mockRejectedValue(new Error('Network error'))

      render(<AgentChat />)

      await waitFor(() => {
        expect(agentService.createSession).toHaveBeenCalled()
      })

      const input = screen.getByPlaceholderText('Ask me anything...')
      await user.type(input, 'Hello')
      await user.click(screen.getByRole('button', { name: /send/i }))

      await waitFor(() => {
        expect(screen.getByText(/Error: Network error/)).toBeInTheDocument()
      })
    })
  })
})
