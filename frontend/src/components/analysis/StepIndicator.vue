<template>
  <div class="step-indicator">
    <div v-for="(step, i) in steps" :key="i"
      :class="['step', { active: i === current, completed: i < current, pending: i > current }]">
      <div class="step-dot">{{ i + 1 }}</div>
      <span class="step-label">{{ step.label }}</span>
      <div v-if="i < steps.length - 1" class="step-line" :class="{ filled: i < current }" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  steps: Array<{ label: string; key: string }>
  current: number
}>()
</script>

<style scoped>
.step-indicator { display: flex; align-items: center; padding: 16px 0; }
.step { display: flex; align-items: center; gap: 8px; }
.step-dot { width: 28px; height: 28px; border-radius: 50%; border: 2px solid var(--border); display: flex; align-items: center; justify-content: center; font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); }
.step.active .step-dot { border-color: var(--accent); color: var(--accent); background: rgba(0,229,255,0.15); box-shadow: 0 0 10px rgba(0,229,255,0.4); }
.step.completed .step-dot { border-color: var(--success); color: var(--success); background: rgba(0,255,136,0.15); }
.step-label { font-size: 12px; color: var(--text-muted); }
.step.active .step-label { color: var(--accent); }
.step.completed .step-label { color: var(--success); }
.step-line { width: 40px; height: 2px; background: var(--border); }
.step-line.filled { background: var(--success); }
</style>
