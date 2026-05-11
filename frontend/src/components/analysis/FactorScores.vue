<template>
  <div class="factor-scores">
    <h3 v-if="title" class="factor-title">{{ title }}</h3>
    <div v-for="factor in factorList" :key="factor.key" class="factor-row">
      <span class="factor-label">{{ factor.label }}</span>
      <div class="factor-bar">
        <div class="factor-fill" :style="{ width: `${(factor.value / 5) * 100}%`, background: factorColor(factor.value) }" />
      </div>
      <span class="factor-value mono-number" :style="{ color: factorColor(factor.value) }">{{ factor.value.toFixed(1) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  scores: Record<string, number>
  title?: string
  labels?: Record<string, string>
}>()

const defaultLabels: Record<string, string> = {
  F1: 'Entry', F2: 'Exit', F3: 'Position', F4: 'Selection', F5: 'Behavior'
}

const factorList = computed(() => {
  const labs = props.labels || defaultLabels
  return Object.entries(props.scores).map(([key, value]) => ({
    key,
    label: labs[key] || key,
    value
  }))
})

function factorColor(val: number): string {
  if (val >= 4) return '#00ff88'
  if (val >= 3) return '#00e5ff'
  if (val >= 2) return '#ffaa00'
  return '#ff3366'
}
</script>

<style scoped>
.factor-scores { padding: 12px 0; }
.factor-title { font-size: 14px; color: var(--text-secondary); font-weight: 500; margin-bottom: 12px; }
.factor-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.factor-label { font-size: 12px; color: var(--text-muted); min-width: 60px; }
.factor-bar { flex: 1; height: 6px; background: rgba(0,229,255,0.1); border-radius: 3px; overflow: hidden; }
.factor-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
.factor-value { font-size: 13px; font-weight: 600; min-width: 30px; text-align: right; }
</style>
