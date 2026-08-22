import type { ExtractedDoc, SummaryItem } from './types'

export const summaries: SummaryItem[] = [
  {
    id: 'quantum-computing',
    title: 'Quantum Computing Overview',
    source: 'quantum_computing_whitepaper.pdf',
    format: 'PDF',
    excerpt:
      'How quantum mechanics is reshaping computation — from qubits to commercial reality.',
    date: 'Today, 2:45 PM',
    length: 'Medium',
    kind: 'Executive Summary',
    category: 'Research',
    pages: 18,
    words: 6420,
    tldr:
      'Quantum computing leverages quantum mechanics to process information fundamentally differently than classical computers, promising exponential speedups in cryptography, material science, and complex optimization. While physical challenges like qubit decoherence remain, recent breakthroughs indicate a transition from theory to practical engineering within the next decade.',
    takeaways: [
      {
        title: 'Superposition & Entanglement',
        body: 'The core mechanics allowing qubits to exist in multiple states simultaneously, enabling massive parallel computation.',
      },
      {
        title: "Shor's Algorithm",
        body: 'A proven quantum algorithm capable of factoring large primes exponentially faster, posing a future threat to RSA encryption.',
      },
      {
        title: 'Error Correction',
        body: 'The current major hurdle. "Logical qubits" require thousands of physical qubits to maintain stability and prevent decoherence.',
      },
      {
        title: 'NISQ Era',
        body: 'We are currently in the Noisy Intermediate-Scale Quantum era, where useful applications must tolerate imperfect hardware.',
      },
    ],
    sections: [
      {
        heading: 'The Paradigm Shift',
        body: 'Unlike classical bits (0 or 1), quantum bits (qubits) utilize superposition to represent complex probabilities. This fundamental difference means quantum computers do not just "do things faster"; they approach problems differently. For tasks involving vast combinatorics like simulating molecular structures, a classical computer might need millennia, while a mature quantum system could find solutions in hours.',
      },
      {
        heading: 'Hardware Approaches',
        body: 'The industry has not settled on a single hardware architecture. Leading contenders include superconducting circuits (IBM, Google), trapped ions (IonQ, Quantinuum), and topological qubits (Microsoft). Each approach balances coherence time against gate fidelity and scalability.',
      },
      {
        heading: 'Commercial Implications',
        body: 'Early commercial value is expected in specialized optimization problems (logistics, financial modeling) and materials science (discovering new battery materials or pharmaceuticals). The report concludes that organizations should begin "quantum-proofing" their cryptography now, while monitoring hardware developments for strategic advantage.',
      },
    ],
    highlight:
      'The strategic pivot towards quantum-safe cryptography has begun yielding substantial returns earlier than anticipated.',
  },
  {
    id: 'transformer-architecture',
    title: 'Research Paper — Transformer Architecture',
    source: 'attention_is_all_you_need.pdf',
    format: 'PDF',
    excerpt:
      'A deep dive into attention mechanisms and their impact on modern LLMs.',
    date: 'Today, 11:20 AM',
    length: 'Long',
    kind: 'Detailed Summary',
    category: 'Research',
    pages: 11,
    words: 4890,
    tldr:
      'The transformer replaces recurrence with self-attention, allowing a model to weigh the relevance of every token in a sequence simultaneously. This architectural shift is the foundation of modern large language models and scales more efficiently than prior sequence models.',
    takeaways: [
      {
        title: 'Self-Attention',
        body: 'Each token attends to every other token, capturing long-range dependencies in a single pass rather than sequentially.',
      },
      {
        title: 'Multi-Head Attention',
        body: 'Parallel attention heads learn distinct relational patterns, letting the model represent several types of relationships at once.',
      },
      {
        title: 'Positional Encoding',
        body: 'Since attention is order-agnostic, positional signals are injected so the model retains sequence structure.',
      },
    ],
    sections: [
      {
        heading: 'From Recurrence to Attention',
        body: 'Recurrent networks process tokens step by step, which limits parallelization. The transformer processes the entire sequence at once, dramatically improving training throughput and enabling the scaling that underpins modern LLMs.',
      },
      {
        heading: 'Scalability',
        body: 'Because computation is highly parallel and memory-bound, transformers scale across accelerators efficiently. This property, more than any architectural detail, is why they became the default for large-scale language modeling.',
      },
    ],
    highlight:
      'Attention mechanisms, not model depth, are the primary driver of long-range reasoning quality.',
  },
  {
    id: 'annual-financial-report',
    title: 'Annual Financial Report 2025',
    source: 'financial_report_2025.docx',
    format: 'DOCX',
    excerpt:
      'Summary of Q4 earnings, projected growth for next fiscal year, and risk factors.',
    date: 'Yesterday',
    length: 'Short',
    kind: 'Executive Summary',
    category: 'Finance',
    pages: 44,
    words: 12840,
    tldr:
      'Revenue grew 18% year-over-year to $45.2M, with gross margin improving to 72%. Operating income rose 25% to $12.5M, driven by enterprise subscriptions and a successful cloud-native analytics launch.',
    takeaways: [
      {
        title: 'Revenue Growth',
        body: '18% YoY increase, significantly outpacing the 8% target, driven by enterprise SaaS adoption.',
      },
      {
        title: 'Margin Expansion',
        body: 'Gross margin improved from 68% to 72% through economies of scale and favorable contract renewals.',
      },
      {
        title: 'Risk Factors',
        body: 'Customer concentration and currency exposure remain the two largest monitored risks for the coming year.',
      },
    ],
    sections: [
      {
        heading: 'Executive Summary',
        body: 'Total consolidated revenue reached $45.2M, an 18% increase year-over-year, driven by enterprise software adoption and the launch of the Cloud-Native Analytics module.',
      },
      {
        heading: 'Revenue by Segment',
        body: 'Enterprise subscriptions remain the primary growth engine at $28.5M, up 24%. Professional services grew 5%, while legacy maintenance declined 2% consistent with platform migration strategy.',
      },
    ],
    highlight:
      'Enterprise subscriptions remain the primary growth engine, up 24% year-over-year.',
  },
  {
    id: 'ml-market-trends',
    title: 'Machine Learning Market Trends',
    source: 'ml_market_trends_2025.md',
    format: 'WEB',
    excerpt:
      'The shift toward edge computing and smaller, specialized models is accelerating.',
    date: 'Oct 10, 2025',
    length: 'Medium',
    kind: 'Key Points',
    category: 'Tech',
    pages: 1,
    words: 3200,
    tldr:
      'Companies are prioritizing smaller, more efficient models over massive general-purpose LLMs for specific industry applications, driving a shift toward edge computing in AI.',
    takeaways: [
      {
        title: 'Edge Shift',
        body: 'Inference is moving to the edge, reducing latency and data egress costs for real-time applications.',
      },
      {
        title: 'Small Models Win',
        body: 'Task-specialized models under 10B parameters are beating larger general models on domain benchmarks.',
      },
    ],
    sections: [
      {
        heading: 'Market Dynamics',
        body: 'The economics of large-model inference are shifting procurement toward fine-tuned smaller models that run on commodity hardware.',
      },
    ],
    highlight:
      'Task-specialized models under 10B parameters are beating larger general models on domain benchmarks.',
  },
  {
    id: 'project-phoenix',
    title: 'Project Phoenix Kickoff',
    source: 'project_phoenix_kickoff.pptx',
    format: 'PPTX',
    excerpt:
      'Timeline for a 6-month development cycle focused on core infrastructure overhaul.',
    date: 'Oct 8, 2025',
    length: 'Short',
    kind: 'Action Items',
    category: 'Internal',
    pages: 45,
    words: 2100,
    tldr:
      'A 6-month development cycle split into three phases, beginning with core infrastructure overhaul. Key stakeholders identified from Engineering, Product, and Marketing.',
    takeaways: [
      {
        title: 'Phase 1',
        body: 'Core infrastructure overhaul — 8 weeks, owned by Engineering.',
      },
      {
        title: 'Phase 2',
        body: 'Feature parity migration — 10 weeks, cross-functional.',
      },
    ],
    sections: [
      {
        heading: 'Timeline',
        body: 'The plan spans three phases over six months, with explicit ownership and checkpoints at each milestone.',
      },
    ],
    highlight:
      'Phase 1 focuses on core infrastructure overhaul with explicit ownership from Engineering.',
  },
]

export const extractedDoc: ExtractedDoc = {
  id: 'annual-financial-report',
  title: 'Q3 2023 Financial Performance Overview',
  fileName: 'Q3_Financial_Report_2023.pdf',
  format: 'PDF',
  pages: 12,
  words: 4285,
  lang: 'English (US)',
  ocr: 'Advanced Vision V4',
  body: [
    {
      heading: 'Executive Summary',
      paragraphs: [
        'This document provides a comprehensive review of the company\u2019s financial performance for the third quarter of 2023, ending September 30. The results indicate a robust quarter, characterized by significant revenue growth across core segments, improved operational efficiency, and a strengthened balance sheet.',
        'Total consolidated revenue for Q3 2023 reached $45.2 million, representing an 18% increase year-over-year (YoY). This growth was primarily driven by the accelerated adoption of our enterprise software solutions and the successful launch of the new Cloud-Native Analytics module in late August.',
        'Gross profit margin improved to 72%, up from 68% in the same quarter last year, reflecting economies of scale and more favorable pricing structures in recent enterprise contract renewals. Operating income stood at $12.5 million, a substantial 25% YoY increase.',
      ],
    },
    {
      heading: 'Revenue by Segment',
      paragraphs: [
        'The revenue breakdown highlights the shifting dynamics of our product portfolio towards higher-margin, recurring revenue streams.',
      ],
      bullets: [
        'Enterprise Subscriptions: $28.5 million (up 24% YoY). This segment remains our primary growth engine.',
        'Professional Services: $9.2 million (up 5% YoY). Growth here has been intentionally moderated to focus on scalable software revenue.',
        'Legacy Maintenance: $7.5 million (down 2% YoY). The slight decline is consistent with our strategy to migrate customers to newer platforms.',
      ],
    },
  ],
}
