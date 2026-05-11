<template>
  <div class="environment-state">
    <h3 class="env-title">Environment State</h3>
    <div class="env-grid">
      <div v-for="item in stateItems" :key="item.key" class="env-item">
        <span class="env-label">{{ item.label }}</span>
        <span class="env-value mono-number" :style="{ color: item.color || 'var(--text-primary)' }">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  state: Record<string, any>
  labels?: Record<string, string>
}>()

const defaultLabels: Record<string, string> = {
  market_trend: 'Market Trend',
  volatility: 'Volatility',
  liquidity: 'Liquidity',
  sentiment: 'Sentiment',
  volume_24h: '24h Volume',
  holder_count: 'Holders'
}

const stateItems = computed(() => {
  const labs = props.labels || defaultLabels
  return Object.entries(props.state).map(([key, value]) => {
    let color = 'var(--text-primary)'
    if (typeof value === 'string') {
      if (value === 'bullish' || value === 'high' || value === 'positive') color = '#00ff88'
      else if (value === 'bearish' || value === 'low' || value === 'negative') color = '#ff3366'
      else if (value === 'neutral' || value === 'medium') color = '#ffaa00'
    }
    return { key, label: labs[key] || key, value: String(value), color }
  })
})
</script>

<style scoped>
.environment-state { padding: 12px 0; }
.env-title { font-size: 14px; color: var(--text-secondary); font-weight: 500; margin-bottom: 12px; }
.env-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.env-item { display: flex; flex-direction: column; gap: 2px; padding: 8px 10px; background: rgba(0,0,0,0.15); border-radius: 4px; }
.env-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }
.env-value { font-size: 14px; font-weight: 600; }
</style>
