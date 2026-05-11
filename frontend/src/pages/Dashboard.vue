<template>
  <div class="dashboard">
    <h1 class="page-title glow-text">{{ t('dashboard.title') }}</h1>

    <div class="dashboard-grid">
      <section class="feed-section">
        <h2>{{ t('dashboard.liveFeed') }}</h2>
        <div v-if="whaleStore.loading" class="loading-state">Loading feed...</div>
        <div v-else-if="whaleStore.error" class="error-state">{{ whaleStore.error }}</div>
        <WhaleFeed v-else :items="whaleStore.feedItems" @analyze="onAnalyze" />
      </section>

      <div class="side-panels">
        <section class="filters-section">
          <h2>{{ t('dashboard.activeFilters') }}</h2>
          <div v-for="filter in analysisStore.filters" :key="filter.id" class="filter-item glow-card">
            <span class="filter-name">{{ filter.name }}</span>
            <span class="filter-status" style="color: #00ff88">Active</span>
          </div>
          <div v-if="!analysisStore.filters.length" class="empty-hint">No filters configured</div>
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
          <ProgressGlow :pct="quotaPct" />
          <span class="quota-text mono-number">{{ apiUsed }} / {{ apiLimit }}</span>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useWhaleStore } from '@/stores/whale'
import { useAnalysisStore } from '@/stores/analysis'
import * as api from '@/services/api'
import WhaleFeed from '@/components/whale/WhaleFeed.vue'
import GlowButton from '@/components/common/GlowButton.vue'
import ProgressGlow from '@/components/common/ProgressGlow.vue'

const { t } = useI18n()
const router = useRouter()
const whaleStore = useWhaleStore()
const analysisStore = useAnalysisStore()

const recentAnalyses = ref<Array<{ id: string; address: string; type: string; status: string; score: number | null }>>([])
const apiUsed = ref(0)
const apiLimit = ref(1000)
const quotaPct = computed(() => apiLimit.value > 0 ? (apiUsed.value / apiLimit.value) * 100 : 0)

function shortAddr(addr: string) {
  return addr ? `${addr.slice(0, 6)}...${addr.slice(-4)}` : ''
}

async function onAnalyze(address: string) {
  try {
    const analysisId = await analysisStore.startReverse(address)
    router.push(`/reverse/${analysisId}`)
  } catch {
    // If API fails, still navigate with address
    router.push(`/reverse/${address}`)
  }
}

onMounted(async () => {
  // Fetch real data
  whaleStore.fetchFeed()
  analysisStore.fetchFilters()

  // Fetch quota
  try {
    const quota = await api.getSystemQuota()
    apiUsed.value = quota.used ?? quota.api_used ?? 0
    apiLimit.value = quota.limit ?? quota.api_limit ?? 1000
  } catch { /* use defaults */ }

  // Fetch recent analyses for history
  try {
    const history = await api.getHistory(1, 5)
    recentAnalyses.value = (history.items || history || []).map((h: any) => ({
      id: h.id || h.analysis_id,
      address: h.whale_address || h.address || '',
      type: h.type || 'reverse',
      status: h.status || 'completed',
      score: h.score ?? h.confidence ?? null
    }))
  } catch { /* empty */ }
})
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
.loading-state, .error-state, .empty-hint { font-size: 13px; color: var(--text-muted); padding: 12px; text-align: center; }
.error-state { color: #ff6b6b; }
</style>
