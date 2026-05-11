<template>
  <g :transform="`translate(${x}, ${y})`" class="graph-node" :class="{ active, selected }"
    @click="$emit('click')">
    <circle :r="size" :fill="color" :stroke="active ? '#00e5ff' : 'rgba(0,229,255,0.3)'"
      stroke-width="1.5" :filter="active ? 'url(#glow)' : ''" />
    <text dy="4" text-anchor="middle" fill="#e0e0e0" font-size="10"
      font-family="JetBrains Mono, monospace">
      {{ truncatedLabel }}
    </text>
  </g>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  id: string
  label: string
  type: string
  x: number
  y: number
  size?: number
  active?: boolean
  selected?: boolean
}>()

defineEmits(['click'])

const truncatedLabel = computed(() => props.label?.substring(0, 6) || '')

const colorMap: Record<string, string> = {
  factor: '#00e5ff', variable: '#ffffff', event: '#7c3aed',
  decision: '#ffaa00', result: '#00ff88'
}
const color = computed(() => colorMap[props.type] || '#4a5568')
</script>

<style scoped>
.graph-node { cursor: pointer; transition: opacity 0.2s; }
.graph-node:hover circle { filter: url(#glow); }
</style>
