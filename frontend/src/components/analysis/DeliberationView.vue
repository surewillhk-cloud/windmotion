<template>
  <div class="deliberation-view">
    <div class="delib-header">
      <h3>Deliberation</h3>
      <span v-if="triggered" class="trigger-badge">TRIGGERED</span>
      <span v-else class="trigger-badge safe">NOT NEEDED</span>
    </div>

    <div v-if="triggerReason" class="trigger-reason">
      <span class="reason-label">Trigger:</span>
      <span class="reason-text">{{ triggerReason }}</span>
    </div>

    <div v-if="rounds?.length" class="rounds-container">
      <RoundNav :total="rounds.length" :current="activeRound" @select="activeRound = $event" />

      <div v-for="(round, i) in rounds" :key="i" v-show="i + 1 === activeRound" class="round-content">
        <div v-if="round.challenges?.length" class="challenges">
          <h4>Challenges</h4>
          <div v-for="(c, ci) in round.challenges" :key="ci" class="challenge-item">
            <div class="challenge-header">
              <span class="from">{{ c.from }}</span>
              <span class="arrow">→</span>
              <span class="to">{{ c.to }}</span>
            </div>
            <p class="challenge-text">{{ c.challenge }}</p>
          </div>
        </div>

        <div v-if="round.responses?.length" class="responses">
          <h4>Responses</h4>
          <div v-for="(r, ri) in round.responses" :key="ri" class="response-item">
            <span class="response-agent">{{ r.agent }}:</span>
            <p class="response-text">{{ r.response }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="ruling" class="ruling">
      <h4>Ruling</h4>
      <p class="ruling-text">{{ ruling }}</p>
      <div v-if="finalProbability" class="final-prob">
        <span class="final-label">Final Probability:</span>
        <span class="final-value mono-number">{{ finalProbability }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import RoundNav from '@/components/timeline/RoundNav.vue'

defineProps<{
  triggered?: boolean
  triggerReason?: string
  rounds?: Array<{
    round: number
    challenges?: Array<{ from: string; to: string; challenge: string }>
    responses?: Array<{ agent: string; response: string }>
  }>
  ruling?: string
  finalProbability?: number
}>()

const activeRound = ref(1)
</script>

<style scoped>
.deliberation-view { padding: 16px; }
.delib-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.delib-header h3 { font-size: 16px; color: var(--text-primary); font-weight: 600; }
.trigger-badge { font-size: 10px; padding: 2px 8px; border-radius: 10px; background: rgba(255,170,0,0.15); color: #ffaa00; font-family: var(--font-mono); font-weight: 600; }
.trigger-badge.safe { background: rgba(0,255,136,0.1); color: #00ff88; }
.trigger-reason { font-size: 12px; color: var(--text-muted); margin-bottom: 16px; padding: 8px 12px; background: rgba(0,0,0,0.2); border-radius: 4px; }
.reason-label { color: var(--text-muted); margin-right: 4px; }
.rounds-container { margin-bottom: 16px; }
.round-content { margin-top: 12px; }
.challenges h4, .responses h4, .ruling h4 { font-size: 12px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.challenge-item { padding: 8px 12px; border-left: 2px solid #ffaa00; background: rgba(255,170,0,0.03); border-radius: 0 4px 4px 0; margin-bottom: 8px; }
.challenge-header { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; font-size: 12px; font-family: var(--font-mono); }
.from { color: #ffaa00; }
.arrow { color: var(--text-muted); }
.to { color: var(--text-secondary); }
.challenge-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }
.response-item { padding: 8px 12px; border-left: 2px solid #00e5ff; background: rgba(0,229,255,0.03); border-radius: 0 4px 4px 0; margin-bottom: 8px; }
.response-agent { font-size: 12px; font-family: var(--font-mono); color: var(--accent); display: block; margin-bottom: 4px; }
.response-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin: 0; }
.ruling { padding: 12px; background: rgba(0,255,136,0.05); border: 1px solid rgba(0,255,136,0.2); border-radius: 6px; }
.ruling-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin: 0 0 8px; }
.final-prob { display: flex; align-items: center; gap: 8px; }
.final-label { font-size: 12px; color: var(--text-muted); }
.final-value { font-size: 20px; font-weight: 700; color: var(--accent); }
</style>
