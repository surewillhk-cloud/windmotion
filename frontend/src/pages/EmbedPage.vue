<template>
  <div class="embed-page" :class="{ compact: isCompact }">
    <!-- Header -->
    <header class="embed-header" v-if="showHeader">
      <div class="header-left">
        <img v-if="brandLogo" :src="brandLogo" class="brand-logo" alt="logo" />
        <span class="brand-name">{{ brandName }}</span>
        <span class="live-badge">● LIVE INFERENCE</span>
      </div>
      <div class="header-right">
        <select v-model="currentLang" class="lang-select" @change="switchLang">
          <option value="zh-CN">简体中文</option>
          <option value="zh-TW">繁體中文</option>
          <option value="en">English</option>
          <option value="th">ภาษาไทย</option>
          <option value="ko">한국어</option>
          <option value="ja">日本語</option>
          <option value="vi">Tiếng Việt</option>
        </select>
      </div>
    </header>

    <!-- Step Indicator -->
    <div class="step-bar">
      <div v-for="(stage, i) in stages" :key="i"
        :class="['step-item', { active: i === currentStage, done: i < currentStage }]">
        <span class="dot" />
        <span class="label">{{ stageName(stage) }}</span>
        <div v-if="i < stages.length - 1" class="connector" :class="{ filled: i < currentStage }" />
      </div>
    </div>

    <!-- Case Info -->
    <div class="case-info" v-if="caseData">
      <span class="mono-number">{{ caseData.token }}</span>
      <span>·</span>
      <span>{{ caseData.result }}</span>
      <span>·</span>
      <span class="mono-number">{{ elapsed }}</span>
    </div>

    <!-- Main Body: Graph + Detail -->
    <div class="embed-body">
      <div class="graph-panel" ref="graphPanel">
        <svg :width="graphW" :height="graphH" class="graph-svg">
          <g v-for="(node, i) in graphNodes" :key="'n'+i"
            :transform="`translate(${node.x},${node.y})`"
            :class="['gnode', { active: node.active, done: node.done }]">
            <circle :r="node.r" :fill="nodeFill(node)" :stroke="node.active ? '#00e5ff' : 'rgba(0,229,255,0.2)'" stroke-width="1.5" />
            <text dy="4" text-anchor="middle" fill="#e0e0e0" font-size="10" font-family="JetBrains Mono,monospace">{{ node.label }}</text>
          </g>
          <line v-for="(edge, i) in graphEdges" :key="'e'+i"
            :x1="edge.x1" :y1="edge.y1" :x2="edge.x2" :y2="edge.y2"
            :stroke="edge.active ? '#00e5ff' : 'rgba(0,229,255,0.12)'"
            :stroke-width="edge.active ? 2 : 1"
            :stroke-dasharray="edge.done ? 'none' : '4,4'" />
        </svg>
      </div>

      <div class="detail-panel">
        <div v-for="(stage, si) in visibleStages" :key="si" class="stage-block">
          <h3 class="stage-title">Stage {{ stage.stage }}: {{ stageName(stage) }}</h3>

          <!-- Stage 1: Steps -->
          <template v-if="stage.steps">
            <div v-for="(step, j) in stage.steps" :key="j" class="step-row"
              :class="{ active: isStepActive(si, j), done: isStepDone(si, j) }">
              <span class="step-agent">{{ step.agent }}</span>
              <span class="step-action">{{ step.action }}</span>
              <span v-if="isStepDone(si, j)" class="step-output">{{ step.output }}</span>
              <span v-if="isStepDone(si, j)" class="step-dur mono-number">· {{ step.duration_s }}s</span>
            </div>
          </template>

          <!-- Stage 2: Events + Reasoning -->
          <template v-if="stage.events">
            <div v-for="(evt, j) in stage.events" :key="'ev'+j" class="event-row"
              :class="{ active: j === currentEvent }">
              <span class="evt-id mono-number">{{ evt.id }}</span>
              <span class="evt-desc">{{ evt.description }}</span>
            </div>
            <div v-for="(ar, j) in visibleReasoning" :key="'ar'+j" class="reasoning-row">
              <span class="ar-agent">{{ ar.agent }}:</span>
              <span class="ar-text">"{{ ar.reasoning }}"</span>
              <span class="ar-prob mono-number">{{ ar.probability }}%</span>
            </div>
            <div class="prob-bar" v-if="probTimeline.length">
              <div v-for="(p, j) in probTimeline" :key="j" class="prob-col" :class="{ active: j <= currentEvent }">
                <span class="prob-val mono-number">{{ p.aggregate }}%</span>
                <div class="prob-fill" :style="{ height: `${p.aggregate * 0.6}px` }" />
              </div>
            </div>
          </template>

          <!-- Stage 3: Probability -->
          <template v-if="stage.final_probability !== undefined && !stage.events">
            <div class="prob-summary">
              <span class="big-prob mono-number">{{ stage.final_probability }}%</span>
              <span class="prob-meta">σ={{ stage.std_dev }} · spread={{ stage.max_spread }}</span>
            </div>
          </template>

          <!-- Stage 4: Deliberation -->
          <template v-if="stage.rounds">
            <div class="trigger-reason">⚡ {{ stage.trigger_reason }}</div>
            <div v-for="(round, j) in stage.rounds" :key="j" class="round-block">
              <h4>Round {{ round.round }}</h4>
              <div v-if="round.challenges" v-for="(ch, k) in round.challenges" :key="k" class="challenge-row">
                <span class="ch-from">{{ ch.from }}</span> → <span class="ch-to">{{ ch.to }}:</span>
                <span class="ch-text">"{{ ch.challenge }}"</span>
              </div>
              <div v-if="round.responses" v-for="(r, k) in round.responses" :key="k" class="response-row">
                <span class="r-agent">{{ r.agent }}:</span>
                <span class="r-text">"{{ r.response }}"</span>
              </div>
            </div>
            <div class="ruling" v-if="stage.ruling">
              <strong>Ruling:</strong> {{ stage.ruling }}
              <span class="final-prob mono-number">{{ stage.final_probability }}%</span>
            </div>
          </template>

          <!-- Stage 5: Report -->
          <template v-if="stage.conclusion">
            <p class="conclusion-text">{{ stage.conclusion }}</p>
            <div class="key-factors">
              <span v-for="f in stage.key_factors" :key="f" class="factor-tag">{{ f }}</span>
            </div>
            <div class="meta-row mono-number">
              <span>⏱ {{ formatDuration(stage.total_duration_s) }}</span>
              <span>💰 ¥{{ stage.total_cost_cny }}</span>
            </div>
          </template>
        </div>

        <!-- Controls -->
        <div class="embed-controls">
          <button @click="prevStage" :disabled="currentStage === 0" class="ctrl-btn">◄</button>
          <button @click="toggleAuto" class="ctrl-btn play-btn">{{ autoPlaying ? '⏸' : '▶' }}</button>
          <button @click="nextStage" :disabled="currentStage >= stages.length - 1" class="ctrl-btn">►</button>
          <select v-model="playSpeed" class="speed-select">
            <option :value="1">1x</option>
            <option :value="2">2x</option>
            <option :value="5">5x</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer v-if="showFooter" class="embed-footer">
      <span>Want real-time inference?</span>
      <a :href="ctaUrl" class="cta-btn" target="_blank" rel="noopener">{{ ctaText }}</a>
      <span class="powered">Powered by {{ brandName }}</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

// ── URL Parameters ──
const params = new URLSearchParams(window.location.search)
const brandName = ref(params.get('brand') || 'Wind Motion')
const brandLogo = ref(params.get('logo') || '')
const ctaUrl = ref(params.get('cta_url') || 'https://windmotion.io')
const ctaText = ref(params.get('cta_text') || 'Contact Us')
const showFooter = ref(params.get('show_footer') !== 'false')
const showHeader = ref(true)
const isCompact = ref(params.get('compact') === 'true')
const currentLang = ref(params.get('lang') || navigator.language || 'zh-CN')
const playSpeed = ref(parseInt(params.get('speed') || '1', 10))
const autoPlaying = ref(params.get('autoplay') === 'true')

// ── State ──
const currentStage = ref(0)
const currentEvent = ref(-1)
const currentStep = ref(0)
const elapsed = ref('00:00')
const graphW = ref(400)
const graphH = ref(300)
const graphPanel = ref<HTMLElement>()
const caseData = ref<any>(null)
const stages = ref<any[]>([])
let autoTimer: ReturnType<typeof setTimeout> | undefined
let elapsedTimer: ReturnType<typeof setInterval> | undefined
let startTime = 0

// ── Stage name i18n ──
const stageI18n: Record<string, Record<string, string>> = {
  'zh-CN': { 'Causal Graph Build': '因果图谱构建', 'Event Chain Analysis': '事件链分析', 'Probability Pricing': '概率定价', 'Deliberation': '审议', 'Report Generation': '报告生成' },
  'zh-TW': { 'Causal Graph Build': '因果圖譜構建', 'Event Chain Analysis': '事件鏈分析', 'Probability Pricing': '概率定價', 'Deliberation': '審議', 'Report Generation': '報告生成' },
  'en': { 'Causal Graph Build': 'Causal Graph', 'Event Chain Analysis': 'Event Chain', 'Probability Pricing': 'Prob. Pricing', 'Deliberation': 'Deliberation', 'Report Generation': 'Report' },
  'th': { 'Causal Graph Build': 'สร้างกราฟ因果', 'Event Chain Analysis': 'ห่วงโซ่เหตุการณ์', 'Probability Pricing': 'กำหนดราคา', 'Deliberation': 'การพิจารณา', 'Report Generation': 'รายงาน' },
  'ko': { 'Causal Graph Build': '인과 그래프', 'Event Chain Analysis': '이벤트 체인', 'Probability Pricing': '확률 가격', 'Deliberation': '심의', 'Report Generation': '보고서' },
  'ja': { 'Causal Graph Build': '因果グラフ', 'Event Chain Analysis': 'イベント連鎖', 'Probability Pricing': '確率定价', 'Deliberation': '審議', 'Report Generation': 'レポート' },
  'vi': { 'Causal Graph Build': 'Xây dựng đồ thị', 'Event Chain Analysis': 'Chuỗi sự kiện', 'Probability Pricing': 'Định giá xác suất', 'Deliberation': 'Thảo luận', 'Report Generation': 'Báo cáo' },
}

function stageName(stage: any): string {
  const lang = currentLang.value
  const names = stageI18n[lang] || stageI18n['en'] || {}
  return names[stage.name] || stage.name_zh || stage.name
}

function formatDuration(s: number): string {
  return s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${s % 60}s`
}

function switchLang() { locale.value = currentLang.value }

// ── Graph ──
interface GNode { x: number; y: number; r: number; label: string; type: string; active: boolean; done: boolean }
interface GEdge { x1: number; y1: number; x2: number; y2: number; active: boolean; done: boolean }
const graphNodes = ref<GNode[]>([])
const graphEdges = ref<GEdge[]>([])

function nodeFill(n: GNode): string {
  if (n.active) return 'rgba(0,229,255,0.3)'
  if (n.done) return 'rgba(0,255,136,0.15)'
  return 'rgba(0,229,255,0.06)'
}

function buildGraph() {
  const cx = graphW.value / 2, cy = graphH.value / 2, count = 14, radius = 110
  const nodes: GNode[] = []
  const edges: GEdge[] = []
  for (let i = 0; i < count; i++) {
    const a = (Math.PI * 2 / count) * i - Math.PI / 2
    nodes.push({ x: cx + Math.cos(a) * radius, y: cy + Math.sin(a) * radius, r: 16, label: `N${i}`, type: i < 5 ? 'factor' : i < 9 ? 'variable' : 'event', active: false, done: false })
  }
  for (let i = 0; i < count; i++) { edges.push({ x1: nodes[i].x, y1: nodes[i].y, x2: nodes[(i + 1) % count].x, y2: nodes[(i + 1) % count].y, active: false, done: false }) }
  for (let i = 0; i < count; i += 2) { edges.push({ x1: nodes[i].x, y1: nodes[i].y, x2: nodes[(i + 4) % count].x, y2: nodes[(i + 4) % count].y, active: false, done: false }) }
  graphNodes.value = nodes; graphEdges.value = edges
}

// ── Derived ──
const visibleStages = computed(() => stages.value.slice(0, currentStage.value + 1))
const probTimeline = computed(() => stages.value.find((s: any) => s.probability_timeline)?.probability_timeline || [])
const visibleReasoning = computed(() => {
  const s = stages.value.find((s: any) => s.agent_reasoning)
  return s ? s.agent_reasoning.filter((_: any, i: number) => i <= currentEvent.value) : []
})

function isStepActive(si: number, j: number) { return si === currentStage.value && j === currentStep.value && currentStage.value === 0 }
function isStepDone(si: number, j: number) { return si < currentStage.value || (si === currentStage.value && j < currentStep.value) }

// ── Playback ──
function advance() {
  if (!autoPlaying.value) return
  const delay = 2000 / playSpeed.value
  if (currentStage.value === 0 && stages.value[0]?.steps) {
    if (currentStep.value < stages.value[0].steps.length) {
      const n = Math.min(currentStep.value * 4 + 4, graphNodes.value.length)
      for (let i = 0; i < n; i++) graphNodes.value[i].done = true
      currentStep.value++
      autoTimer = setTimeout(advance, delay); return
    }
  }
  if (currentStage.value === 1 && stages.value[1]?.events) {
    if (currentEvent.value < stages.value[1].events.length - 1) {
      currentEvent.value++
      const ei = currentEvent.value * 2
      if (ei < graphEdges.value.length) { graphEdges.value[ei].active = true; if (ei + 1 < graphEdges.value.length) graphEdges.value[ei + 1].active = true }
      autoTimer = setTimeout(advance, delay * 1.5); return
    }
  }
  if (currentStage.value < stages.value.length - 1) {
    currentStage.value++; currentStep.value = 0; currentEvent.value = -1
    graphNodes.value.forEach(n => { n.done = true; n.active = false })
    graphEdges.value.forEach(e => { e.done = e.active })
    autoTimer = setTimeout(advance, delay)
  } else { autoPlaying.value = false }
}

function toggleAuto() { autoPlaying.value = !autoPlaying.value; if (autoPlaying.value) advance() }
function nextStage() { if (currentStage.value < stages.value.length - 1) { currentStage.value++; currentStep.value = 0; currentEvent.value = -1 } }
function prevStage() { if (currentStage.value > 0) { currentStage.value--; currentStep.value = 0; currentEvent.value = -1 } }

// ── postMessage to parent ──
function postToParent(type: string, data: any) {
  if (window.parent !== window) {
    window.parent.postMessage({ type: 'windmotion', event: type, data }, '*')
  }
}

// ── Load case ──
async function loadCase() {
  const caseId = params.get('case') || 'token-x-10x'
  try {
    const resp = await fetch(`/api/embed/cases/${caseId}`)
    if (resp.ok) { caseData.value = await resp.json(); stages.value = caseData.value.stages || [] }
  } catch {
    try {
      const mod = await import(`../../embed/cases/${caseId}.json`)
      caseData.value = mod.default || mod; stages.value = caseData.value.stages || []
    } catch { loadBuiltin() }
  }
  buildGraph()
}

function loadBuiltin() {
  caseData.value = { token: 'TOKEN_X', result: '$50K → $500K · 23 days' }
  stages.value = [
    { stage: 1, name: 'Causal Graph Build', name_zh: '因果图谱构建', steps: [
      { agent: 'Referee', action: 'Generating draft...', output: '15 entities, 19 paths', duration_s: 40 },
      { agent: 'Reviewer A/B/C', action: 'Parallel review', output: '+3 paths, 1 fixed', duration_s: 15 },
      { agent: 'Referee', action: 'Merging', output: '32 nodes, 39 edges', duration_s: 15 }]},
    { stage: 2, name: 'Event Chain Analysis', name_zh: '事件链分析',
      events: [{ id: 'T1', description: 'TOKEN_X listed' }, { id: 'T2', description: 'First whale buy' }, { id: 'T3', description: 'Target whale enters' }, { id: 'T4', description: 'Social buzz' }, { id: 'T5', description: 'More whales' }, { id: 'T6', description: 'Retail FOMO' }],
      agent_reasoning: [{ event: 'T3', agent: 'Chain Analyst', reasoning: '50 BNB, 25% portfolio. Smart sizing.', probability: 72 }, { event: 'T3', agent: 'Institutional', reasoning: 'Testing waters.', probability: 68 }, { event: 'T4', agent: 'Social A', reasoning: 'Next 100x!', probability: 85 }, { event: 'T4', agent: 'Social B', reasoning: 'No product. P&D.', probability: 35 }],
      probability_timeline: [{ aggregate: 45 }, { aggregate: 55 }, { aggregate: 62 }, { aggregate: 74 }, { aggregate: 78 }, { aggregate: 72 }]},
    { stage: 3, name: 'Probability Pricing', name_zh: '概率定价', final_probability: 72.8, std_dev: 15.2, max_spread: 50 },
    { stage: 4, name: 'Deliberation', name_zh: '审议', trigger_reason: 'Spread > 30%', rounds: [
      { round: 1, challenges: [{ from: 'Chain Analyst', to: 'Social B', challenge: 'Ignores $500K liquidity.' }, { from: 'Institutional', to: 'Social A', challenge: 'No product = no long-term.' }]},
      { round: 2, responses: [{ agent: 'Social B', response: 'Adjusting to 42%.' }, { agent: 'Social A', response: 'Adjusting to 75%.' }]}],
      ruling: 'Liquidity path strengthened. Final: 72.8%', final_probability: 72.8 },
    { stage: 5, name: 'Report Generation', name_zh: '报告生成', conclusion: 'Strong early-stage. Smart whale. Risk: no product.', key_factors: ['Early entry', 'Smart sizing', 'Social catalyst', 'Liquidity'], total_duration_s: 423, total_cost_cny: 3.2 }
  ]
}

onMounted(() => {
  loadCase()
  if (autoPlaying.value) setTimeout(() => advance(), 1000)
  startTime = Date.now()
  elapsedTimer = setInterval(() => { const s = Math.floor((Date.now() - startTime) / 1000); elapsed.value = `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}` }, 1000)
  if (graphPanel.value) { graphW.value = graphPanel.value.clientWidth || 400; graphH.value = graphPanel.value.clientHeight || 300 }
  // ResizeObserver for responsive
  if (graphPanel.value && typeof ResizeObserver !== 'undefined') {
    const ro = new ResizeObserver(entries => { for (const e of entries) { graphW.value = e.contentRect.width; graphH.value = e.contentRect.height; buildGraph() } })
    ro.observe(graphPanel.value)
  }
  postToParent('ready', { brand: brandName.value })
})

onUnmounted(() => { clearTimeout(autoTimer); clearInterval(elapsedTimer) })
</script>

<style lang="scss" scoped>
.embed-page { min-height: 100vh; background: #0a0e17; color: #e0e0e0; font-family: 'Noto Sans SC', sans-serif; display: flex; flex-direction: column; padding: 16px; gap: 12px; }
.embed-page.compact { padding: 8px; gap: 8px; .stage-block { padding: 8px; } }
.embed-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 14px; background: #111827; border: 1px solid rgba(0,229,255,0.15); border-radius: 6px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-right { display: flex; align-items: center; gap: 8px; }
.brand-logo { height: 24px; border-radius: 4px; }
.brand-name { font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #00e5ff; font-weight: 600; letter-spacing: 1px; }
.live-badge { font-size: 10px; color: #00ff88; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
.lang-select { background: #0a0e17; border: 1px solid rgba(0,229,255,0.2); border-radius: 4px; color: #e0e0e0; padding: 4px 8px; font-size: 11px; }
.step-bar { display: flex; align-items: center; justify-content: center; gap: 0; padding: 8px 0; }
.step-item { display: flex; align-items: center; gap: 6px; padding: 4px 12px; font-size: 11px; color: #4a5568; position: relative; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #4a5568; }
.step-item.active { color: #00e5ff; .dot { background: #00e5ff; box-shadow: 0 0 8px rgba(0,229,255,0.5); } }
.step-item.done { color: #00ff88; .dot { background: #00ff88; } }
.connector { width: 30px; height: 2px; background: rgba(0,229,255,0.15); margin: 0 4px; }
.connector.filled { background: #00ff88; }
.case-info { text-align: center; font-size: 12px; color: #8892a0; font-family: 'JetBrains Mono', monospace; display: flex; gap: 8px; justify-content: center; }
.embed-body { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; flex: 1; min-height: 0; }
.graph-panel { background: rgba(0,0,0,0.2); border: 1px solid rgba(0,229,255,0.1); border-radius: 8px; overflow: hidden; min-height: 300px; }
.graph-svg { width: 100%; height: 100%; }
.gnode circle { transition: all 0.5s ease; }
.gnode.active circle { filter: drop-shadow(0 0 8px rgba(0,229,255,0.5)); }
.detail-panel { display: flex; flex-direction: column; gap: 12px; overflow-y: auto; max-height: 70vh; }
.stage-block { background: #111827; border: 1px solid rgba(0,229,255,0.15); border-radius: 8px; padding: 12px; }
.stage-title { font-size: 12px; font-family: 'JetBrains Mono', monospace; color: #00e5ff; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
.step-row { display: flex; align-items: baseline; gap: 8px; padding: 5px 0; font-size: 12px; border-bottom: 1px solid rgba(0,229,255,0.04); opacity: 0.4; transition: opacity 0.3s; }
.step-row.active, .step-row.done { opacity: 1; }
.step-agent { color: #00e5ff; font-weight: 600; min-width: 100px; }
.step-action { color: #8892a0; }
.step-output { color: #00ff88; }
.step-dur { color: #4a5568; font-size: 11px; }
.event-row { display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 12px; opacity: 0.4; transition: all 0.3s; }
.event-row.active { opacity: 1; background: rgba(0,229,255,0.04); border-radius: 4px; padding: 6px 8px; }
.evt-id { color: #7c3aed; font-size: 11px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.evt-desc { color: #8892a0; }
.reasoning-row { margin: 6px 0 6px 16px; padding: 8px; background: rgba(0,229,255,0.02); border-left: 2px solid rgba(0,229,255,0.15); border-radius: 0 4px 4px 0; font-size: 11px; }
.ar-agent { color: #00e5ff; font-weight: 600; }
.ar-text { color: #8892a0; font-style: italic; }
.ar-prob { color: #00e5ff; font-size: 12px; margin-left: 8px; font-family: 'JetBrains Mono', monospace; }
.prob-bar { display: flex; gap: 3px; align-items: flex-end; height: 50px; margin-top: 10px; }
.prob-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 2px; }
.prob-col.active .prob-fill { background: #00e5ff; box-shadow: 0 0 6px rgba(0,229,255,0.4); }
.prob-col.active .prob-val { color: #00e5ff; }
.prob-val { font-size: 8px; color: #4a5568; font-family: 'JetBrains Mono', monospace; }
.prob-fill { width: 100%; max-width: 24px; background: rgba(0,229,255,0.15); border-radius: 2px 2px 0 0; transition: all 0.3s; }
.prob-summary { text-align: center; padding: 16px; }
.big-prob { font-size: 36px; font-family: 'JetBrains Mono', monospace; color: #00e5ff; text-shadow: 0 0 20px rgba(0,229,255,0.4); }
.prob-meta { display: block; font-size: 11px; color: #4a5568; margin-top: 4px; }
.trigger-reason { font-size: 11px; color: #ffaa00; margin-bottom: 8px; }
.round-block { margin: 8px 0; }
.round-block h4 { font-size: 11px; color: #7c3aed; margin-bottom: 4px; text-transform: uppercase; }
.challenge-row, .response-row { font-size: 11px; padding: 3px 0; }
.ch-from { color: #00e5ff; font-weight: 600; }
.ch-to { color: #7c3aed; }
.ch-text, .r-text { color: #8892a0; font-style: italic; }
.r-agent { color: #00e5ff; font-weight: 600; }
.ruling { margin-top: 8px; padding: 8px; background: rgba(0,255,136,0.04); border: 1px solid rgba(0,255,136,0.15); border-radius: 4px; font-size: 12px; color: #00ff88; }
.final-prob { font-size: 14px; margin-left: 12px; font-family: 'JetBrains Mono', monospace; }
.conclusion-text { font-size: 12px; line-height: 1.6; color: #8892a0; }
.key-factors { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0; }
.factor-tag { font-size: 10px; padding: 3px 10px; border-radius: 10px; background: rgba(0,229,255,0.08); color: #00e5ff; border: 1px solid rgba(0,229,255,0.15); }
.meta-row { display: flex; gap: 16px; margin-top: 6px; color: #4a5568; font-size: 11px; }
.embed-controls { display: flex; gap: 8px; justify-content: center; padding: 8px 0; }
.ctrl-btn { background: transparent; border: 1px solid rgba(0,229,255,0.15); color: #00e5ff; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-size: 12px; transition: all 0.2s; }
.ctrl-btn:hover { background: rgba(0,229,255,0.08); border-color: #00e5ff; }
.ctrl-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.play-btn { font-size: 16px; padding: 6px 18px; }
.speed-select { background: #0a0e17; border: 1px solid rgba(0,229,255,0.15); color: #e0e0e0; padding: 4px 8px; border-radius: 4px; font-size: 11px; }
.embed-footer { display: flex; justify-content: center; align-items: center; gap: 16px; padding: 12px; background: #111827; border: 1px solid rgba(0,229,255,0.15); border-radius: 6px; font-size: 12px; color: #8892a0; }
.cta-btn { color: #00e5ff; text-decoration: none; padding: 4px 16px; border: 1px solid #00e5ff; border-radius: 4px; transition: all 0.2s; }
.cta-btn:hover { background: rgba(0,229,255,0.08); }
.powered { color: #4a5568; font-size: 10px; }
</style>
