// Global test setup
import { vi } from 'vitest'

// Mock console.log to avoid cluttering test output
global.console = {
  ...console,
  log: vi.fn(),
  error: vi.fn(),
  warn: vi.fn(),
  info: vi.fn(),
  debug: vi.fn()
}

// Mock API base URL for tests
global.API_BASE_URL = 'http://localhost:8000/api'