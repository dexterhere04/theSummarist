export type DocFormat = 'PDF' | 'DOC' | 'DOCX' | 'PPTX' | 'TXT' | 'WEB'

export type DocStatus =
  | 'uploaded'
  | 'extracting'
  | 'understanding'
  | 'preparing'
  | 'ready'
  | 'failed'

export type SummaryLength = 'Short' | 'Medium' | 'Long'

export type SummaryStyle = 'executive' | 'key_points' | 'detailed' | 'study_notes' | 'action_items'

export type SummaryFormat = 'bullets' | 'paragraph'

export type DetailLevel = 'concise' | 'medium' | 'detailed'

export type Category = 'Research' | 'Finance' | 'Tech' | 'Internal'

export interface User {
  id: string
  email: string
  name: string
  avatar_initials: string
  plan: string
  created_at: string
}

export interface UserSettings {
  default_length: SummaryLength
  default_style: SummaryStyle
  language: string
  tts_voice: string
  theme: string
}

export interface Document {
  id: string
  user_id: string
  file_name: string
  format: DocFormat
  mime_type: string
  size_bytes: number
  source: 'upload' | 'url'
  source_url: string | null
  status: DocStatus
  pages: number | null
  words: number | null
  language: string | null
  ocr_method: string | null
  created_at: string
  updated_at: string
}

export type JobType = 'extract' | 'summarize'
export type JobStatus = 'pending' | 'running' | 'succeeded' | 'failed' | 'cancelled'
export type JobStage = 'uploaded' | 'extracting' | 'understanding' | 'preparing'

export interface Job {
  id: string
  document_id: string | null
  summary_id?: string | null
  type: JobType
  status: JobStatus
  stage: JobStage
  progress: number
  stage_index: number
  total_stages: number
  error: { code: string; message: string } | null
  created_at: string
}

export interface ExtractedSection {
  heading: string
  paragraphs: string[]
  bullets?: string[]
}

export interface ExtractedText {
  document_id: string
  title: string
  file_name: string
  format: DocFormat
  pages: number | null
  words: number | null
  language: string | null
  ocr_method: string | null
  body: ExtractedSection[]
}

export interface SummaryItem {
  id: string
  document_id: string
  user_id: string
  title: string
  source: string
  format: DocFormat
  excerpt: string
  date: string
  length: SummaryLength
  style: SummaryStyle
  kind: string
  category: Category
  pages: number | null
  words: number | null
  tldr: string
  takeaways: { title: string; body: string }[]
  sections: { heading: string; body: string }[]
  highlight: string | null
  favorite: boolean
  status: 'ready' | 'generating' | 'failed'
  params: {
    format: SummaryFormat
    detail_level: DetailLevel
    include_key_points: boolean
    include_quotes: boolean
  }
  created_at: string
}

export interface Page<T> {
  items: T[]
  page: number
  per_page: number
  total: number
  has_more: boolean
}

export interface SearchMatch {
  section_heading: string
  paragraph_index: number
  snippet: string
  start: number
  end: number
}

export interface SearchResponse {
  matches: SearchMatch[]
  total: number
}

export interface ShareResponse {
  share_url: string
  token: string
  expires_at: string | null
}

export interface AudioResponse {
  audio_url: string
  duration_seconds: number
  voice: string
}

export interface TokenResponse {
  user: User
  access_token: string
  refresh_token: string
}

export interface ApiErrorBody {
  error: { code: string; message: string; details?: unknown }
}
