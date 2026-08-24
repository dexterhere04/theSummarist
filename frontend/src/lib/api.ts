import type {
  AudioResponse,
  Category,
  DetailLevel,
  DocFormat,
  Document,
  ExtractedText,
  Job,
  Page,
  SearchResponse,
  ShareResponse,
  SummaryFormat,
  SummaryItem,
  SummaryLength,
  SummaryStyle,
  TokenResponse,
  User,
  UserSettings,
} from './types'

const BASE = '/api/v1'
const ACCESS_KEY = 'ts_access_token'
const REFRESH_KEY = 'ts_refresh_token'

const DEMO_ACCOUNT = {
  email: 'demo@summarist.ai',
  password: 'summarist-demo-1',
  name: 'Dexter',
}

function tokens(): { access: string | null; refresh: string | null } {
  return {
    access: localStorage.getItem(ACCESS_KEY),
    refresh: localStorage.getItem(REFRESH_KEY),
  }
}

function storeTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}

function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

async function parseError(res: Response): Promise<never> {
  let message = `Request failed (${res.status})`
  try {
    const body = (await res.json()) as { error?: { message?: string } }
    if (body.error?.message) message = body.error.message
  } catch {
    /* non-JSON error body */
  }
  throw new Error(message)
}

async function refreshSession(): Promise<boolean> {
  const { refresh } = tokens()
  if (!refresh) return false
  const res = await fetch(`${BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh }),
  })
  if (!res.ok) {
    clearTokens()
    return false
  }
  const pair = (await res.json()) as { access_token: string; refresh_token: string }
  storeTokens(pair.access_token, pair.refresh_token)
  return true
}

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const { access } = tokens()
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      ...(init.headers ?? {}),
      ...(access ? { Authorization: `Bearer ${access}` } : {}),
    },
  })
  if (res.status === 401 && retry) {
    const refreshed = await refreshSession()
    if (refreshed) return request<T>(path, init, false)
  }
  if (!res.ok) return parseError(res)
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

/** Bootstraps a session without a login screen (spec §9.4). */
export async function ensureSession(): Promise<User> {
  const { access } = tokens()
  if (access) {
    try {
      return await request<User>('/me')
    } catch {
      clearTokens()
    }
  }
  const login = async (): Promise<Response> =>
    fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: DEMO_ACCOUNT.email,
        password: DEMO_ACCOUNT.password,
      }),
    })

  let res = await login()
  if (res.status === 401) {
    await fetch(`${BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(DEMO_ACCOUNT),
    })
    res = await login()
  }
  if (!res.ok) return parseError(res)
  const auth = (await res.json()) as TokenResponse
  storeTokens(auth.access_token, auth.refresh_token)
  return auth.user
}

export interface CreateSummaryPayload {
  document_id: string
  length: SummaryLength
  style: SummaryStyle
  format: SummaryFormat
  detail_level: DetailLevel
  include_key_points: boolean
  include_quotes: boolean
}

export interface ListSummariesParams {
  tab?: 'all' | 'recent' | 'favorites'
  q?: string
  category?: Category
  format?: DocFormat
  length?: SummaryLength
  style?: SummaryStyle
  sort?: 'created_at' | 'title'
  page?: number
  per_page?: number
}

export const api = {
  // --- documents ---
  async upload(file: File, runSummary = true): Promise<{ document: Document; job: Job }> {
    const form = new FormData()
    form.append('file', file)
    form.append('run_summary', String(runSummary))
    return request('/documents', { method: 'POST', body: form })
  },
  async fromUrl(url: string): Promise<{ document: Document; job: Job }> {
    return request('/documents/from-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    })
  },
  listDocuments(params: { page?: number; per_page?: number; q?: string } = {}): Promise<
    Page<Document>
  > {
    const qs = new URLSearchParams(
      Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== '')
        .map(([k, v]) => [k, String(v)]),
    )
    return request(`/documents?${qs}`)
  },
  getDocument(id: string): Promise<Document> {
    return request(`/documents/${id}`)
  },
  deleteDocument(id: string): Promise<void> {
    return request(`/documents/${id}`, { method: 'DELETE' })
  },
  documentStatus(id: string): Promise<Job> {
    return request(`/documents/${id}/status`)
  },
  extractedText(id: string): Promise<ExtractedText> {
    return request(`/documents/${id}/extracted-text`)
  },
  searchDocument(id: string, q: string): Promise<SearchResponse> {
    return request(`/documents/${id}/search?q=${encodeURIComponent(q)}`)
  },

  // --- summaries ---
  createSummary(payload: CreateSummaryPayload): Promise<{ summary: SummaryItem; job: Job }> {
    return request('/summaries', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  },
  listSummaries(params: ListSummariesParams = {}): Promise<Page<SummaryItem>> {
    const qs = new URLSearchParams(
      Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== '')
        .map(([k, v]) => [k, String(v)]),
    )
    return request(`/summaries?${qs}`)
  },
  getSummary(id: string): Promise<SummaryItem> {
    return request(`/summaries/${id}`)
  },
  regenerateSummary(
    id: string,
    overrides: Partial<Omit<CreateSummaryPayload, 'document_id'>> = {},
  ): Promise<{ summary: SummaryItem; job: Job }> {
    return request(`/summaries/${id}/regenerate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(overrides),
    })
  },
  deleteSummary(id: string): Promise<void> {
    return request(`/summaries/${id}`, { method: 'DELETE' })
  },
  toggleFavorite(id: string): Promise<{ favorite: boolean }> {
    return request(`/summaries/${id}/favorite`, { method: 'POST' })
  },
  shareSummary(id: string): Promise<ShareResponse> {
    return request(`/summaries/${id}/share`, { method: 'POST' })
  },
  audio(id: string, voice = 'default'): Promise<AudioResponse> {
    return request(`/summaries/${id}/audio?voice=${encodeURIComponent(voice)}`)
  },

  // --- jobs ---
  job(id: string): Promise<Job> {
    return request(`/jobs/${id}`)
  },
  cancelJob(id: string): Promise<{ status: string }> {
    return request(`/jobs/${id}/cancel`, { method: 'POST' })
  },
  backgroundJob(id: string): Promise<{ status: string }> {
    return request(`/jobs/${id}/background`, { method: 'POST' })
  },

  // --- account ---
  me(): Promise<User> {
    return request('/me')
  },
  patchMe(body: { name?: string; email?: string }): Promise<User> {
    return request('/me', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  },
  settings(): Promise<UserSettings> {
    return request('/me/settings')
  },
  patchSettings(body: Partial<UserSettings>): Promise<UserSettings> {
    return request('/me/settings', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
  },
  categories(): Promise<{ categories: Category[] }> {
    return request('/categories')
  },
}

/** Authenticated binary download via blob (download links can't send headers). */
export async function downloadFile(path: string, filename: string): Promise<void> {
  const { access } = tokens()
  const res = await fetch(`${BASE}${path}`, {
    headers: access ? { Authorization: `Bearer ${access}` } : {},
  })
  if (!res.ok) return parseError(res)
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = window.document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
