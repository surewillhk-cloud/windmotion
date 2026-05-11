<template>
  <div class="graph-legend">
    <div v-for="item in items" :key="item.type" class="legend-item">
      <span class="legend-dot" :style="{ background: item.color }" />
      <span class="legend-label">{{ item.label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const items = [
  { type: 'factor', label: 'Factor', color: '#00e5ff' },
  { type: 'variable', label: 'Variable', color: '#ffffff' },
  { type: 'event', label: 'Event', color: '#7c3aed' },
  { type: 'decision', label: 'Decision', color: '#ffaa00' },
  { type: 'result', label: 'Result', color: '#00ff88' }
]
</script>

<style scoped>
.graph-legend { display: flex; gap: 16px; flex-wrap: wrap; padding: 8px 0; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }
.legend-label { font-size: 11px; color: var(--text-muted); }
</style>
