<template>
  <div class="dashboard">
    <h1 class="page-title glow-text">{{ t('dashboard.title') }}</h1>

    <div class="dashboard-grid">
      <section class="feed-section">
        <h2>{{ t('dashboard.liveFeed') }}</h2>
        <WhaleFeed :items="feedItems" @analyze="onAnalyze" />
      </section>

      <div class="side-panels">
        <section class="filters-section">
          <h2>{{ t('dashboard.activeFilters') }}</h2>
          <div v-for="filter in activeFilters" :key="filter.id" class="filter-item glow-card">
            <span class="filter-name">{{ filter.name }}</span>
            <span class="filter-status" :style="{ color: filter.active ? '#00ff88' : '#8892a0' }">
              {{ filter.active ? 'Running' : 'Paused' }}
            </span>
          </div>
          <GlowButton @click="$router.push('/filters')">{{ t('dashboard.newFilter') }}</GlowButton>
        </section>

        <section class="analysis-section">
          <h2>{{ t('dashboard.recentAnalysis') }}</h2>
          <div v-for="item in recentAnalyses" :key="item.id" class="analysis-item"
            @click="$router.push(`/analysis/${item.id}`)">
            <span class="addr mono-number">{{ shortAddr(item.address) }}</span>
            <span class="type" :class="item.type">{{ item.type }}</span>
            <span class="status">{{ item.status }}</span>
            <span class="score mono-number">{{ item.score || '-' }}</span>
          </div>
          <GlowButton @click="$router.push('/history')">{{ t('dashboard.viewAll') }}</GlowButton>
        </section>

        <section class="quota-section glow-card">
          <h2>{{ t('dashboard.apiQuota') }}</h2>
          <ProgressGlow :pct="(apiUsed / apiLimit) * 100" />
          <span class="quota-text mono-number">{{ apiUsed }} / {{ apiLimit }}</span>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import WhaleFeed from '@/components/whale/WhaleFeed.vue'
import GlowButton from '@/components/common/GlowButton.vue'
import ProgressGlow from '@/components/common/ProgressGlow.vue'

const { t } = useI18n()
const router = useRouter()

const feedItems = ref([])
const activeFilters = ref([
  { id: '1', name: 'BSC 大额交易', active: true },
  { id: '2', name: '新Token鲸鱼', active: false }
])
const recentAnalyses = ref([
  { id: 'a1', address: '0xabcdef1234567890', type: 'reverse', status: 'completed', score: 82 },
  { id: 'a2', address: '0x1234567890abcdef', type: 'forward', status: 'running', score: null }
])
const apiUsed = ref(142)
const apiLimit = ref(1000)

function shortAddr(addr: string) {
  return addr ? `${addr.slice(0, 6)}...${addr.slice(-4)}` : ''
}

function onAnalyze(address: string) {
  router.push(`/reverse/${address}`)
}
</script>

<style scoped>
.dashboard { padding: 24px; max-width: 1400px; margin: 0 auto; }
.page-title { font-size: 24px; font-family: var(--font-mono); margin-bottom: 24px; color: var(--accent); }
.dashboard-grid { display: grid; grid-template-columns: 1fr 380px; gap: 24px; }
.feed-section h2, .side-panels h2 { font-size: 14px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
.side-panels { display: flex; flex-direction: column; gap: 20px; }
.filter-item, .analysis-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; margin-bottom: 8px; cursor: pointer; }
.analysis-item { font-size: 13px; }
.analysis-item .type { font-size: 10px; padding: 2px 6px; border-radius: 4px; }
.type.reverse { background: rgba(124,58,237,0.2); color: #7c3aed; }
.type.forward { background: rgba(0,229,255,0.2); color: #00e5ff; }
.quota-text { font-size: 12px; color: var(--text-muted); margin-top: 8px; display: block; }
</style>
