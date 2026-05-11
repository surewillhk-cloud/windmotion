<template>
  <div class="wind-tunnel-embed" :class="{ playing: isPlaying }">
    <div class="embed-stage-header">
      <h2 class="case-title">{{ localizedTitle }}</h2>
      <span class="case-result mono-number">{{ caseData?.result }}</span>
    </div>

    <StepIndicator :steps="stageSteps" :current="currentStage" />

    <div class="stage-content">
      <EmbedStageView v-if="currentStage === 0" :stage="caseData?.stages?.[0]" :lang="lang" />
      <EmbedGraphView v-else-if="currentStage === 1" :stage="caseData?.stages?.[1]" :lang="lang" />
      <EmbedProbability v-else-if="currentStage === 2" :stage="caseData?.stages?.[2]" :lang="lang" />
      <EmbedDeliberation v-else-if="currentStage === 3" :stage="caseData?.stages?.[3]" :lang="lang" />
      <EmbedTimeline v-else-if="currentStage === 4" :stage="caseData?.stages?.[4]" :lang="lang" />
    </div>

    <EmbedControls
      :current="currentStage"
      :total="5"
      :playing="isPlaying"
      @prev="prevStage"
      @next="nextStage"
      @togglePlay="togglePlay"
      @restart="restart" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import StepIndicator from '@/components/analysis/StepIndicator.vue'
import EmbedStageView from './components/EmbedStageView.vue'
import EmbedGraphView from './components/EmbedGraphView.vue'
import EmbedProbability from './components/EmbedProbability.vue'
import EmbedDeliberation from './components/EmbedDeliberation.vue'
import EmbedTimeline from './components/EmbedTimeline.vue'
import EmbedControls from './components/EmbedControls.vue'

const props = defineProps<{
  caseData?: any
  lang?: string
  autoplay?: boolean
}>()

const emit = defineEmits(['complete'])

const currentStage = ref(0)
const isPlaying = ref(false)
let playTimer: ReturnType<typeof setTimeout> | null = null

const stageSteps = [
  { label: 'Graph Build', key: 'graph' },
  { label: 'Event Chain', key: 'events' },
  { label: 'Probability', key: 'probability' },
  { label: 'Deliberation', key: 'deliberation' },
  { label: 'Report', key: 'report' }
]

const localizedTitle = computed(() => {
  if (!props.caseData) return ''
  if (props.lang === 'zh' && props.caseData.title_zh) return props.caseData.title_zh
  return props.caseData.title
})

function nextStage() {
  if (currentStage.value < 4) {
    currentStage.value++
  } else {
    isPlaying.value = false
    emit('complete', props.caseData)
  }
}

function prevStage() {
  if (currentStage.value > 0) currentStage.value--
}

function togglePlay() {
  isPlaying.value = !isPlaying.value
  if (isPlaying.value) {
    autoAdvance()
  } else if (playTimer) {
    clearTimeout(playTimer)
    playTimer = null
  }
}

function autoAdvance() {
  if (!isPlaying.value) return
  const stage = props.caseData?.stages?.[currentStage.value]
  const duration = stage?.total_duration_s || 30
  playTimer = setTimeout(() => {
    nextStage()
    if (isPlaying.value) autoAdvance()
  }, Math.min(duration * 1000, 5000))
}

function restart() {
  currentStage.value = 0
  isPlaying.value = false
  if (playTimer) clearTimeout(playTimer)
}

function start() {
  restart()
  togglePlay()
}

defineExpose({ start })

onMounted(() => {
  if (props.autoplay) start()
})

onUnmounted(() => {
  if (playTimer) clearTimeout(playTimer)
})
</script>

<style scoped>
.wind-tunnel-embed { padding: 20px; max-width: 900px; margin: 0 auto; }
.embed-stage-header { text-align: center; margin-bottom: 16px; }
.case-title { font-size: 22px; font-family: var(--font-mono); color: #00e5ff; margin-bottom: 4px; }
.case-result { font-size: 14px; color: rgba(255,255,255,0.6); }
.stage-content { min-height: 300px; margin: 16px 0; }
</style>
