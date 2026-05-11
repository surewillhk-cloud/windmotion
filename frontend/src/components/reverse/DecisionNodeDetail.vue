<template>
  <div class="decision-node-detail">
    <div class="node-header">
      <span class="node-icon" :style="{ color: nodeColor }">◆</span>
      <h3 class="node-label">{{ node.label }}</h3>
      <span class="node-type" :class="node.type">{{ node.type }}</span>
    </div>
    <div class="node-body">
      <div v-if="node.description" class="node-desc">{{ node.description }}</div>
      <div class="node-meta">
        <div v-if="node.weight" class="meta-item">
          <span class="meta-label">Weight</span>
          <span class="meta-value mono-number">{{ node.weight }}</span>
        </div>
        <div v-if="node.confidence" class="meta-item">
          <span class="meta-label">Confidence</span>
          <span class="meta-value mono-number">{{ node.confidence }}%</span>
        </div>
        <div v-if="node.connections" class="meta-item">
          <span class="meta-label">Connections</span>
          <span class="meta-value mono-number">{{ node.connections }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  node: {
    label: string
    type: string
    description?: string
    weight?: number
    confidence?: number
    connections?: number
  }
}>()

const nodeColor = computed(() => {
  const colors: Record<string, string> = {
    factor: '#00e5ff', variable: '#ffffff', event: '#7c3aed',
    decision: '#ffaa00', result: '#00ff88'
  }
  return colors[props.node.type] || '#4a5568'
})
</script>

<style scoped>
.decision-node-detail { padding: 16px; background: rgba(0,0,0,0.2); border-radius: 8px; border: 1px solid var(--border); }
.node-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.node-icon { font-size: 18px; }
.node-label { font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0; }
.node-type { font-size: 10px; padding: 2px 8px; border-radius: 10px; font-family: var(--font-mono); }
.node-type.factor { background: rgba(0,229,255,0.15); color: #00e5ff; }
.node-type.event { background: rgba(124,58,237,0.15); color: #7c3aed; }
.node-type.decision { background: rgba(255,170,0,0.15); color: #ffaa00; }
.node-type.result { background: rgba(0,255,136,0.15); color: #00ff88; }
.node-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin-bottom: 12px; }
.node-meta { display: flex; gap: 16px; }
.meta-item { display: flex; flex-direction: column; gap: 2px; }
.meta-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }
.meta-value { font-size: 14px; color: var(--accent); font-weight: 600; }
</style>
