<template>
  <div class="pattern-card glow-card" :class="{ selected }" @click="$emit('click')">
    <div class="pattern-header">
      <span class="pattern-icon" :style="{ color: patternColor }">◇</span>
      <h4 class="pattern-name">{{ pattern.name }}</h4>
      <span class="pattern-match mono-number" :style="{ color: matchColor }">{{ pattern.match_pct }}%</span>
    </div>
    <p class="pattern-desc">{{ pattern.description }}</p>
    <div class="pattern-tags">
      <span v-for="tag in pattern.tags" :key="tag" class="pattern-tag">{{ tag }}</span>
    </div>
    <div v-if="pattern.historical" class="pattern-history">
      <span class="history-label">Historical:</span>
      <span class="history-value mono-number">{{ pattern.historical.win_rate }}% win rate ({{ pattern.historical.samples }} samples)</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  pattern: {
    name: string
    description: string
    match_pct: number
    tags?: string[]
    historical?: { win_rate: number; samples: number }
    category?: string
  }
  selected?: boolean
}>()
defineEmits(['click'])

const patternColor = computed(() => {
  if (props.pattern.match_pct >= 80) return '#00ff88'
  if (props.pattern.match_pct >= 60) return '#00e5ff'
  return '#ffaa00'
})

const matchColor = computed(() => {
  if (props.pattern.match_pct >= 80) return '#00ff88'
  if (props.pattern.match_pct >= 60) return '#00e5ff'
  if (props.pattern.match_pct >= 40) return '#ffaa00'
  return '#ff3366'
})
</script>

<style scoped>
.pattern-card { cursor: pointer; padding: 14px; transition: all 0.2s; }
.pattern-card.selected { border-color: var(--accent); box-shadow: 0 0 12px rgba(0,229,255,0.2); }
.pattern-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.pattern-icon { font-size: 16px; }
.pattern-name { font-size: 14px; font-weight: 600; color: var(--text-primary); margin: 0; flex: 1; }
.pattern-match { font-size: 15px; font-weight: 700; }
.pattern-desc { font-size: 12px; color: var(--text-secondary); line-height: 1.5; margin: 0 0 10px; }
.pattern-tags { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 8px; }
.pattern-tag { font-size: 10px; padding: 2px 6px; border-radius: 8px; background: rgba(0,229,255,0.08); color: var(--text-muted); border: 1px solid rgba(0,229,255,0.15); }
.pattern-history { font-size: 11px; color: var(--text-muted); }
.history-label { margin-right: 4px; }
.history-value { color: var(--accent); }
</style>
