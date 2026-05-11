<template>
  <div class="whale-detail">
    <div class="detail-header">
      <div class="address-section">
        <h2 class="whale-address mono-number">{{ whale.address }}</h2>
        <div class="whale-badges">
          <span v-for="tag in whale.labels" :key="tag" class="badge">{{ tag }}</span>
        </div>
      </div>
      <div class="score-section">
        <div class="score-ring" :style="{ borderColor: scoreColor }">
          <span class="score-num mono-number" :style="{ color: scoreColor }">{{ whale.score?.toFixed(0) }}</span>
        </div>
        <span class="score-label">Score</span>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card glow-card">
        <span class="stat-label">Total Profit</span>
        <span class="stat-value mono-number">{{ formatCurrency(whale.total_profit_usd) }}</span>
      </div>
      <div class="stat-card glow-card">
        <span class="stat-label">Win Rate</span>
        <span class="stat-value mono-number">{{ whale.win_rate?.toFixed(1) }}%</span>
      </div>
      <div class="stat-card glow-card">
        <span class="stat-label">ROI</span>
        <span class="stat-value mono-number">{{ whale.roi?.toFixed(2) }}x</span>
      </div>
      <div class="stat-card glow-card">
        <span class="stat-label">Total Trades</span>
        <span class="stat-value mono-number">{{ whale.trade_count }}</span>
      </div>
      <div class="stat-card glow-card">
        <span class="stat-label">Avg Hold Time</span>
        <span class="stat-value mono-number">{{ whale.avg_hold_days || '-' }}d</span>
      </div>
      <div class="stat-card glow-card">
        <span class="stat-label">Active Chains</span>
        <span class="stat-value mono-number">{{ whale.chains?.length || 0 }}</span>
      </div>
    </div>

    <div v-if="whale.recent_trades?.length" class="recent-trades">
      <h3>Recent Trades</h3>
      <div class="trades-table">
        <div v-for="trade in whale.recent_trades" :key="trade.id" class="trade-row">
          <span class="trade-type" :class="trade.type">{{ trade.type }}</span>
          <span class="trade-token">{{ trade.token }}</span>
          <span class="trade-amount mono-number">{{ trade.amount }}</span>
          <span class="trade-pnl mono-number" :class="{ positive: trade.pnl > 0, negative: trade.pnl < 0 }">
            {{ trade.pnl > 0 ? '+' : '' }}{{ trade.pnl?.toFixed(2) }}%
          </span>
          <span class="trade-time">{{ trade.time }}</span>
        </div>
      </div>
    </div>

    <div class="detail-actions">
      <GlowButton variant="primary" @click="$emit('analyze', whale.address)">Run Analysis</GlowButton>
      <GlowButton variant="ghost" @click="$emit('track', whale.address)">Track Whale</GlowButton>
      <GlowButton variant="ghost" @click="$emit('export', whale)">Export Data</GlowButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import GlowButton from '@/components/common/GlowButton.vue'
import { formatCurrency } from '@/i18n/helpers/number-format'

const props = defineProps<{ whale: any }>()
defineEmits(['analyze', 'track', 'export'])

const scoreColor = computed(() => {
  const s = props.whale.score || 0
  if (s >= 80) return '#00ff88'
  if (s >= 60) return '#00e5ff'
  if (s >= 40) return '#ffaa00'
  return '#ff3366'
})
</script>

<style scoped>
.whale-detail { padding: 20px 0; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.address-section { flex: 1; }
.whale-address { font-size: 18px; color: var(--accent); word-break: break-all; margin: 0 0 8px; }
.whale-badges { display: flex; gap: 6px; flex-wrap: wrap; }
.badge { font-size: 11px; padding: 2px 10px; border-radius: 10px; background: rgba(0,229,255,0.1); color: var(--accent); border: 1px solid rgba(0,229,255,0.2); }
.score-section { text-align: center; }
.score-ring { width: 64px; height: 64px; border: 3px solid; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 4px; }
.score-num { font-size: 22px; font-weight: 700; }
.score-label { font-size: 11px; color: var(--text-muted); }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
.stat-card { text-align: center; padding: 14px; }
.stat-card .stat-label { display: block; font-size: 11px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px; }
.stat-card .stat-value { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.recent-trades h3 { font-size: 14px; color: var(--text-secondary); margin-bottom: 12px; }
.trades-table { display: flex; flex-direction: column; gap: 4px; }
.trade-row { display: grid; grid-template-columns: 60px 1fr 100px 80px 80px; gap: 8px; align-items: center; padding: 8px 10px; font-size: 12px; border-radius: 4px; background: rgba(0,0,0,0.1); }
.trade-type { font-size: 10px; padding: 2px 6px; border-radius: 3px; text-align: center; }
.trade-type.buy { background: rgba(0,255,136,0.15); color: #00ff88; }
.trade-type.sell { background: rgba(255,51,102,0.15); color: #ff3366; }
.trade-token { color: var(--text-primary); }
.trade-amount { color: var(--text-secondary); text-align: right; }
.trade-pnl { text-align: right; font-weight: 600; }
.trade-pnl.positive { color: #00ff88; }
.trade-pnl.negative { color: #ff3366; }
.trade-time { color: var(--text-muted); text-align: right; }
.detail-actions { display: flex; gap: 10px; margin-top: 20px; }
</style>
