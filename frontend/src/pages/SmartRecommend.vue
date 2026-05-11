<template>
  <div class="smart-recommend">
    <h1 class="page-title glow-text">{{ t('recommend.title') || 'Smart Recommendations' }}</h1>
    <p class="page-desc">AI-powered whale recommendations based on your filter criteria and market conditions.</p>

    <div class="recommendations-grid">
      <div v-for="rec in recommendations" :key="rec.id" class="rec-card glow-card">
        <div class="rec-header">
          <div class="rec-score-ring" :style="{ borderColor: scoreColor(rec.score) }">
            <span class="rec-score mono-number" :style="{ color: scoreColor(rec.score) }">{{ rec.score }}</span>
          </div>
          <div class="rec-meta">
            <span class="rec-addr mono-number">{{ shortAddr(rec.address) }}</span>
            <span class="rec-reason">{{ rec.reason }}</span>
          </div>
          <span class="rec-confidence" :style="{ color: confidenceColor(rec.confidence) }">{{ rec.confidence }}</span>
        </div>

        <div class="rec-body">
          <div class="rec-stats">
            <div class="stat"><span class="s-label">Profit</span><span class="s-value mono-number">${{ formatK(rec.profit) }}</span></div>
            <div class="stat"><span class="s-label">Win Rate</span><span class="s-value mono-number">{{ rec.winrate }}%</span></div>
            <div class="stat"><span class="s-label">Pattern</span><span class="s-value">{{ rec.pattern }}</span></div>
            <div class="stat"><span class="s-label">Timeframe</span><span class="s-value mono-number">{{ rec.timeframe }}</span></div>
          </div>

          <div class="rec-insight">
            <span class="insight-icon">💡</span>
            <p class="insight-text">{{ rec.insight }}</p>
          </div>

          <div class="rec-tags">
            <span v-for="tag in rec.tags" :key="tag" class="rec-tag">{{ tag }}</span>
          </div>
        </div>

        <div class="rec-actions">
          <GlowButton variant="primary" @click="applyRecommendation(rec)">Apply & Analyze</GlowButton>
          <GlowButton variant="ghost" @click="ignoreRecommendation(rec)">Ignore</GlowButton>
        </div>
      </div>
    </div>

    <div v-if="!recommendations.length" class="empty-state">
      <span class="empty-icon">🤖</span>
      <p>No recommendations at the moment. Check back later.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import GlowButton from '@/components/common/GlowButton.vue'

const { t } = useI18n()
const router = useRouter()

const recommendations = ref([
  {
    id: 'r1',
    address: '0xabcdef1234567890abcdef1234567890abcdef12',
    score: 92,
    reason: 'Consistent high-win-rate trader with smart entry timing',
    confidence: 'High',
    profit: 2450000,
    winrate: 78,
    pattern: 'Smart Accumulation',
    timeframe: '7d',
    insight: 'This whale has been consistently profitable across 3 market cycles. Their entry pattern shows strong correlation with on-chain volume signals. Currently accumulating a new position.',
    tags: ['BSC', 'DeFi', 'Smart Money'],
    status: 'active'
  },
  {
    id: 'r2',
    address: '0x1234567890abcdef1234567890abcdef12345678',
    score: 85,
    reason: 'Early token discovery pattern detected',
    confidence: 'Medium-High',
    profit: 1800000,
    winrate: 72,
    pattern: 'Early Discovery',
    timeframe: '3d',
    insight: 'This wallet has found 5 tokens that did 10x+ in the past 90 days. Currently entering 2 new positions on Ethereum. Historical pattern suggests 3-5x potential.',
    tags: ['ETH', 'Alpha', 'Early'],
    status: 'active'
  },
  {
    id: 'r3',
    address: '0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef',
    score: 78,
    reason: 'Cross-chain arbitrage specialist',
    confidence: 'Medium',
    profit: 950000,
    winrate: 65,
    pattern: 'Cross-Chain Arb',
    timeframe: '1d',
    insight: 'This whale executes cross-chain arbitrage between BSC and Arbitrum. Consistent small profits with low drawdown. Currently active on 3 chains.',
    tags: ['Multi-Chain', 'Arbitrage', 'Low Risk'],
    status: 'active'
  }
])

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

function confidenceColor(c: string) {
  if (c === 'High') return '#00ff88'
  if (c.includes('Medium')) return '#00e5ff'
  return '#ffaa00'
}

function applyRecommendation(rec: any) {
  router.push(`/reverse/${rec.address}`)
}

function ignoreRecommendation(rec: any) {
  recommendations.value = recommendations.value.filter(r => r.id !== rec.id)
}
</script>

<style scoped>
.smart-recommend { padding: 24px; max-width: 1200px; margin: 0 auto; }
.page-title { font-size: 24px; font-family: var(--font-mono); color: var(--accent); margin-bottom: 4px; }
.page-desc { font-size: 14px; color: var(--text-muted); margin-bottom: 24px; }
.recommendations-grid { display: flex; flex-direction: column; gap: 16px; }
.rec-card { padding: 20px; transition: all 0.2s; }
.rec-card:hover { border-color: rgba(0,229,255,0.3); box-shadow: 0 0 16px rgba(0,229,255,0.15); }
.rec-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.rec-score-ring { width: 48px; height: 48px; border: 2px solid; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.rec-score { font-size: 18px; font-weight: 700; }
.rec-meta { flex: 1; }
.rec-addr { font-size: 14px; color: var(--accent); display: block; margin-bottom: 2px; }
.rec-reason { font-size: 13px; color: var(--text-secondary); }
.rec-confidence { font-size: 12px; font-family: var(--font-mono); font-weight: 600; }
.rec-body { margin-bottom: 16px; }
.rec-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 14px; }
.stat { text-align: center; }
.s-label { display: block; font-size: 10px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 2px; }
.s-value { font-size: 13px; color: var(--text-primary); font-weight: 500; }
.rec-insight { display: flex; gap: 10px; padding: 12px; background: rgba(0,229,255,0.03); border-radius: 6px; border-left: 2px solid var(--accent); margin-bottom: 12px; }
.insight-icon { font-size: 18px; flex-shrink: 0; }
.insight-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin: 0; }
.rec-tags { display: flex; gap: 4px; flex-wrap: wrap; }
.rec-tag { font-size: 10px; padding: 2px 8px; border-radius: 10px; background: rgba(0,229,255,0.1); color: var(--accent); border: 1px solid rgba(0,229,255,0.2); }
.rec-actions { display: flex; gap: 10px; justify-content: flex-end; }
.empty-state { text-align: center; padding: 60px 20px; color: var(--text-muted); }
.empty-icon { font-size: 48px; display: block; margin-bottom: 12px; }
</style>
