<template>
  <div class="history-page">
    <div class="history-header">
      <h1 class="page-title glow-text">{{ t('history.title') || 'Analysis History' }}</h1>
      <div class="header-actions">
        <GlowButton variant="ghost" @click="exportData">Export CSV</GlowButton>
        <GlowButton @click="$router.push('/filters')">New Analysis</GlowButton>
      </div>
    </div>

    <div class="history-filters">
      <select v-model="filterType" class="glow-input">
        <option value="">All Types</option>
        <option value="forward">Forward</option>
        <option value="reverse">Reverse</option>
      </select>
      <select v-model="filterStatus" class="glow-input">
        <option value="">All Status</option>
        <option value="completed">Completed</option>
        <option value="running">Running</option>
        <option value="failed">Failed</option>
      </select>
      <input v-model="searchQuery" type="text" class="glow-input search-input" placeholder="Search by address..." />
    </div>

    <div class="history-table">
      <div class="table-header">
        <span class="col-addr">Address</span>
        <span class="col-type">Type</span>
        <span class="col-token">Token</span>
        <span class="col-score">Score</span>
        <span class="col-status">Status</span>
        <span class="col-date">Date</span>
        <span class="col-actions">Actions</span>
      </div>
      <div v-for="item in filteredHistory" :key="item.id" class="table-row" @click="openAnalysis(item)">
        <span class="col-addr mono-number">{{ shortAddr(item.address) }}</span>
        <span class="col-type"><span class="type-badge" :class="item.type">{{ item.type }}</span></span>
        <span class="col-token">{{ item.token || '-' }}</span>
        <span class="col-score mono-number">{{ item.score || '-' }}</span>
        <span class="col-status"><span class="status-badge" :class="item.status">{{ item.status }}</span></span>
        <span class="col-date mono-number">{{ item.date }}</span>
        <span class="col-actions">
          <button class="action-btn" @click.stop="$router.push(`/${item.type}/${item.id}`)">View</button>
          <button class="action-btn" @click.stop="$router.push(`/replay/${item.address}?token=${item.token}`)">Replay</button>
        </span>
      </div>
      <div v-if="!filteredHistory.length" class="empty-table">
        <span>No analysis history found.</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import GlowButton from '@/components/common/GlowButton.vue'

const { t } = useI18n()
const router = useRouter()

const filterType = ref('')
const filterStatus = ref('')
const searchQuery = ref('')

const history = ref([
  { id: 'a1', address: '0xabcdef1234567890abcdef1234567890abcdef12', type: 'reverse', token: 'TOKEN_X', score: 82, status: 'completed', date: '2026-05-10' },
  { id: 'a2', address: '0x1234567890abcdef1234567890abcdef12345678', type: 'forward', token: 'ETH', score: 71, status: 'completed', date: '2026-05-09' },
  { id: 'a3', address: '0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef', type: 'reverse', token: 'BNB', score: null, status: 'running', date: '2026-05-11' },
  { id: 'a4', address: '0x9876543210fedcba9876543210fedcba98765432', type: 'forward', token: 'SOL', score: 55, status: 'completed', date: '2026-05-08' },
  { id: 'a5', address: '0xaaaa1111bbbb2222cccc3333dddd4444eeee5555', type: 'reverse', token: 'ARB', score: null, status: 'failed', date: '2026-05-07' }
])

const filteredHistory = computed(() => {
  return history.value.filter(item => {
    if (filterType.value && item.type !== filterType.value) return false
    if (filterStatus.value && item.status !== filterStatus.value) return false
    if (searchQuery.value && !item.address.toLowerCase().includes(searchQuery.value.toLowerCase())) return false
    return true
  })
})

function shortAddr(addr: string) {
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`
}

function openAnalysis(item: any) {
  router.push(`/${item.type}/${item.id}`)
}

function exportData() {
  const csv = ['Address,Type,Token,Score,Status,Date']
    .concat(history.value.map(h => `${h.address},${h.type},${h.token},${h.score},${h.status},${h.date}`))
    .join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'analysis-history.csv'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.history-page { padding: 24px; max-width: 1200px; margin: 0 auto; }
.history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 24px; font-family: var(--font-mono); color: var(--accent); margin: 0; }
.header-actions { display: flex; gap: 10px; }
.history-filters { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.glow-input { padding: 8px 12px; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-family: var(--font-mono); font-size: 13px; }
.glow-input:focus { border-color: var(--accent); outline: none; }
.search-input { flex: 1; min-width: 200px; }
.history-table { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.table-header { display: grid; grid-template-columns: 2fr 80px 80px 70px 90px 100px 120px; gap: 8px; padding: 10px 14px; background: rgba(0,229,255,0.05); font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
.table-row { display: grid; grid-template-columns: 2fr 80px 80px 70px 90px 100px 120px; gap: 8px; padding: 10px 14px; font-size: 13px; cursor: pointer; transition: background 0.2s; border-top: 1px solid rgba(255,255,255,0.03); }
.table-row:hover { background: rgba(0,229,255,0.04); }
.col-addr { color: var(--accent); }
.col-score { font-weight: 600; }
.col-date { color: var(--text-muted); font-size: 12px; }
.type-badge { font-size: 10px; padding: 2px 6px; border-radius: 4px; }
.type-badge.forward { background: rgba(0,229,255,0.15); color: #00e5ff; }
.type-badge.reverse { background: rgba(124,58,237,0.15); color: #7c3aed; }
.status-badge { font-size: 10px; padding: 2px 6px; border-radius: 4px; }
.status-badge.completed { background: rgba(0,255,136,0.15); color: #00ff88; }
.status-badge.running { background: rgba(0,229,255,0.15); color: #00e5ff; }
.status-badge.failed { background: rgba(255,51,102,0.15); color: #ff3366; }
.action-btn { font-size: 11px; padding: 3px 8px; border: 1px solid var(--border); border-radius: 3px; background: transparent; color: var(--accent); cursor: pointer; margin-right: 4px; transition: all 0.2s; }
.action-btn:hover { border-color: var(--accent); background: rgba(0,229,255,0.1); }
.empty-table { text-align: center; padding: 40px; color: var(--text-muted); }
</style>
