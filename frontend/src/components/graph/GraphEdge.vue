<template>
  <line :x1="x1" :y1="y1" :x2="x2" :y2="y2"
    :class="['graph-edge', { active, verified }]"
    :stroke="active ? '#00e5ff' : '#4a5568'"
    :stroke-width="strokeWidth"
    :stroke-dasharray="verified ? 'none' : '5,5'" />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  x1: number
  y1: number
  x2: number
  y2: number
  strength?: 'weak' | 'medium' | 'strong'
  active?: boolean
  verified?: boolean
}>()

const strokeWidth = computed(() => {
  switch (props.strength) {
    case 'strong': return 3
    case 'medium': return 2
    default: return 1
  }
})
</script>

<style scoped>
.graph-edge { transition: stroke 0.2s, opacity 0.2s; }
.graph-edge.verified { opacity: 0.8; }
</style>
