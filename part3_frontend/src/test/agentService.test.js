import { describe, it, expect, vi, beforeEach } from 'vitest'
import agentService from '../services/agentService'

// Mock axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

import axios from 'axios'

describe('agentService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  describe('createSession', () => {
    it('creates a new session and returns session ID', async () => {
      axios.post.mockResolvedValue({
        data: { session_id: 'new-session-123' },
      })

      const sessionId = await agentService.createSession()

      expect(axios.post).toHaveBeenCalledWith('/api/agent/chat/new')
      expect(sessionId).toBe('new-session-123')
    })

    it('throws error on failure', async () => {
      axios.post.mockRejectedValue(new Error('Network error'))

      await expect(agentService.createSession()).rejects.toThrow('Network error')
    })
  })

  describe('sendMessage', () => {
    it('sends message and calls onChunk with streamed content', async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('event: content\ndata: {"text":"Hello "}\n\n'),
          })
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('event: content\ndata: {"text":"World"}\n\n'),
          })
          .mockResolvedValueOnce({
            done: true,
            value: undefined,
          }),
        releaseLock: vi.fn(),
      }

      global.fetch.mockResolvedValue({
        ok: true,
        body: {
          getReader: () => mockReader,
        },
      })

      const onChunk = vi.fn()
      await agentService.sendMessage('session-123', 'Hi there', onChunk)

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/agent/chat/session-123',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: 'Hi there' }),
        })
      )

      expect(onChunk).toHaveBeenCalledWith('Hello ')
      expect(onChunk).toHaveBeenCalledWith('World')
    })

    it('throws error on non-ok response', async () => {
      global.fetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      })

      await expect(
        agentService.sendMessage('session-123', 'Hello', vi.fn())
      ).rejects.toThrow('HTTP error! status: 404')
    })

    it('handles malformed SSE data gracefully', async () => {
      const mockReader = {
        read: vi.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode('data: not-valid-json\n\n'),
          })
          .mockResolvedValueOnce({
            done: true,
            value: undefined,
          }),
        releaseLock: vi.fn(),
      }

      global.fetch.mockResolvedValue({
        ok: true,
        body: {
          getReader: () => mockReader,
        },
      })

      const onChunk = vi.fn()
      // Should not throw, just log warning
      await agentService.sendMessage('session-123', 'Hi', onChunk)

      // onChunk should not be called for invalid data
      expect(onChunk).not.toHaveBeenCalled()
    })

    it('releases reader lock after completion', async () => {
      const mockReader = {
        read: vi.fn().mockResolvedValue({ done: true, value: undefined }),
        releaseLock: vi.fn(),
      }

      global.fetch.mockResolvedValue({
        ok: true,
        body: {
          getReader: () => mockReader,
        },
      })

      await agentService.sendMessage('session-123', 'Hi', vi.fn())

      expect(mockReader.releaseLock).toHaveBeenCalled()
    })
  })

  describe('getHistory', () => {
    it('fetches conversation history', async () => {
      const mockHistory = {
        session_id: 'session-123',
        messages: [
          { role: 'user', content: 'Hello' },
          { role: 'assistant', content: 'Hi there!' },
        ],
      }

      axios.get.mockResolvedValue({ data: mockHistory })

      const history = await agentService.getHistory('session-123')

      expect(axios.get).toHaveBeenCalledWith('/api/agent/chat/session-123/history')
      expect(history).toEqual(mockHistory)
    })

    it('throws error on failure', async () => {
      axios.get.mockRejectedValue(new Error('Not found'))

      await expect(agentService.getHistory('invalid-session')).rejects.toThrow('Not found')
    })
  })
})
