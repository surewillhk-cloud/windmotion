<template>
  <div class="embed-stage-view">
    <div v-if="!stage" class="stage-empty">No stage data</div>
    <div v-else class="stage-content">
      <h3 class="stage-title">{{ lang === 'zh' ? stage.name_zh : stage.name }}</h3>
      <div class="steps-list">
        <div v-for="(step, i) in stage.steps" :key="i" class="step-item" :class="{ active: i === activeStep }">
          <div class="step-agent">
            <span class="agent-icon">🤖</span>
            <span class="agent-name">{{ step.agent }}</span>
          </div>
          <div class="step-body">
            <span class="step-action">{{ step.action }}</span>
            <span class="step-output mono-number">{{ step.output }}</span>
            <span class="step-duration mono-number">{{ step.duration_s }}s</span>
          </div>
        </div>
      </div>
      <div class="stage-total">
        <span class="total-label">Total Duration:</span>
        <span class="total-value mono-number">{{ stage.total_duration_s }}s</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = defineProps<{
  stage?: any
  lang?: string
}>()

const activeStep = ref(-1)

function animateSteps() {
  if (!props.stage?.steps) return
  activeStep.value = -1
  props.stage.steps.forEach((_: any, i: number) => {
    setTimeout(() => { activeStep.value = i }, (i + 1) * 1500)
  })
}

onMounted(animateSteps)
watch(() => props.stage, animateSteps)
</script>

<style scoped>
.embed-stage-view { padding: 16px; }
.stage-empty { text-align: center; color: rgba(255,255,255,0.4); padding: 40px; }
.stage-title { font-size: 18px; color: #00e5ff; font-family: var(--font-mono); margin-bottom: 16px; }
.steps-list { display: flex; flex-direction: column; gap: 10px; }
.step-item { display: flex; gap: 14px; padding: 12px; border: 1px solid rgba(0,229,255,0.1); border-radius: 6px; transition: all 0.3s; opacity: 0.5; }
.step-item.active { opacity: 1; border-color: rgba(0,229,255,0.3); background: rgba(0,229,255,0.05); box-shadow: 0 0 12px rgba(0,229,255,0.1); }
.step-agent { display: flex; align-items: center; gap: 6px; min-width: 120px; }
.agent-icon { font-size: 16px; }
.agent-name { font-size: 12px; color: #e0e0e0; font-family: var(--font-mono); }
.step-body { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.step-action { font-size: 13px; color: rgba(255,255,255,0.7); }
.step-output { font-size: 12px; color: #00e5ff; }
.step-duration { font-size: 11px; color: rgba(255,255,255,0.4); }
.stage-total { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(0,229,255,0.1); }
.total-label { font-size: 12px; color: rgba(255,255,255,0.5); }
.total-value { font-size: 14px; color: #00e5ff; font-weight: 600; }
</style>
