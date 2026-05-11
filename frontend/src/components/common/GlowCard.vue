<template>
  <div :class="['glow-card', { interactive }]" @click="interactive && $emit('click')">
    <div v-if="$slots.header" class="card-header">
      <slot name="header" />
    </div>
    <div class="card-body">
      <slot />
    </div>
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ interactive?: boolean }>()
defineEmits(['click'])
</script>

<style scoped>
.glow-card.interactive { cursor: pointer; }
.glow-card.interactive:hover { border-color: rgba(0, 229, 255, 0.3); box-shadow: 0 0 16px rgba(0, 229, 255, 0.3); }
.card-header { padding-bottom: 12px; border-bottom: 1px solid var(--border); margin-bottom: 12px; }
.card-footer { padding-top: 12px; border-top: 1px solid var(--border); margin-top: 12px; }
</style>
