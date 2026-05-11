<template>
  <div class="embed-graph-view">
    <div v-if="!stage" class="graph-empty">No graph data</div>
    <div v-else class="graph-content">
      <h3 class="graph-title">{{ lang === 'zh' ? stage.name_zh : stage.name }}</h3>
      <div class="events-timeline">
        <div v-for="(evt, i) in stage.events" :key="evt.id"
          class="event-item" :class="{ active: i === activeEvent, [evt.type]: true }">
          <div class="event-marker">
            <span class="marker-dot" />
            <span v-if="i < stage.events.length - 1" class="marker-line" />
          </div>
          <div class="event-body">
            <span class="event-id mono-number">{{ evt.id }}</span>
            <span class="event-desc">{{ evt.description }}</span>
          </div>
        </div>
      </div>

      <div v-if="stage.agent_reasoning?.length" class="reasoning-section">
        <h4>Agent Reasoning</h4>
        <div v-for="(r, i) in stage.agent_reasoning" :key="i" class="reasoning-item">
          <div class="reasoning-header">
            <span class="r-agent">{{ r.agent }}</span>
            <span class="r-event mono-number">{{ r.event }}</span>
            <span class="r-prob mono-number" :style="{ color: probColor(r.probability) }">{{ r.probability }}%</span>
          </div>
          <p class="r-text">{{ r.reasoning }}</p>
        </div>
      </div>

      <div v-if="stage.probability_timeline?.length" class="prob-timeline">
        <h4>Probability Timeline</h4>
        <div class="prob-bars">
          <div v-for="pt in stage.probability_timeline" :key="pt.event" class="prob-bar-item">
            <span class="bar-label mono-number">{{ pt.event }}</span>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: `${pt.aggregate}%`, background: probColor(pt.aggregate) }" />
              <div class="bar-std" :style="{ left: `${Math.max(0, pt.aggregate - pt.std_dev)}%`, width: `${pt.std_dev * 2}%` }" />
            </div>
            <span class="bar-value mono-number" :style="{ color: probColor(pt.aggregate) }">{{ pt.aggregate }}%</span>
          </div>
        </div>
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

const activeEvent = ref(-1)

function animate() {
  if (!props.stage?.events) return
  activeEvent.value = -1
  props.stage.events.forEach((_: any, i: number) => {
    setTimeout(() => { activeEvent.value = i }, (i + 1) * 800)
  })
}

function probColor(p: number) {
  if (p >= 70) return '#00ff88'
  if (p >= 50) return '#00e5ff'
  if (p >= 30) return '#ffaa00'
  return '#ff3366'
}

onMounted(animate)
watch(() => props.stage, animate)
</script>

<style scoped>
.embed-graph-view { padding: 16px; }
.graph-empty { text-align: center; color: rgba(255,255,255,0.4); padding: 40px; }
.graph-title { font-size: 18px; color: #00e5ff; font-family: var(--font-mono); margin-bottom: 16px; }
.events-timeline { margin-bottom: 20px; }
.event-item { display: flex; gap: 12px; padding: 8px 0; transition: all 0.3s; opacity: 0.5; }
.event-item.active { opacity: 1; }
.event-marker { display: flex; flex-direction: column; align-items: center; }
.marker-dot { width: 10px; height: 10px; border-radius: 50%; border: 2px solid rgba(0,229,255,0.3); background: #050a14; }
.event-item.active .marker-dot { border-color: #00e5ff; background: #00e5ff; box-shadow: 0 0 8px rgba(0,229,255,0.5); }
.event-item.trade .marker-dot { border-color: #00e5ff; }
.event-item.social .marker-dot { border-color: #7c3aed; }
.event-item.active.trade .marker-dot { background: #00e5ff; }
.event-item.active.social .marker-dot { background: #7c3aed; }
.marker-line { width: 2px; flex: 1; background: rgba(0,229,255,0.1); min-height: 20px; }
.event-body { flex: 1; }
.event-id { font-size: 11px; color: rgba(255,255,255,0.4); display: block; }
.event-desc { font-size: 13px; color: #e0e0e0; }
.reasoning-section, .prob-timeline { margin-top: 16px; }
.reasoning-section h4, .prob-timeline h4 { font-size: 12px; color: rgba(255,255,255,0.5); text-transform: uppercase; margin-bottom: 10px; }
.reasoning-item { padding: 10px; border-left: 2px solid rgba(0,229,255,0.3); background: rgba(0,229,255,0.03); border-radius: 0 4px 4px 0; margin-bottom: 8px; }
.reasoning-header { display: flex; gap: 10px; align-items: center; margin-bottom: 6px; }
.r-agent { font-size: 12px; color: #00e5ff; font-family: var(--font-mono); }
.r-event { font-size: 11px; color: rgba(255,255,255,0.4); }
.r-prob { font-size: 14px; font-weight: 700; }
.r-text { font-size: 12px; color: rgba(255,255,255,0.7); line-height: 1.5; margin: 0; }
.prob-bars { display: flex; flex-direction: column; gap: 8px; }
.prob-bar-item { display: flex; align-items: center; gap: 8px; }
.bar-label { font-size: 12px; color: rgba(255,255,255,0.5); min-width: 30px; }
.bar-track { flex: 1; height: 8px; background: rgba(0,229,255,0.1); border-radius: 4px; position: relative; overflow: visible; }
.bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.bar-std { position: absolute; top: -2px; height: 12px; background: rgba(0,229,255,0.08); border-radius: 2px; }
.bar-value { font-size: 13px; font-weight: 600; min-width: 40px; text-align: right; }
</style>
