<template>
  <div class="round-timeline">
    <div class="timeline-header">
      <h3>{{ title || 'Round Timeline' }}</h3>
      <span class="round-count mono-number">{{ current }}/{{ total }}</span>
    </div>
    <div class="timeline-track">
      <div v-for="r in total" :key="r"
        :class="['round-marker', { active: r === current, completed: r < current }]"
        :style="{ left: `${((r - 1) / (total - 1)) * 100}%` }"
        @click="$emit('select', r)">
        <span class="marker-dot" />
        <span class="marker-label">R{{ r }}</span>
      </div>
      <div class="track-fill" :style="{ width: `${((current - 1) / (total - 1)) * 100}%` }" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  total: number
  current: number
  title?: string
}>()
defineEmits(['select'])
</script>

<style scoped>
.round-timeline { padding: 12px 0; }
.timeline-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.timeline-header h3 { font-size: 14px; color: var(--text-secondary); font-weight: 500; }
.round-count { font-size: 13px; color: var(--accent); }
.timeline-track { position: relative; height: 4px; background: rgba(0,229,255,0.1); border-radius: 2px; margin: 24px 0 16px; }
.track-fill { position: absolute; height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.3s ease; }
.round-marker { position: absolute; top: -8px; transform: translateX(-50%); cursor: pointer; text-align: center; }
.marker-dot { display: block; width: 10px; height: 10px; border-radius: 50%; border: 2px solid var(--border); margin: 0 auto 4px; background: var(--bg); }
.round-marker.active .marker-dot { border-color: var(--accent); background: var(--accent); box-shadow: 0 0 8px rgba(0,229,255,0.5); }
.round-marker.completed .marker-dot { border-color: var(--success); background: var(--success); }
.marker-label { font-size: 10px; color: var(--text-muted); font-family: var(--font-mono); }
.round-marker.active .marker-label { color: var(--accent); }
</style>
