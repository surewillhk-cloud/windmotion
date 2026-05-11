import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '@/services/api'

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
  result?: any
}

export interface FilterConfig {
  id: string
  name: string
  createdAt: string
  matchCount: number
  [key: string]: any
}

export const useAnalysisStore = defineStore('analysis', () => {
  const jobs = ref<AnalysisJob[]>([])
  const filters = ref<FilterConfig[]>([])
  const currentAnalysis = ref<any>(null)
  const progress = ref<any>(null)
  const report = ref<any>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const completedJobs = computed(() => jobs.value.filter(j => j.status === 'completed'))
  const runningJobs = computed(() => jobs.value.filter(j => j.status === 'running'))

  // ── Reverse Analysis ──
  async function startReverse(address: string, mode = 'deep') {
    loading.value = true
    error.value = null
    try {
      const data = await api.startReverseAnalysis(address, mode)
      currentAnalysis.value = data
      // Add to jobs list
      const job: AnalysisJob = {
        id: data.analysis_id || data.id,
        whaleId: data.whale_id || '',
        whaleAddress: address,
        type: 'reverse',
        status: 'running',
        currentStep: 0,
        totalSteps: 5,
        startTime: new Date().toISOString(),
        estimatedCompletion: '',
        confidence: 0,
        riskLevel: 'medium'
      }
      jobs.value.unshift(job)
      return data.analysis_id || data.id
    } catch (e: any) {
      error.value = e.message || 'Failed to start reverse analysis'
      throw e
    } finally {
      loading.value = false
    }
  }

  // ── Forward Analysis ──
  async function startForward(address: string) {
    loading.value = true
    error.value = null
    try {
      const data = await api.startForwardInference(address)
      currentAnalysis.value = data
      const job: AnalysisJob = {
        id: data.analysis_id || data.id,
        whaleId: data.whale_id || '',
        whaleAddress: address,
        type: 'forward',
        status: 'running',
        currentStep: 0,
        totalSteps: 5,
        startTime: new Date().toISOString(),
        estimatedCompletion: '',
        confidence: 0,
        riskLevel: 'medium'
      }
      jobs.value.unshift(job)
      return data.analysis_id || data.id
    } catch (e: any) {
      error.value = e.message || 'Failed to start forward analysis'
      throw e
    } finally {
      loading.value = false
    }
  }

  // ── Fetch progress ──
  async function fetchProgress(id: string) {
    try {
      const data = await api.getAnalysisProgress(id)
      progress.value = data
      // Update job status
      const job = jobs.value.find(j => j.id === id)
      if (job) {
        job.status = data.status || job.status
        job.currentStep = data.current_step ?? data.step ?? job.currentStep
        job.confidence = data.confidence ?? job.confidence
      }
      return data
    } catch (e: any) {
      console.error('fetchProgress error:', e)
    }
  }

  // ── Fetch report ──
  async function fetchReport(id: string) {
    loading.value = true
    try {
      const data = await api.getAnalysisReport(id)
      report.value = data.report || data
      return report.value
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch report'
    } finally {
      loading.value = false
    }
  }

  // ── Fetch replay ──
  async function fetchReplay(id: string) {
    try {
      return await api.getAnalysisReplay(id)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch replay'
    }
  }

  // ── Cancel analysis ──
  async function cancel(id: string) {
    try {
      await api.cancelAnalysis(id)
      const job = jobs.value.find(j => j.id === id)
      if (job) job.status = 'failed'
    } catch (e: any) {
      error.value = e.message || 'Failed to cancel analysis'
    }
  }

  // ── Filters ──
  async function fetchFilters() {
    try {
      const data = await api.getFilters()
      filters.value = data.filters || data || []
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch filters'
    }
  }

  async function saveFilter(config: object) {
    try {
      const data = await api.createFilter(config)
      filters.value.push(data)
      return data
    } catch (e: any) {
      error.value = e.message || 'Failed to save filter'
      throw e
    }
  }

  async function removeFilter(id: string) {
    try {
      await api.deleteFilter(id)
      filters.value = filters.value.filter(f => f.id !== id)
    } catch (e: any) {
      error.value = e.message || 'Failed to delete filter'
    }
  }

  // ── Fetch analysis details ──
  async function fetchAnalysis(id: string) {
    loading.value = true
    try {
      const data = await api.getAnalysis(id)
      currentAnalysis.value = data
      return data
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch analysis'
    } finally {
      loading.value = false
    }
  }

  function getJobById(id: string) {
    return jobs.value.find(j => j.id === id)
  }

  function updateJobStatus(id: string, status: AnalysisJob['status'], step?: number) {
    const job = jobs.value.find(j => j.id === id)
    if (job) {
      job.status = status
      if (step !== undefined) job.currentStep = step
    }
  }

  return {
    jobs, filters, currentAnalysis, progress, report, loading, error,
    completedJobs, runningJobs,
    startReverse, startForward, fetchProgress, fetchReport, fetchReplay,
    cancel, fetchFilters, saveFilter, removeFilter, fetchAnalysis,
    getJobById, updateJobStatus
  }
})
