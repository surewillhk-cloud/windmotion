<template>
  <button :class="['glow-btn', variant, { loading }]" :disabled="disabled || loading" @click="$emit('click')">
    <span v-if="loading" class="spinner">⟳</span>
    <slot />
  </button>
</template>

<script setup lang="ts">
defineProps<{
  variant?: 'default' | 'primary' | 'danger' | 'ghost'
  disabled?: boolean
  loading?: boolean
}>()
defineEmits(['click'])
</script>

<style scoped>
.spinner { animation: spin 1s linear infinite; margin-right: 6px; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
.ghost { border-color: transparent; background: transparent; }
.ghost:hover { background: rgba(0, 229, 255, 0.05); }
</style>
