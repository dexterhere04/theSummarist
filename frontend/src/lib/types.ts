export type DocFormat = 'PDF' | 'DOC' | 'DOCX' | 'PPTX' | 'TXT' | 'WEB'

export type SummaryLength = 'Short' | 'Medium' | 'Long'

export interface SummaryItem {
  id: string
  title: string
  source: string
  format: DocFormat
  excerpt: string
  date: string
  length: SummaryLength
  kind: string
  category: string
  pages: number
  words: number
  tldr: string
  takeaways: { title: string; body: string }[]
  sections: { heading: string; body: string }[]
  highlight: string
}

export interface ExtractedDoc {
  id: string
  title: string
  fileName: string
  format: DocFormat
  pages: number
  words: number
  lang: string
  ocr: string
  body: { heading: string; paragraphs: string[]; bullets?: string[] }[]
}
