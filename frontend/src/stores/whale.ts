import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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
  const whales = ref<WhaleAddress[]>([
    {
      id: 'w1',
      address: '0x1234...5678',
      chain: 'Ethereum',
      label: 'ETH Whale Alpha',
      profit: 2450000,
      winRate: 78.5,
      roi: 342.1,
      trades: 156,
      tokens: ['ETH', 'UNI', 'AAVE', 'LINK'],
      lastActive: new Date(Date.now() - 3600000).toISOString(),
      score: 92,
      behaviorTag: 'earlyBird',
      riskProfile: 'medium'
    },
    {
      id: 'w2',
      address: '0xabcd...ef01',
      chain: 'Ethereum',
      label: 'DeFi Master',
      profit: 1870000,
      winRate: 82.3,
      roi: 289.7,
      trades: 203,
      tokens: ['ETH', 'MKR', 'COMP', 'CRV'],
      lastActive: new Date(Date.now() - 7200000).toISOString(),
      score: 88,
      behaviorTag: 'dcaMaster',
      riskProfile: 'low'
    },
    {
      id: 'w3',
      address: '0x9876...5432',
      chain: 'BSC',
      label: 'BSC Sniper',
      profit: 980000,
      winRate: 65.2,
      roi: 567.3,
      trades: 412,
      tokens: ['BNB', 'CAKE', 'XVS', 'BAKE'],
      lastActive: new Date(Date.now() - 1800000).toISOString(),
      score: 79,
      behaviorTag: 'sniperEntry',
      riskProfile: 'high'
    }
  ])

  const feedItems = ref<WhaleFeedItem[]>([
    {
      id: 'f1',
      whaleId: 'w1',
      address: '0x1234...5678',
      action: 'buy',
      token: 'ETH',
      amount: 150,
      value: 525000,
      chain: 'Ethereum',
      timestamp: new Date(Date.now() - 120000).toISOString(),
      txHash: '0xabc...def'
    },
    {
      id: 'f2',
      whaleId: 'w2',
      address: '0xabcd...ef01',
      action: 'sell',
      token: 'UNI',
      amount: 25000,
      value: 187500,
      chain: 'Ethereum',
      timestamp: new Date(Date.now() - 300000).toISOString(),
      txHash: '0x123...456'
    },
    {
      id: 'f3',
      whaleId: 'w3',
      address: '0x9876...5432',
      action: 'buy',
      token: 'CAKE',
      amount: 50000,
      value: 95000,
      chain: 'BSC',
      timestamp: new Date(Date.now() - 600000).toISOString(),
      txHash: '0x789...012'
    }
  ])

  const activeWhales = computed(() => whales.value.filter(w => {
    const lastActive = new Date(w.lastActive)
    return Date.now() - lastActive.getTime() < 86400000
  }))

  const topWhales = computed(() => [...whales.value].sort((a, b) => b.score - a.score))

  function addWhale(whale: WhaleAddress) {
    whales.value.push(whale)
  }

  function removeWhale(id: string) {
    whales.value = whales.value.filter(w => w.id !== id)
  }

  function addFeedItem(item: WhaleFeedItem) {
    feedItems.value.unshift(item)
    if (feedItems.value.length > 100) feedItems.value.pop()
  }

  function getWhaleById(id: string) {
    return whales.value.find(w => w.id === id)
  }

  return {
    whales,
    feedItems,
    activeWhales,
    topWhales,
    addWhale,
    removeWhale,
    addFeedItem,
    getWhaleById
  }
})
