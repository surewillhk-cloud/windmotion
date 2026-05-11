<template>
  <div class="agent-reasoning">
    <div class="agent-header">
      <span class="agent-name" :style="{ color: agentColor }">{{ agent }}</span>
      <span class="agent-prob mono-number" :style="{ color: agentColor }">{{ probability }}%</span>
    </div>
    <div class="reasoning-text">{{ reasoning }}</div>
    <div v-if="event" class="reasoning-event">
      <span class="event-label">Event:</span>
      <span class="event-id mono-number">{{ event }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  agent: string
  reasoning: string
  probability: number
  event?: string
}>()

const agentColor = computed(() => {
  if (props.probability >= 70) return '#00ff88'
  if (props.probability >= 50) return '#00e5ff'
  if (props.probability >= 30) return '#ffaa00'
  return '#ff3366'
})
</script>

<style scoped>
.agent-reasoning { padding: 12px; border-left: 3px solid var(--accent); background: rgba(0,229,255,0.03); border-radius: 0 6px 6px 0; margin-bottom: 10px; }
.agent-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.agent-name { font-size: 13px; font-weight: 600; font-family: var(--font-mono); }
.agent-prob { font-size: 16px; font-weight: 700; }
.reasoning-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 8px; }
.reasoning-event { font-size: 11px; color: var(--text-muted); }
.event-label { margin-right: 4px; }
.event-id { color: var(--accent); }
</style>
