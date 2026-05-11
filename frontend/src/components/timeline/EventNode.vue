<template>
  <div class="event-node" :class="{ active, completed }" @click="$emit('click')">
    <div class="event-dot">
      <span class="dot-inner" />
    </div>
    <div class="event-content">
      <span class="event-id mono-number">{{ event.id }}</span>
      <span class="event-desc">{{ event.description }}</span>
      <span class="event-type" :class="event.type">{{ event.type }}</span>
    </div>
    <div v-if="probability" class="event-probability">
      <span class="prob-value mono-number">{{ probability }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  event: { id: string; description: string; type: string }
  active?: boolean
  completed?: boolean
  probability?: number
}>()
defineEmits(['click'])
</script>

<style scoped>
.event-node { display: flex; align-items: center; gap: 12px; padding: 10px 12px; cursor: pointer; border-radius: 6px; transition: background 0.2s; }
.event-node:hover { background: rgba(0,229,255,0.05); }
.event-node.active { background: rgba(0,229,255,0.08); }
.event-dot { width: 12px; height: 12px; border-radius: 50%; border: 2px solid var(--border); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.event-node.active .event-dot { border-color: var(--accent); }
.event-node.completed .event-dot { border-color: var(--success); background: var(--success); }
.dot-inner { width: 4px; height: 4px; border-radius: 50%; }
.event-node.active .dot-inner { background: var(--accent); }
.event-content { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.event-id { font-size: 11px; color: var(--text-muted); }
.event-desc { font-size: 13px; color: var(--text-primary); }
.event-type { font-size: 10px; padding: 1px 6px; border-radius: 3px; width: fit-content; }
.event-type.trade { background: rgba(0,229,255,0.15); color: #00e5ff; }
.event-type.social { background: rgba(124,58,237,0.15); color: #7c3aed; }
.event-probability { text-align: right; }
.prob-value { font-size: 14px; color: var(--accent); font-weight: 600; }
</style>
