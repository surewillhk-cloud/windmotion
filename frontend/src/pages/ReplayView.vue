<template>
  <div class="replay-view">
    <div class="replay-header">
      <h1 class="page-title glow-text">{{ t('replay.title') || 'Trade Replay' }}</h1>
      <span class="target-info mono-number">{{ token }} — {{ address }}</span>
    </div>

    <div class="replay-layout">
      <div class="chart-section">
        <PriceChart :data="priceData" :markers="tradeMarkers" />
        <div class="signal-overlay">
          <SignalLayer :signals="signals" />
        </div>
      </div>

      <div class="side-section">
        <div class="prob-curve glow-card">
          <h3>Probability Curve</h3>
          <ProbabilityChart :data="probData" />
        </div>

        <div class="narrative-section glow-card">
          <NarrativePanel :entries="narratives" :active-index="activeNarrative" title="Narrative" />
        </div>
      </div>
    </div>

    <div class="timeline-section">
      <TimelineSlider
        :progress="progress"
        :markers="timelineMarkers"
        :playing="playing"
        @togglePlay="playing = !playing"
        @prev="prevStep"
        @next="nextStep"
        @seek="seekTo"
        @speedChange="speed = $event" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import PriceChart from '@/components/replay/PriceChart.vue'
import ProbabilityChart from '@/components/replay/ProbabilityChart.vue'
import NarrativePanel from '@/components/replay/NarrativePanel.vue'
import SignalLayer from '@/components/replay/SignalLayer.vue'
import TimelineSlider from '@/components/timeline/TimelineSlider.vue'

const { t } = useI18n()
const route = useRoute()
const address = route.params.address as string || '0x...'
const token = route.query.token as string || 'TOKEN_X'

const playing = ref(false)
const speed = ref(1)
const activeStep = ref(0)
const activeNarrative = ref(0)

const priceData = ref([
  { time: 'Day 1', price: 0.0042 },
  { time: 'Day 3', price: 0.0055 },
  { time: 'Day 5', price: 0.0078 },
  { time: 'Day 8', price: 0.012 },
  { time: 'Day 10', price: 0.018 },
  { time: 'Day 12', price: 0.025 },
  { time: 'Day 15', price: 0.035 },
  { time: 'Day 18', price: 0.028 },
  { time: 'Day 20', price: 0.032 },
  { time: 'Day 23', price: 0.042 }
])

const tradeMarkers = ref([
  { time: 'Day 1', type: 'buy', label: 'Entry' },
  { time: 'Day 15', type: 'sell', label: 'Partial Exit' },
  { time: 'Day 23', type: 'sell', label: 'Final Exit' }
])

const signals = ref([
  { id: 's1', type: 'buy' as const, label: 'Whale Buy', value: '50 BNB', x: 10, y: 60, active: false },
  { id: 's2', type: 'whale' as const, label: 'Accumulation', value: '200 BNB', x: 30, y: 45, active: false },
  { id: 's3', type: 'alert' as const, label: 'Social Spike', x: 55, y: 30, active: false },
  { id: 's4', type: 'sell' as const, label: 'Exit Signal', value: '75%', x: 85, y: 25, active: false }
])

const probData = ref([
  { time: 'T1', probability: 45, std_dev: 8 },
  { time: 'T2', probability: 55, std_dev: 10 },
  { time: 'T3', probability: 62, std_dev: 12 },
  { time: 'T4', probability: 74, std_dev: 18 },
  { time: 'T5', probability: 78, std_dev: 15 },
  { time: 'T6', probability: 72, std_dev: 20 }
])

const narratives = ref([
  { time: 'Day 1', text: 'TOKEN_X listed on PancakeSwap. Initial liquidity: $500K.', type: 'event' as const },
  { time: 'Day 1', text: 'Target whale buys 50 BNB of TOKEN_X. First position.', type: 'buy' as const, highlight: true },
  { time: 'Day 5', text: 'Trading volume increases 340%. More wallets accumulating.', type: 'event' as const },
  { time: 'Day 8', text: 'Social media buzz begins. KOL mentions TOKEN_X.', type: 'event' as const },
  { time: 'Day 12', text: 'Whale adds another 150 BNB. Total position: 200 BNB.', type: 'buy' as const, highlight: true },
  { time: 'Day 15', text: 'Price hits local top. Whale sells 75% of position.', type: 'sell' as const, highlight: true },
  { time: 'Day 18', text: 'Price retraces 20%. Retail panic selling.', type: 'event' as const },
  { time: 'Day 23', text: 'Whale exits remaining position. Total profit: $450K.', type: 'sell' as const, highlight: true }
])

const timelineMarkers = computed(() => {
  return narratives.value.map((n, i) => ({
    id: String(i),
    pct: (i / (narratives.value.length - 1)) * 100,
    label: n.time,
    active: i === activeNarrative.value,
    completed: i < activeNarrative.value
  }))
})

const progress = computed(() => {
  return (activeNarrative.value / (narratives.value.length - 1)) * 100
})

function prevStep() {
  if (activeNarrative.value > 0) activeNarrative.value--
}

function nextStep() {
  if (activeNarrative.value < narratives.value.length - 1) activeNarrative.value++
}

function seekTo(markerId: string) {
  activeNarrative.value = parseInt(markerId)
}
</script>

<style scoped>
.replay-view { padding: 24px; max-width: 1400px; margin: 0 auto; }
.replay-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { font-size: 24px; font-family: var(--font-mono); color: var(--accent); margin: 0; }
.target-info { font-size: 13px; color: var(--text-muted); }
.replay-layout { display: grid; grid-template-columns: 1fr 380px; gap: 20px; margin-bottom: 20px; }
.chart-section { position: relative; }
.signal-overlay { position: absolute; inset: 0; pointer-events: none; }
.side-section { display: flex; flex-direction: column; gap: 16px; }
.prob-curve, .narrative-section { padding: 16px; }
.prob-curve h3, .narrative-section h3 { font-size: 14px; color: var(--text-secondary); margin-bottom: 12px; }
.timeline-section { padding: 16px; background: rgba(0,0,0,0.2); border-radius: 8px; }
</style>
