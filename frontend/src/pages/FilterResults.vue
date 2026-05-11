<template>
  <div class="filter-results">
    <div class="results-header">
      <h1 class="page-title glow-text">{{ t('results.title') || 'Filter Results' }}</h1>
      <div class="results-controls">
        <select v-model="sortBy" class="glow-input sort-select">
          <option value="score">Score</option>
          <option value="profit">Profit</option>
          <option value="winrate">Win Rate</option>
          <option value="roi">ROI</option>
          <option value="trades">Trades</option>
        </select>
        <button :class="['sort-dir', sortDir]" @click="sortDir = sortDir === 'desc' ? 'asc' : 'desc'">
          {{ sortDir === 'desc' ? '↓' : '↑' }}
        </button>
        <GlowButton variant="ghost" @click="selectAll">{{ allSelected ? 'Deselect All' : 'Select All' }}</GlowButton>
        <GlowButton variant="primary" :disabled="!selectedCount" @click="batchAnalyze">
          Analyze Selected ({{ selectedCount }})
        </GlowButton>
      </div>
    </div>

    <div class="results-count">
      <span class="mono-number">{{ sortedResults.length }}</span> whales found
    </div>

    <div class="results-grid">
      <div v-for="whale in sortedResults" :key="whale.address"
        :class="['result-card glow-card', { selected: selected.has(whale.address) }]">
        <div class="card-select">
          <input type="checkbox" :checked="selected.has(whale.address)" @change="toggleSelect(whale.address)" />
        </div>
        <div class="card-content" @click="$router.push(`/whale/${whale.address}`)">
          <div class="card-header">
            <span class="address mono-number">{{ shortAddr(whale.address) }}</span>
            <span class="score" :style="{ color: scoreColor(whale.score) }">{{ whale.score }}/100</span>
          </div>
          <div class="card-stats">
            <div class="stat"><span class="s-label">Profit</span><span class="s-value mono-number">${{ formatK(whale.profit) }}</span></div>
            <div class="stat"><span class="s-label">Win Rate</span><span class="s-value mono-number">{{ whale.winrate }}%</span></div>
            <div class="stat"><span class="s-label">ROI</span><span class="s-value mono-number">{{ whale.roi }}x</span></div>
            <div class="stat"><span class="s-label">Trades</span><span class="s-value mono-number">{{ whale.trades }}</span></div>
          </div>
          <div class="card-tags">
            <span v-for="tag in whale.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
        <div class="card-actions">
          <GlowButton variant="primary" @click.stop="$router.push(`/reverse/${whale.address}`)">Analyze</GlowButton>
        </div>
      </div>
    </div>

    <div v-if="!sortedResults.length" class="empty-state">
      <span class="empty-icon">🔍</span>
      <p>No whales match your filters. Try adjusting the criteria.</p>
      <GlowButton @click="$router.push('/filters')">Edit Filters</GlowButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import GlowButton from '@/components/common/GlowButton.vue'

const { t } = useI18n()

const sortBy = ref('score')
const sortDir = ref<'asc' | 'desc'>('desc')
const selected = ref(new Set<string>())

const results = ref([
  { address: '0xabcdef1234567890abcdef1234567890abcdef12', score: 92, profit: 245000, winrate: 78, roi: 4.2, trades: 45, tags: ['Smart Money', 'BSC'] },
  { address: '0x1234567890abcdef1234567890abcdef12345678', score: 85, profit: 180000, winrate: 72, roi: 3.5, trades: 32, tags: ['Whale', 'ETH'] },
  { address: '0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef', score: 78, profit: 95000, winrate: 65, roi: 2.8, trades: 28, tags: ['DeFi', 'Arbitrum'] },
  { address: '0x9876543210fedcba9876543210fedcba98765432', score: 71, profit: 62000, winrate: 61, roi: 2.1, trades: 19, tags: ['New', 'Solana'] },
])

const sortedResults = computed(() => {
  return [...results.value].sort((a, b) => {
    const mul = sortDir.value === 'desc' ? -1 : 1
    return (a[sortBy.value as keyof typeof a] as number - (b[sortBy.value as keyof typeof b] as number)) * mul
  })
})

const selectedCount = computed(() => selected.value.size)
const allSelected = computed(() => selected.value.size === results.value.length)

function toggleSelect(addr: string) {
  const s = new Set(selected.value)
  if (s.has(addr)) s.delete(addr)
  else s.add(addr)
  selected.value = s
}

function selectAll() {
  if (allSelected.value) {
    selected.value = new Set()
  } else {
    selected.value = new Set(results.value.map(r => r.address))
  }
}

function batchAnalyze() {
  console.log('Batch analyze:', Array.from(selected.value))
}

function shortAddr(addr: string) {
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`
}

function formatK(n: number) {
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M'
  if (n >= 1e3) return (n / 1e3).toFixed(0) + 'K'
  return n.toString()
}

function scoreColor(s: number) {
  if (s >= 80) return '#00ff88'
  if (s >= 60) return '#00e5ff'
  if (s >= 40) return '#ffaa00'
  return '#ff3366'
}
</script>

<style scoped>
.filter-results { padding: 24px; max-width: 1200px; margin: 0 auto; }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 24px; font-family: var(--font-mono); color: var(--accent); margin: 0; }
.results-controls { display: flex; align-items: center; gap: 10px; }
.sort-select { padding: 6px 10px; font-size: 12px; width: 120px; }
.sort-dir { background: transparent; border: 1px solid var(--border); color: var(--accent); padding: 6px 10px; border-radius: 4px; cursor: pointer; font-size: 14px; }
.sort-dir:hover { border-color: var(--accent); }
.results-count { font-size: 13px; color: var(--text-muted); margin-bottom: 16px; }
.results-grid { display: flex; flex-direction: column; gap: 10px; }
.result-card { display: flex; align-items: center; gap: 12px; padding: 14px; transition: all 0.2s; }
.result-card.selected { border-color: var(--accent); box-shadow: 0 0 8px rgba(0,229,255,0.15); }
.card-select input { accent-color: var(--accent); }
.card-content { flex: 1; cursor: pointer; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.address { font-size: 14px; color: var(--accent); }
.score { font-size: 18px; font-weight: 700; font-family: var(--font-mono); }
.card-stats { display: flex; gap: 20px; margin-bottom: 8px; }
.stat { display: flex; flex-direction: column; gap: 1px; }
.s-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }
.s-value { font-size: 13px; color: var(--text-primary); font-weight: 500; }
.card-tags { display: flex; gap: 4px; }
.tag { font-size: 10px; padding: 2px 8px; border-radius: 10px; background: rgba(0,229,255,0.1); color: var(--accent); border: 1px solid rgba(0,229,255,0.2); }
.card-actions { flex-shrink: 0; }
.empty-state { text-align: center; padding: 60px 20px; color: var(--text-muted); }
.empty-icon { font-size: 48px; display: block; margin-bottom: 12px; }
.glow-input { padding: 8px 12px; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-family: var(--font-mono); font-size: 13px; }
.glow-input:focus { border-color: var(--accent); outline: none; }
</style>
