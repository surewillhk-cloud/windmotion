<template>
  <div class="embed-deliberation">
    <div v-if="!stage" class="delib-empty">No deliberation data</div>
    <div v-else class="delib-content">
      <h3 class="delib-title">{{ lang === 'zh' ? stage.name_zh : stage.name }}</h3>

      <div class="delib-status">
        <span v-if="stage.triggered" class="status-badge triggered">DELIBERATION TRIGGERED</span>
        <span v-else class="status-badge safe">NOT NEEDED</span>
        <span v-if="stage.trigger_reason" class="trigger-reason">{{ stage.trigger_reason }}</span>
      </div>

      <div v-if="stage.rounds?.length" class="rounds">
        <div v-for="(round, ri) in stage.rounds" :key="ri" class="round-block" :class="{ active: ri === activeRound }">
          <div class="round-header" @click="activeRound = ri">
            <span class="round-label">Round {{ round.round }}</span>
            <span class="round-toggle">{{ ri === activeRound ? '▼' : '▶' }}</span>
          </div>

          <div v-if="ri === activeRound" class="round-body">
            <div v-if="round.challenges?.length" class="challenges">
              <div v-for="(c, ci) in round.challenges" :key="ci" class="challenge-item">
                <div class="challenge-header">
                  <span class="c-from">{{ c.from }}</span>
                  <span class="c-arrow">→</span>
                  <span class="c-to">{{ c.to }}</span>
                </div>
                <p class="c-text">{{ c.challenge }}</p>
              </div>
            </div>

            <div v-if="round.responses?.length" class="responses">
              <div v-for="(r, ri2) in round.responses" :key="ri2" class="response-item">
                <span class="r-agent">{{ r.agent }}:</span>
                <p class="r-text">{{ r.response }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="stage.ruling" class="ruling-section">
        <h4>Ruling</h4>
        <p class="ruling-text">{{ stage.ruling }}</p>
        <div class="final-prob">
          <span class="final-label">Final Probability:</span>
          <span class="final-value mono-number" :style="{ color: '#00ff88' }">{{ stage.final_probability }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  stage?: any
  lang?: string
}>()

const activeRound = ref(0)
</script>

<style scoped>
.embed-deliberation { padding: 16px; }
.delib-empty { text-align: center; color: rgba(255,255,255,0.4); padding: 40px; }
.delib-title { font-size: 18px; color: #00e5ff; font-family: var(--font-mono); margin-bottom: 16px; }
.delib-status { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.status-badge { font-size: 10px; padding: 3px 10px; border-radius: 10px; font-family: var(--font-mono); font-weight: 600; }
.status-badge.triggered { background: rgba(255,170,0,0.15); color: #ffaa00; }
.status-badge.safe { background: rgba(0,255,136,0.1); color: #00ff88; }
.trigger-reason { font-size: 12px; color: rgba(255,255,255,0.5); }
.rounds { margin-bottom: 16px; }
.round-block { border: 1px solid rgba(0,229,255,0.1); border-radius: 6px; margin-bottom: 8px; overflow: hidden; }
.round-block.active { border-color: rgba(0,229,255,0.3); }
.round-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; cursor: pointer; background: rgba(0,229,255,0.03); }
.round-label { font-size: 13px; color: #e0e0e0; font-family: var(--font-mono); }
.round-toggle { font-size: 10px; color: rgba(255,255,255,0.4); }
.round-body { padding: 12px 14px; }
.challenge-item { padding: 8px; border-left: 2px solid #ffaa00; background: rgba(255,170,0,0.03); border-radius: 0 4px 4px 0; margin-bottom: 6px; }
.challenge-header { display: flex; gap: 6px; align-items: center; margin-bottom: 4px; font-size: 11px; font-family: var(--font-mono); }
.c-from { color: #ffaa00; }
.c-arrow { color: rgba(255,255,255,0.3); }
.c-to { color: rgba(255,255,255,0.6); }
.c-text { font-size: 12px; color: rgba(255,255,255,0.7); line-height: 1.5; margin: 0; }
.response-item { padding: 8px; border-left: 2px solid #00e5ff; background: rgba(0,229,255,0.03); border-radius: 0 4px 4px 0; margin-bottom: 6px; }
.r-agent { font-size: 11px; color: #00e5ff; font-family: var(--font-mono); display: block; margin-bottom: 3px; }
.r-text { font-size: 12px; color: rgba(255,255,255,0.7); line-height: 1.5; margin: 0; }
.ruling-section { padding: 14px; background: rgba(0,255,136,0.05); border: 1px solid rgba(0,255,136,0.2); border-radius: 6px; }
.ruling-section h4 { font-size: 12px; color: rgba(255,255,255,0.5); text-transform: uppercase; margin-bottom: 8px; }
.ruling-text { font-size: 13px; color: rgba(255,255,255,0.8); line-height: 1.5; margin: 0 0 10px; }
.final-prob { display: flex; align-items: center; gap: 8px; }
.final-label { font-size: 12px; color: rgba(255,255,255,0.5); }
.final-value { font-size: 22px; font-weight: 700; }
</style>
