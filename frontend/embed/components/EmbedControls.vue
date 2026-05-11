<template>
  <div class="embed-controls">
    <div class="controls-left">
      <span class="stage-indicator mono-number">{{ current + 1 }} / {{ total }}</span>
    </div>
    <div class="controls-center">
      <button class="ctrl-btn" @click="$emit('prev')" :disabled="current === 0">◄</button>
      <button class="ctrl-btn play" @click="$emit('togglePlay')">{{ playing ? '⏸' : '▶' }}</button>
      <button class="ctrl-btn" @click="$emit('next')" :disabled="current === total - 1">►</button>
    </div>
    <div class="controls-right">
      <button class="ctrl-btn restart" @click="$emit('restart')">↺</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  current: number
  total: number
  playing: boolean
}>()
defineEmits(['prev', 'next', 'togglePlay', 'restart'])
</script>

<style scoped>
.embed-controls { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; }
.controls-left, .controls-right { min-width: 80px; }
.controls-right { text-align: right; }
.stage-indicator { font-size: 13px; color: rgba(255,255,255,0.5); }
.controls-center { display: flex; gap: 8px; }
.ctrl-btn { background: transparent; border: 1px solid rgba(0,229,255,0.2); color: #00e5ff; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 14px; transition: all 0.2s; }
.ctrl-btn:hover:not(:disabled) { border-color: #00e5ff; background: rgba(0,229,255,0.1); box-shadow: 0 0 8px rgba(0,229,255,0.2); }
.ctrl-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.ctrl-btn.play { padding: 8px 20px; font-size: 16px; }
.ctrl-btn.restart { font-size: 16px; }
</style>
