<template>
  <div class="embed-timeline">
    <div v-if="!stage" class="timeline-empty">No timeline data</div>
    <div v-else class="timeline-content">
      <h3 class="timeline-title">{{ lang === 'zh' ? stage.name_zh : stage.name }}</h3>
      <div class="timeline-summary">
        <p class="summary-text">{{ stage.conclusion }}</p>
      </div>
      <div class="timeline-meta">
        <div class="meta-item">
          <span class="meta-label">Confidence</span>
          <span class="meta-value" :style="{ color: '#00ff88' }">{{ stage.confidence }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Duration</span>
          <span class="meta-value mono-number">{{ stage.total_duration_s }}s</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Cost</span>
          <span class="meta-value mono-number">¥{{ stage.total_cost_cny }}</span>
        </div>
      </div>
      <div v-if="stage.key_factors?.length" class="key-factors">
        <h4>Key Factors</h4>
        <div class="factors-list">
          <span v-for="f in stage.key_factors" :key="f" class="factor-tag">{{ f }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  stage?: any
  lang?: string
}>()
</script>

<style scoped>
.embed-timeline { padding: 16px; }
.timeline-empty { text-align: center; color: rgba(255,255,255,0.4); padding: 40px; }
.timeline-title { font-size: 18px; color: #00e5ff; font-family: var(--font-mono); margin-bottom: 16px; }
.timeline-summary { padding: 16px; background: rgba(0,229,255,0.03); border: 1px solid rgba(0,229,255,0.1); border-radius: 6px; margin-bottom: 16px; }
.summary-text { font-size: 14px; color: rgba(255,255,255,0.8); line-height: 1.6; margin: 0; }
.timeline-meta { display: flex; gap: 24px; margin-bottom: 16px; }
.meta-item { display: flex; flex-direction: column; gap: 2px; }
.meta-label { font-size: 10px; color: rgba(255,255,255,0.4); text-transform: uppercase; }
.meta-value { font-size: 16px; font-weight: 600; color: #e0e0e0; }
.key-factors h4 { font-size: 12px; color: rgba(255,255,255,0.5); text-transform: uppercase; margin-bottom: 8px; }
.factors-list { display: flex; gap: 6px; flex-wrap: wrap; }
.factor-tag { font-size: 11px; padding: 3px 10px; border-radius: 12px; background: rgba(0,229,255,0.1); color: #00e5ff; border: 1px solid rgba(0,229,255,0.2); }
</style>
