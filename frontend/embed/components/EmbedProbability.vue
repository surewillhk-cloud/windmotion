<template>
  <div class="embed-probability">
    <div v-if="!stage" class="prob-empty">No probability data</div>
    <div v-else class="prob-content">
      <h3 class="prob-title">{{ lang === 'zh' ? stage.name_zh : stage.name }}</h3>
      <div class="prob-display">
        <div class="prob-ring" :style="{ borderColor: probColor }">
          <span class="prob-number mono-number" :style="{ color: probColor }">{{ stage.final_probability }}%</span>
        </div>
        <div class="prob-details">
          <div class="prob-detail-item">
            <span class="detail-label">Std Deviation</span>
            <span class="detail-value mono-number">±{{ stage.std_dev }}%</span>
          </div>
          <div class="prob-detail-item">
            <span class="detail-label">Max Spread</span>
            <span class="detail-value mono-number" :class="{ danger: stage.max_spread > 30 }">{{ stage.max_spread }}%</span>
          </div>
        </div>
      </div>
      <div class="prob-bar">
        <div class="bar-track">
          <div class="bar-fill" :style="{ width: `${stage.final_probability}%`, background: probGradient }" />
        </div>
        <div class="bar-labels">
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  stage?: any
  lang?: string
}>()

const probColor = computed(() => {
  const p = props.stage?.final_probability || 0
  if (p >= 70) return '#00ff88'
  if (p >= 50) return '#00e5ff'
  if (p >= 30) return '#ffaa00'
  return '#ff3366'
})

const probGradient = computed(() => {
  return `linear-gradient(90deg, rgba(0,229,255,0.8), ${probColor.value})`
})
</script>

<style scoped>
.embed-probability { padding: 16px; }
.prob-empty { text-align: center; color: rgba(255,255,255,0.4); padding: 40px; }
.prob-title { font-size: 18px; color: #00e5ff; font-family: var(--font-mono); margin-bottom: 24px; }
.prob-display { display: flex; align-items: center; gap: 32px; justify-content: center; margin-bottom: 24px; }
.prob-ring { width: 100px; height: 100px; border: 3px solid; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.prob-number { font-size: 28px; font-weight: 700; }
.prob-details { display: flex; flex-direction: column; gap: 12px; }
.prob-detail-item { display: flex; flex-direction: column; gap: 2px; }
.detail-label { font-size: 11px; color: rgba(255,255,255,0.4); text-transform: uppercase; }
.detail-value { font-size: 18px; font-weight: 600; color: #e0e0e0; }
.detail-value.danger { color: #ff3366; }
.prob-bar { max-width: 400px; margin: 0 auto; }
.bar-track { height: 6px; background: rgba(0,229,255,0.1); border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; transition: width 1s ease; }
.bar-labels { display: flex; justify-content: space-between; margin-top: 6px; }
.bar-labels span { font-size: 10px; color: rgba(255,255,255,0.3); font-family: var(--font-mono); }
</style>
