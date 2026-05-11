import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '@/services/api'

export interface WhaleAddress {
  id: string
  address: string
  chain: string
  label: string
  profit: number
  winRate: number
  roi: number
  trades: number
  tokens: string[]
  lastActive: string
  score: number
  behaviorTag: string
  riskProfile: 'low' | 'medium' | 'high'
}

export interface WhaleFeedItem {
  id: string
  whaleId: string
  address: string
  action: 'buy' | 'sell' | 'transfer' | 'approve'
  token: string
  amount: number
  value: number
  chain: string
  timestamp: string
  txHash: string
}

export const useWhaleStore = defineStore('whale', () => {
  const whales = ref<WhaleAddress[]>([])
  const feedItems = ref<WhaleFeedItem[]>([])
  const currentWhale = ref<any>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const activeWhales = computed(() =>
    whales.value.filter(w => Date.now() - new Date(w.lastActive).getTime() < 86400000)
  )
  const topWhales = computed(() => [...whales.value].sort((a, b) => b.score - a.score))

  async function fetchFeed(chain = 'bsc', minValue = 100000, limit = 50) {
    loading.value = true
    error.value = null
    try {
      const data = await api.getWhaleFeed(chain, minValue, limit)
      feedItems.value = data.feed || data.items || data || []
      if (data.whales) whales.value = data.whales
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch whale feed'
      console.error('fetchFeed error:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchDetail(address: string) {
    loading.value = true
    error.value = null
    try {
      currentWhale.value = await api.getWhaleDetail(address)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch whale detail'
    } finally {
      loading.value = false
    }
  }

  async function fetchLibrary() {
    loading.value = true
    try {
      const data = await api.getWhaleLibrary()
      whales.value = data.whales || data || []
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch library'
    } finally {
      loading.value = false
    }
  }

  async function addWhaleToLibrary(address: string, nickname?: string) {
    try {
      await api.addToLibrary(address, nickname)
      await fetchLibrary()
    } catch (e: any) {
      error.value = e.message || 'Failed to add to library'
    }
  }

  function addFeedItem(item: WhaleFeedItem) {
    feedItems.value.unshift(item)
    if (feedItems.value.length > 100) feedItems.value.pop()
  }

  function getWhaleById(id: string) {
    return whales.value.find(w => w.id === id)
  }

  return {
    whales, feedItems, currentWhale, loading, error,
    activeWhales, topWhales,
    fetchFeed, fetchDetail, fetchLibrary, addWhaleToLibrary,
    addFeedItem, getWhaleById
  }
})
