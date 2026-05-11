<template>
  <div class="progress-glow">
    <div class="progress-track">
      <div class="progress-fill" :style="{ width: `${pct}%` }" />
    </div>
    <span class="progress-label mono-number">{{ pct.toFixed(0) }}%</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ pct: number }>()
</script>

<style scoped>
.progress-glow { display: flex; align-items: center; gap: 10px; }
.progress-track { flex: 1; height: 4px; background: rgba(0, 229, 255, 0.1); border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.5s ease; box-shadow: 0 0 8px rgba(0, 229, 255, 0.5); }
.progress-label { font-size: 12px; color: var(--accent); min-width: 40px; text-align: right; }
</style>
