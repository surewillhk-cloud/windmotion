<template>
  <div class="whale-library">
    <div class="library-header">
      <h1 class="page-title glow-text">{{ t('whales.title') || 'Whale Library' }}</h1>
      <div class="header-controls">
        <input v-model="searchQuery" type="text" class="glow-input search-input" placeholder="Search address, tag..." />
        <select v-model="sortBy" class="glow-input">
          <option value="score">Score</option>
          <option value="profit">Profit</option>
          <option value="winrate">Win Rate</option>
          <option value="trades">Trades</option>
        </select>
        <button :class="['sort-dir', sortDir]" @click="sortDir = sortDir === 'desc' ? 'asc' : 'desc'">
          {{ sortDir === 'desc' ? '↓' : '↑' }}
        </button>
      </div>
    </div>

    <div class="tag-filters">
      <button :class="['tag-btn', { active: !activeTag }]" @click="activeTag = ''">All</button>
      <button v-for="tag in allTags" :key="tag" :class="['tag-btn', { active: activeTag === tag }]" @click="activeTag = tag">
        {{ tag }}
      </button>
    </div>

    <div class="whales-grid">
      <WhaleCard v-for="whale in filteredWhales" :key="whale.address" :whale="whale"
        @click="openDetail(whale)" @analyze="analyzeWhale" />
    </div>

    <div v-if="!filteredWhales.length" class="empty-state">
      <span class="empty-icon">🐋</span>
      <p>No whales found matching your criteria.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import WhaleCard from '@/components/whale/WhaleCard.vue'

const { t } = useI18n()
const router = useRouter()

const searchQuery = ref('')
const sortBy = ref('score')
const sortDir = ref<'asc' | 'desc'>('desc')
const activeTag = ref('')

const whales = ref([
  { address: '0xabcdef1234567890abcdef1234567890abcdef12', score: 92, total_profit_usd: 2450000, win_rate: 78, roi: 4.2, trade_count: 145, labels: ['Smart Money', 'BSC', 'DeFi'] },
  { address: '0x1234567890abcdef1234567890abcdef12345678', score: 85, total_profit_usd: 1800000, win_rate: 72, roi: 3.5, trade_count: 98, labels: ['Whale', 'ETH', 'NFT'] },
  { address: '0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef', score: 78, total_profit_usd: 950000, win_rate: 65, roi: 2.8, trade_count: 67, labels: ['DeFi', 'Arbitrum'] },
  { address: '0x9876543210fedcba9876543210fedcba98765432', score: 71, total_profit_usd: 620000, win_rate: 61, roi: 2.1, trade_count: 45, labels: ['New', 'Solana'] },
  { address: '0xaaaa1111bbbb2222cccc3333dddd4444eeee5555', score: 65, total_profit_usd: 380000, win_rate: 58, roi: 1.8, trade_count: 34, labels: ['BSC', 'Meme'] },
  { address: '0xffff999988887777666655554444333322221111', score: 58, total_profit_usd: 210000, win_rate: 52, roi: 1.5, trade_count: 28, labels: ['ETH', 'Layer2'] }
])

const allTags = computed(() => {
  const tags = new Set<string>()
  whales.value.forEach(w => w.labels.forEach(l => tags.add(l)))
  return Array.from(tags).sort()
})

const filteredWhales = computed(() => {
  let list = [...whales.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(w =>
      w.address.toLowerCase().includes(q) ||
      w.labels.some(l => l.toLowerCase().includes(q))
    )
  }

  if (activeTag.value) {
    list = list.filter(w => w.labels.includes(activeTag.value))
  }

  list.sort((a, b) => {
    const mul = sortDir.value === 'desc' ? -1 : 1
    const key = sortBy.value === 'winrate' ? 'win_rate' : sortBy.value === 'trades' ? 'trade_count' : sortBy.value === 'profit' ? 'total_profit_usd' : 'score'
    return ((a as any)[key] - (b as any)[key]) * mul
  })

  return list
})

function openDetail(whale: any) {
  router.push(`/whale/${whale.address}`)
}

function analyzeWhale(address: string) {
  router.push(`/reverse/${address}`)
}
</script>

<style scoped>
.whale-library { padding: 24px; max-width: 1200px; margin: 0 auto; }
.library-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 24px; font-family: var(--font-mono); color: var(--accent); margin: 0; }
.header-controls { display: flex; gap: 10px; align-items: center; }
.glow-input { padding: 8px 12px; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-family: var(--font-mono); font-size: 13px; }
.glow-input:focus { border-color: var(--accent); outline: none; }
.search-input { width: 260px; }
.sort-dir { background: transparent; border: 1px solid var(--border); color: var(--accent); padding: 8px 10px; border-radius: 4px; cursor: pointer; }
.tag-filters { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 20px; }
.tag-btn { font-size: 11px; padding: 4px 12px; border-radius: 14px; border: 1px solid var(--border); background: transparent; color: var(--text-muted); cursor: pointer; transition: all 0.2s; }
.tag-btn:hover { border-color: var(--accent); }
.tag-btn.active { background: rgba(0,229,255,0.15); border-color: var(--accent); color: var(--accent); }
.whales-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 14px; }
.empty-state { text-align: center; padding: 60px 20px; color: var(--text-muted); }
.empty-icon { font-size: 48px; display: block; margin-bottom: 12px; }
</style>
