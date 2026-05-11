<template>
  <div class="analysis-process">
    <div class="process-header">
      <h1 class="page-title glow-text">{{ t('analysis.title') || 'Forward Analysis' }}</h1>
      <span class="target-addr mono-number">{{ address }}</span>
      <span v-if="wsConnected" class="ws-badge connected">● LIVE</span>
      <span v-else class="ws-badge">○ Connecting...</span>
    </div>

    <StepIndicator :steps="steps" :current="currentStep" />

    <div class="process-content">
      <!-- Step 1: Causal Graph -->
      <div v-show="currentStep === 0" class="step-content">
        <h2>Causal Graph Construction</h2>
        <div class="graph-area">
          <Neo4jGraph :graph-data="displayGraph" @nodeClick="onNodeClick" />
          <GraphLegend />
        </div>
        <div v-if="selectedNode" class="node-detail">
          <DecisionNodeDetail :node="selectedNode" />
        </div>
      </div>

      <!-- Step 2: Event Chain -->
      <div v-show="currentStep === 1" class="step-content">
        <h2>Event Chain Analysis</h2>
        <div class="events-list">
          <EventNode v-for="(evt, i) in events" :key="evt.id"
            :event="evt" :active="i === activeEvent" :completed="i < activeEvent"
            :probability="evt.probability" @click="activeEvent = i" />
        </div>
        <div v-if="events[activeEvent]" class="event-reasoning">
          <h3>Agent Reasoning for {{ events[activeEvent].id }}</h3>
          <AgentReasoning v-for="(r, i) in getReasoning(events[activeEvent].id)" :key="i"
            :agent="r.agent" :reasoning="r.reasoning" :probability="r.probability" />
        </div>
      </div>

      <!-- Step 3: Probability -->
      <div v-show="currentStep === 2" class="step-content">
        <h2>Probability Pricing</h2>
        <ProbabilityPanel :probability="finalProb" :std-dev="stdDev" :spread="maxSpread" />
        <div class="prob-chart">
          <ProbabilityChart :data="probTimeline" />
        </div>
      </div>

      <!-- Step 4: Deliberation -->
      <div v-show="currentStep === 3" class="step-content">
        <h2>Deliberation</h2>
        <DeliberationView
          :triggered="deliberation.triggered"
          :trigger-reason="deliberation.triggerReason"
          :rounds="deliberation.rounds"
          :ruling="deliberation.ruling"
          :final-probability="deliberation.finalProbability" />
      </div>

      <!-- Step 5: Report -->
      <div v-show="currentStep === 4" class="step-content">
        <h2>Report</h2>
        <div class="report-card glow-card">
          <div class="report-section">
            <h3>Conclusion</h3>
            <p>{{ report.conclusion }}</p>
          </div>
          <div class="report-section">
            <h3>Key Factors</h3>
            <div class="factors-list">
              <span v-for="f in report.keyFactors" :key="f" class="factor-tag">{{ f }}</span>
            </div>
          </div>
          <div class="report-meta">
            <div class="meta-item">
              <span class="meta-label">Confidence</span>
              <span class="meta-value">{{ report.confidence }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Duration</span>
              <span class="meta-value mono-number">{{ report.duration }}s</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Cost</span>
              <span class="meta-value mono-number">¥{{ report.cost }}</span>
            </div>
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { useGraphStore } from '@/stores/graph'
import { useAnalysisWS } from '@/services/ws'
import StepIndicator from '@/components/analysis/StepIndicator.vue'
import Neo4jGraph from '@/components/graph/Neo4jGraph.vue'
import GraphLegend from '@/components/graph/GraphLegend.vue'
import DecisionNodeDetail from '@/components/reverse/DecisionNodeDetail.vue'
import EventNode from '@/components/timeline/EventNode.vue'
import AgentReasoning from '@/components/analysis/AgentReasoning.vue'
import ProbabilityPanel from '@/components/analysis/ProbabilityPanel.vue'
import ProbabilityChart from '@/components/replay/ProbabilityChart.vue'
import DeliberationView from '@/components/analysis/DeliberationView.vue'
import GlowButton from '@/components/common/GlowButton.vue'

const { t } = useI18n()
const route = useRoute()
const analysisStore = useAnalysisStore()
const graphStore = useGraphStore()

const address = computed(() => (route.params.address || route.params.id) as string || '0x...')
const analysisId = computed(() => route.params.id as string || '')

// WebSocket for live progress
const { progress: wsProgress, status: wsStatus, graphUpdate, isConnected: wsConnected } = useAnalysisWS(analysisId.value)

const currentStep = ref(0)
const activeEvent = ref(0)
const selectedNode = ref<any>(null)

const steps = [
  { label: 'Causal Graph', key: 'graph' },
  { label: 'Event Chain', key: 'events' },
  { label: 'Probability', key: 'probability' },
  { label: 'Deliberation', key: 'deliberation' },
  { label: 'Report', key: 'report' }
]

// Use real graph data from store, fallback to defaults
const displayGraph = computed(() => {
  const g = graphStore.currentGraph
  if (g.nodes.length > 0) return g
  return {
    nodes: [
      { id: 'n1', label: 'Whale Entry', type: 'event' },
      { id: 'n2', label: 'Token Volume', type: 'factor' },
      { id: 'n3', label: 'Social Signal', type: 'variable' },
      { id: 'n4', label: 'Price Impact', type: 'result' },
      { id: 'n5', label: 'Exit Timing', type: 'decision' }
    ],
    edges: [
      { source: 'n1', target: 'n2', strength: 'strong', verified: true },
      { source: 'n2', target: 'n4', strength: 'medium', verified: true },
      { source: 'n3', target: 'n4', strength: 'weak', verified: false },
      { source: 'n1', target: 'n5', strength: 'medium', verified: true },
      { source: 'n5', target: 'n4', strength: 'strong', verified: false }
    ]
  }
})

const events = ref([
  { id: 'T1', description: 'Token listed on DEX', type: 'trade', probability: 45 },
  { id: 'T2', description: 'First whale accumulation', type: 'trade', probability: 55 },
  { id: 'T3', description: 'Target whale enters', type: 'trade', probability: 62 },
  { id: 'T4', description: 'Social buzz begins', type: 'social', probability: 74 }
])

const agentReasonings: Record<string, Array<{ agent: string; reasoning: string; probability: number }>> = {
  'T3': [
    { agent: 'Chain Analyst', reasoning: 'Smart sizing detected. 25% of portfolio allocated.', probability: 72 },
    { agent: 'Institutional', reasoning: 'Conservative entry. Testing the waters.', probability: 68 }
  ],
  'T4': [
    { agent: 'Social A', reasoning: 'Community growing fast. Strong momentum.', probability: 85 },
    { agent: 'Social B', reasoning: 'Hype without substance. Risky.', probability: 35 }
  ]
}

function getReasoning(eventId: string) {
  return agentReasonings[eventId] || []
}

const finalProb = ref(72.8)
const stdDev = ref(15.2)
const maxSpread = ref(50)

const probTimeline = ref([
  { time: 'T1', probability: 45, std_dev: 8 },
  { time: 'T2', probability: 55, std_dev: 10 },
  { time: 'T3', probability: 62, std_dev: 12 },
  { time: 'T4', probability: 74, std_dev: 18 }
])

const deliberation = ref({
  triggered: true,
  triggerReason: 'Max spread > 30% between Social A (85%) and Social B (35%)',
  rounds: [
    {
      round: 1,
      challenges: [
        { from: 'Chain Analyst', to: 'Social B', challenge: 'Ignores liquidity depth and growing holder count.' },
        { from: 'Social A', to: 'Social B', challenge: 'Market does not care about fundamentals in early cycles.' }
      ]
    },
    {
      round: 2,
      responses: [
        { agent: 'Social B', response: 'Fair point. Adjusting from 35% to 42%.' },
        { agent: 'Social A', response: 'Agree on long-term risk. Adjusting from 85% to 75%.' }
      ]
    }
  ],
  ruling: 'Liquidity path strengthened. Social hype acknowledged as short-term catalyst.',
  finalProbability: 72.8
})

const report = ref({
  conclusion: 'Strong early-stage characteristics with informed whale accumulation. Short-term catalyst: social momentum.',
  keyFactors: ['Early entry', 'Smart sizing', 'Social catalyst', 'Liquidity depth'],
  confidence: 'medium-high',
  duration: 423,
  cost: 3.2
})

function onNodeClick(node: any) {
  selectedNode.value = node
}

// Update data from WebSocket progress
function applyWSData(data: any) {
  if (!data) return
  if (data.step !== undefined) currentStep.value = data.step
  if (data.events) events.value = data.events
  if (data.probability) {
    finalProb.value = data.probability.final ?? finalProb.value
    stdDev.value = data.probability.std_dev ?? stdDev.value
    maxSpread.value = data.probability.spread ?? maxSpread.value
  }
  if (data.deliberation) deliberation.value = { ...deliberation.value, ...data.deliberation }
  if (data.report) report.value = { ...report.value, ...data.report }
}

// Watch for WS updates
watch(wsProgress, (val) => { if (val) applyWSData(val) })
watch(graphUpdate, (val) => { if (val) graphStore.applyGraphUpdate(val) })
watch(wsStatus, (val) => {
  if (val === 'completed') currentStep.value = 4
})

onMounted(async () => {
  // Fetch analysis data if ID exists
  if (analysisId.value) {
    try {
      const data = await analysisStore.fetchAnalysis(analysisId.value)
      if (data) {
        if (data.step !== undefined) currentStep.value = data.step
        if (data.graph) graphStore.updateGraph(data.graph)
        if (data.events) events.value = data.events
        if (data.report) report.value = { ...report.value, ...data.report }
      }
    } catch { /* use defaults */ }
  }
  // Connect graph store to live updates
  if (analysisId.value) {
    graphStore.connectLiveUpdates(analysisId.value)
  }
})

onUnmounted(() => {
  graphStore.disconnectLiveUpdates()
})
</script>

<style scoped>
.analysis-process { padding: 24px; max-width: 1200px; margin: 0 auto; }
.process-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; gap: 12px; }
.page-title { font-size: 24px; font-family: var(--font-mono); color: var(--accent); margin: 0; }
.target-addr { font-size: 14px; color: var(--text-muted); }
.ws-badge { font-size: 10px; color: var(--text-muted); }
.ws-badge.connected { color: #00ff88; }
.process-content { min-height: 400px; margin: 20px 0; }
.step-content h2 { font-size: 18px; color: var(--text-primary); margin-bottom: 16px; }
.graph-area { margin-bottom: 16px; }
.events-list { display: flex; flex-direction: column; gap: 4px; margin-bottom: 16px; }
.event-reasoning { padding: 16px; background: rgba(0,0,0,0.2); border-radius: 8px; }
.event-reasoning h3 { font-size: 14px; color: var(--text-secondary); margin-bottom: 12px; }
.prob-chart { margin-top: 16px; }
.report-card { padding: 20px; }
.report-section { margin-bottom: 16px; }
.report-section h3 { font-size: 14px; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 8px; }
.report-section p { font-size: 14px; color: var(--text-primary); line-height: 1.6; }
.factors-list { display: flex; gap: 6px; flex-wrap: wrap; }
.factor-tag { font-size: 11px; padding: 3px 10px; border-radius: 12px; background: rgba(0,229,255,0.1); color: var(--accent); border: 1px solid rgba(0,229,255,0.2); }
.report-meta { display: flex; gap: 24px; padding-top: 16px; border-top: 1px solid var(--border); }
.meta-item { display: flex; flex-direction: column; gap: 2px; }
.meta-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }
.meta-value { font-size: 14px; color: var(--text-primary); font-weight: 600; }
.process-nav { display: flex; justify-content: space-between; margin-top: 20px; }
</style>
