import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface AnalysisJob {
  id: string
  whaleId: string
  whaleAddress: string
  type: 'forward' | 'reverse'
  status: 'pending' | 'running' | 'completed' | 'failed'
  currentStep: number
  totalSteps: number
  startTime: string
  estimatedCompletion: string
  confidence: number
  riskLevel: 'low' | 'medium' | 'high' | 'veryHigh'
  result?: AnalysisResult
}

export interface AnalysisResult {
  summary: string
  causalGraph: CausalGraphData
  eventChain: EventChainItem[]
  probability: ProbabilityData
  deliberation: DeliberationStep[]
  report: string
}

export interface CausalGraphData {
  nodes: CausalNode[]
  edges: CausalEdge[]
}

export interface CausalNode {
  id: string
  label: string
  type: 'event' | 'decision' | 'outcome' | 'factor'
  x?: number
  y?: number
  importance: number
  timestamp?: string
}

export interface CausalEdge {
  source: string
  target: string
  weight: number
  type: 'causal' | 'correlation' | 'temporal'
  label?: string
}

export interface EventChainItem {
  id: string
  timestamp: string
  event: string
  description: string
  impact: 'positive' | 'negative' | 'neutral'
  magnitude: number
}

export interface ProbabilityData {
  predictions: { time: string; probability: number; price: number }[]
  scenarios: { name: string; probability: number; outcome: string }[]
}

export interface DeliberationStep {
  agentId: string
  agentName: string
  reasoning: string
  confidence: number
  factors: { name: string; score: number }[]
  conclusion: string
}

export interface FilterConfig {
  id: string
  name: string
  createdAt: string
  matchCount: number
  scale: { min: number; max: number }
  profitability: { minWinRate: number; minROI: number }
  consistency: { timePeriod: string }
  activity: { minTrades: number }
  chainToken: { chains: string[]; tokens: string[] }
  autoAnalysis: boolean
  notifications: boolean
}

export const useAnalysisStore = defineStore('analysis', () => {
  const jobs = ref<AnalysisJob[]>([
    {
      id: 'a1',
      whaleId: 'w1',
      whaleAddress: '0x1234...5678',
      type: 'forward',
      status: 'completed',
      currentStep: 5,
      totalSteps: 5,
      startTime: new Date(Date.now() - 3600000).toISOString(),
      estimatedCompletion: new Date(Date.now() - 3000000).toISOString(),
      confidence: 87,
      riskLevel: 'medium'
    },
    {
      id: 'a2',
      whaleId: 'w2',
      whaleAddress: '0xabcd...ef01',
      type: 'reverse',
      status: 'running',
      currentStep: 3,
      totalSteps: 5,
      startTime: new Date(Date.now() - 1800000).toISOString(),
      estimatedCompletion: new Date(Date.now() + 900000).toISOString(),
      confidence: 72,
      riskLevel: 'low'
    }
  ])

  const filters = ref<FilterConfig[]>([
    {
      id: 'f1',
      name: 'ETH 大额交易',
      createdAt: new Date(Date.now() - 86400000).toISOString(),
      matchCount: 23,
      scale: { min: 100000, max: 10000000 },
      profitability: { minWinRate: 70, minROI: 100 },
      consistency: { timePeriod: '30d' },
      activity: { minTrades: 10 },
      chainToken: { chains: ['Ethereum'], tokens: [] },
      autoAnalysis: true,
      notifications: true
    },
    {
      id: 'f2',
      name: 'BSC 高胜率鲸鱼',
      createdAt: new Date(Date.now() - 172800000).toISOString(),
      matchCount: 15,
      scale: { min: 50000, max: 5000000 },
      profitability: { minWinRate: 80, minROI: 200 },
      consistency: { timePeriod: '7d' },
      activity: { minTrades: 5 },
      chainToken: { chains: ['BSC'], tokens: [] },
      autoAnalysis: false,
      notifications: true
    }
  ])

  const completedJobs = computed(() => jobs.value.filter(j => j.status === 'completed'))
  const runningJobs = computed(() => jobs.value.filter(j => j.status === 'running'))

  function getJobById(id: string) {
    return jobs.value.find(j => j.id === id)
  }

  function addJob(job: AnalysisJob) {
    jobs.value.push(job)
  }

  function updateJobStatus(id: string, status: AnalysisJob['status'], step?: number) {
    const job = jobs.value.find(j => j.id === id)
    if (job) {
      job.status = status
      if (step !== undefined) job.currentStep = step
    }
  }

  function addFilter(filter: FilterConfig) {
    filters.value.push(filter)
  }

  function removeFilter(id: string) {
    filters.value = filters.value.filter(f => f.id !== id)
  }

  return {
    jobs,
    filters,
    completedJobs,
    runningJobs,
    getJobById,
    addJob,
    updateJobStatus,
    addFilter,
    removeFilter
  }
})
