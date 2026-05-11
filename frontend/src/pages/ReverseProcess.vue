<template>
  <div class="reverse-process">
    <div class="process-header">
      <h1 class="page-title glow-text">{{ t('reverse.title') || 'Reverse Inference' }}</h1>
      <span class="target-addr mono-number">{{ address }}</span>
      <span v-if="wsConnected" class="ws-badge connected">● LIVE</span>
      <span v-else class="ws-badge">○ Connecting...</span>
    </div>

    <StepIndicator :steps="steps" :current="currentStep" />

    <div class="process-content">
      <!-- Step 1: Pattern Recognition -->
      <div v-show="currentStep === 0" class="step-content">
        <h2>Pattern Recognition</h2>
        <div class="patterns-grid">
          <PatternCard v-for="p in patterns" :key="p.name" :pattern="p"
            :selected="selectedPattern === p.name" @click="selectedPattern = p.name" />
        </div>
      </div>

      <!-- Step 2: Factor Analysis -->
      <div v-show="currentStep === 1" class="step-content">
        <h2>Factor Analysis</h2>
        <div class="factor-layout">
          <div class="radar-section">
            <FactorRadar :scores="factorScores" />
          </div>
          <div class="scores-section">
            <FactorScores :scores="factorScores" title="5-Factor Score" />
            <EnvironmentState :state="envState" />
          </div>
        </div>
      </div>

      <!-- Step 3: Decision Reconstruction -->
      <div v-show="currentStep === 2" class="step-content">
        <h2>Decision Reconstruction</h2>
        <RoundTimeline :total="3" :current="activeRound" @select="activeRound = $event" />
        <div class="round-detail">
          <div v-for="round in roundData" :key="round.round" v-show="round.round === activeRound">
            <DecisionNodeDetail v-for="node in round.nodes" :key="node.label" :node="node" style="margin-bottom: 12px;" />
          </div>
        </div>
      </div>

      <!-- Step 4: Deliberation -->
      <div v-show="currentStep === 3" class="step-content">
        <h2>Deliberation</h2>
        <DeliberationView
          :triggered="true"
          trigger-reason="Factor score spread > 2.0 between F1 (4.2) and F5 (1.8)"
          :rounds="delibRounds"
          ruling="Entry timing confirmed as strong. Behavior factor adjusted."
          :final-probability="68.5" />
      </div>

      <!-- Step 5: Conclusion -->
      <div v-show="currentStep === 4" class="step-content">
        <h2>Conclusion</h2>
        <div class="conclusion-card glow-card">
          <div class="conc-header">
            <span class="conc-verdict" :style="{ color: '#00ff88' }">{{ conclusion.verdict }}</span>
            <span class="conc-confidence mono-number">{{ conclusion.confidence }}% confidence</span>
          </div>
          <p class="conc-text">{{ conclusion.summary }}</p>
          <div class="conc-factors">
            <h3>Key Findings</h3>
            <ul>
              <li v-for="(finding, i) in conclusion.findings" :key="i">{{ finding }}</li>
            </ul>
          </div>
          <div class="conc-reco">
            <h3>Recommendation</h3>
            <p>{{ conclusion.recommendation }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="process-nav">
      <GlowButton :disabled="currentStep === 0" @click="currentStep--">Previous</GlowButton>
      <GlowButton variant="primary" :disabled="currentStep === steps.length - 1" @click="currentStep++">
        Next Step
      </GlowButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { useAnalysisWS } from '@/services/ws'
import StepIndicator from '@/components/analysis/StepIndicator.vue'
import PatternCard from '@/components/reverse/PatternCard.vue'
import FactorRadar from '@/components/reverse/FactorRadar.vue'
import FactorScores from '@/components/analysis/FactorScores.vue'
import EnvironmentState from '@/components/reverse/EnvironmentState.vue'
import RoundTimeline from '@/components/reverse/RoundTimeline.vue'
import DecisionNodeDetail from '@/components/reverse/DecisionNodeDetail.vue'
import DeliberationView from '@/components/analysis/DeliberationView.vue'
import GlowButton from '@/components/common/GlowButton.vue'

const { t } = useI18n()
const route = useRoute()
const analysisStore = useAnalysisStore()

const address = computed(() => (route.params.address || route.params.id) as string || '0x...')
const analysisId = computed(() => route.params.id as string || '')

// WebSocket for live progress
const { progress: wsProgress, status: wsStatus, isConnected: wsConnected } = useAnalysisWS(analysisId.value)

const currentStep = ref(0)
const selectedPattern = ref('')
const activeRound = ref(1)

const steps = [
  { label: 'Pattern', key: 'pattern' },
  { label: 'Factors', key: 'factors' },
  { label: 'Reconstruct', key: 'reconstruct' },
  { label: 'Deliberation', key: 'deliberation' },
  { label: 'Conclusion', key: 'conclusion' }
]

const patterns = ref([
  { name: 'Smart Money Accumulation', description: 'Gradual accumulation before major price move', match_pct: 82, tags: ['entry', 'timing', 'volume'], historical: { win_rate: 74, samples: 156 } },
  { name: 'Whale Exit Pattern', description: 'Staged exit near local top', match_pct: 65, tags: ['exit', 'profit-taking'], historical: { win_rate: 68, samples: 89 } },
  { name: 'DCA Strategy', description: 'Dollar-cost averaging over time', match_pct: 45, tags: ['consistency', 'risk-mgmt'], historical: { win_rate: 62, samples: 203 } }
])

const factorScores = ref<Record<string, number>>({ F1: 4.2, F2: 3.5, F3: 3.8, F4: 2.9, F5: 1.8 })

const envState = ref({
  market_trend: 'bullish',
  volatility: 'medium',
  liquidity: 'high',
  sentiment: 'positive',
  volume_24h: '$2.4M',
  holder_count: '12,450'
})

const roundData = ref([
  { round: 1, nodes: [
    { label: 'Entry Signal', type: 'event', description: 'Whale entered at $0.0042 during consolidation phase', weight: 4.2, confidence: 85 },
    { label: 'Volume Spike', type: 'factor', description: 'Trading volume increased 340% in 24h', weight: 3.8, confidence: 72 }
  ]},
  { round: 2, nodes: [
    { label: 'Position Build', type: 'decision', description: 'Accumulated 25% of portfolio over 3 days', weight: 3.5, confidence: 78 },
    { label: 'Social Timing', type: 'variable', description: 'Entered 48h before social buzz peaked', weight: 2.9, confidence: 65 }
  ]},
  { round: 3, nodes: [
    { label: 'Exit Plan', type: 'decision', description: 'Staged exit starting at 5x, finished at 8x', weight: 3.2, confidence: 70 },
    { label: 'Profit Realized', type: 'result', description: 'Total profit: $450K from $50K initial', weight: 4.0, confidence: 100 }
  ]}
])

const delibRounds = ref([
  { round: 1, challenges: [
    { from: 'Factor Analyst', to: 'Behavior Score', challenge: 'Low F5 score (1.8) contradicts high F1 (4.2). Inconsistent behavior.' }
  ]},
  { round: 2, responses: [
    { agent: 'Behavior Score', response: 'Low F5 is due to limited social data. On-chain behavior is strong. Adjusting to 2.5.' }
  ]}
])

const conclusion = ref({
  verdict: 'INFORMED TRADER',
  confidence: 72,
  summary: 'This whale demonstrates informed trading behavior with strong entry timing and position sizing. Pattern matches historical "smart money accumulation" with 82% similarity.',
  findings: [
    'Entry timing: Bought during low-volatility consolidation',
    'Position sizing: 25% of portfolio — aggressive but calculated',
    'Exit strategy: Staged exit near local top',
    'Social timing: Entered before social buzz peaked'
  ],
  recommendation: 'Follow this whale\'s next moves. Set alerts for their next large purchase.'
})

// Apply WebSocket data
function applyWSData(data: any) {
  if (!data) return
  if (data.step !== undefined) currentStep.value = data.step
  if (data.patterns) patterns.value = data.patterns
  if (data.factor_scores) factorScores.value = data.factor_scores
  if (data.environment) envState.value = { ...envState.value, ...data.environment }
  if (data.rounds) roundData.value = data.rounds
  if (data.deliberation) {
    if (data.deliberation.rounds) delibRounds.value = data.deliberation.rounds
  }
  if (data.conclusion) conclusion.value = { ...conclusion.value, ...data.conclusion }
}

watch(wsProgress, (val) => { if (val) applyWSData(val) })
watch(wsStatus, (val) => {
  if (val === 'completed') currentStep.value = 4
})

onMounted(async () => {
  // Try to fetch existing analysis data
  if (analysisId.value) {
    try {
      const data = await analysisStore.fetchAnalysis(analysisId.value)
      if (data) applyWSData(data)
    } catch { /* use defaults */ }
  }
})
</script>

<style scoped>
.reverse-process { padding: 24px; max-width: 1200px; margin: 0 auto; }
.process-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; gap: 12px; }
.page-title { font-size: 24px; font-family: var(--font-mono); color: var(--accent); margin: 0; }
.target-addr { font-size: 14px; color: var(--text-muted); }
.ws-badge { font-size: 10px; color: var(--text-muted); }
.ws-badge.connected { color: #00ff88; }
.process-content { min-height: 400px; margin: 20px 0; }
.step-content h2 { font-size: 18px; color: var(--text-primary); margin-bottom: 16px; }
.patterns-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }
.factor-layout { display: grid; grid-template-columns: 280px 1fr; gap: 24px; }
.round-detail { margin-top: 16px; }
.conclusion-card { padding: 24px; }
.conc-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.conc-verdict { font-size: 20px; font-weight: 700; font-family: var(--font-mono); }
.conc-confidence { font-size: 14px; color: var(--text-muted); }
.conc-text { font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 20px; }
.conc-factors h3, .conc-reco h3 { font-size: 13px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 8px; }
.conc-factors ul { padding-left: 20px; margin: 0 0 16px; }
.conc-factors li { font-size: 13px; color: var(--text-primary); line-height: 1.8; }
.conc-reco p { font-size: 14px; color: var(--accent); line-height: 1.5; }
.process-nav { display: flex; justify-content: space-between; margin-top: 20px; }
</style>
