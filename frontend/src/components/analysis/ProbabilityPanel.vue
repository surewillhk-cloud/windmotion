<template>
  <div class="probability-panel">
    <div class="prob-header">
      <h3>{{ title || 'Probability Estimate' }}</h3>
      <div class="prob-value">
        <span class="prob-number mono-number" :style="{ color: probColor }">{{ probability.toFixed(1) }}%</span>
        <span class="prob-deviation">±{{ stdDev.toFixed(1) }}%</span>
      </div>
    </div>
    <div class="prob-bar-container">
      <div class="prob-bar">
        <div class="prob-fill" :style="{ width: `${probability}%`, background: probGradient }" />
        <div class="prob-std" :style="{ left: `${Math.max(0, probability - stdDev)}%`, width: `${stdDev * 2}%` }" />
      </div>
      <div class="prob-labels">
        <span>0%</span>
        <span>25%</span>
        <span>50%</span>
        <span>75%</span>
        <span>100%</span>
      </div>
    </div>
    <div v-if="spread > 0" class="spread-info">
      <span class="spread-label">Max Spread:</span>
      <span class="spread-value mono-number" :class="{ danger: spread > 30 }">{{ spread.toFixed(0) }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  probability: number
  stdDev?: number
  spread?: number
  title?: string
}>()

const probColor = computed(() => {
  if (props.probability >= 70) return '#00ff88'
  if (props.probability >= 50) return '#00e5ff'
  if (props.probability >= 30) return '#ffaa00'
  return '#ff3366'
})

const probGradient = computed(() => {
  return `linear-gradient(90deg, rgba(0,229,255,0.8), ${probColor.value})`
})
</script>

<style scoped>
.probability-panel { padding: 16px; }
.prob-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.prob-header h3 { font-size: 14px; color: var(--text-secondary); font-weight: 500; }
.prob-value { text-align: right; }
.prob-number { font-size: 28px; font-weight: 700; }
.prob-deviation { font-size: 12px; color: var(--text-muted); margin-left: 6px; }
.prob-bar-container { margin-bottom: 12px; }
.prob-bar { position: relative; height: 8px; background: rgba(0,229,255,0.1); border-radius: 4px; overflow: visible; }
.prob-fill { height: 100%; border-radius: 4px; transition: width 0.8s ease; }
.prob-std { position: absolute; top: -2px; height: 12px; background: rgba(0,229,255,0.1); border-radius: 2px; }
.prob-labels { display: flex; justify-content: space-between; margin-top: 6px; }
.prob-labels span { font-size: 10px; color: var(--text-muted); font-family: var(--font-mono); }
.spread-info { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.spread-label { color: var(--text-muted); }
.spread-value { color: var(--accent); }
.spread-value.danger { color: #ff3366; }
</style>
