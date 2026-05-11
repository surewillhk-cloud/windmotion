<template>
  <div class="round-nav">
    <button v-for="r in total" :key="r"
      :class="['round-btn', { active: r === current, completed: r < current }]"
      @click="$emit('select', r)">
      <span class="round-num">{{ r }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  total: number
  current: number
}>()
defineEmits(['select'])
</script>

<style scoped>
.round-nav { display: flex; gap: 8px; justify-content: center; padding: 12px 0; }
.round-btn { width: 32px; height: 32px; border-radius: 50%; border: 2px solid var(--border); background: transparent; color: var(--text-muted); cursor: pointer; display: flex; align-items: center; justify-content: center; font-family: var(--font-mono); font-size: 13px; transition: all 0.2s; }
.round-btn:hover { border-color: var(--accent); color: var(--accent); }
.round-btn.active { border-color: var(--accent); color: var(--accent); background: rgba(0,229,255,0.15); box-shadow: 0 0 8px rgba(0,229,255,0.3); }
.round-btn.completed { border-color: var(--success); color: var(--success); background: rgba(0,255,136,0.1); }
.round-num { font-size: 13px; }
</style>
