<template>
  <div class="timeline-slider">
    <div class="timeline-track" ref="track" @click="seek">
      <div class="timeline-fill" :style="{ width: `${progress}%` }" />
      <div v-for="marker in markers" :key="marker.id"
        class="marker" :class="{ active: marker.active, completed: marker.completed }"
        :style="{ left: `${marker.pct}%` }"
        @click.stop="$emit('seek', marker.id)">
        <span class="marker-dot" />
        <span class="marker-label">{{ marker.label }}</span>
      </div>
      <div class="thumb" :style="{ left: `${progress}%` }" />
    </div>
    <div class="controls">
      <button @click="$emit('prev')" class="ctrl-btn">◄</button>
      <button @click="$emit('togglePlay')" class="ctrl-btn play">{{ playing ? '⏸' : '▶' }}</button>
      <button @click="$emit('next')" class="ctrl-btn">►</button>
      <select v-model="speed" class="speed-select glow-input" @change="$emit('speedChange', speed)">
        <option :value="1">1x</option>
        <option :value="2">2x</option>
        <option :value="5">5x</option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
defineProps<{
  progress: number
  markers: Array<{ id: string; pct: number; label: string; active: boolean; completed: boolean }>
  playing: boolean
}>()
defineEmits(['seek', 'prev', 'next', 'togglePlay', 'speedChange'])

const speed = ref(1)
const track = ref<HTMLElement>()

function seek(e: MouseEvent) {
  if (!track.value) return
  const pct = (e.offsetX / track.value.clientWidth) * 100
  // emit seek to pct
}
</script>

<style scoped>
.timeline-slider { padding: 12px 0; }
.timeline-track { position: relative; height: 4px; background: rgba(0,229,255,0.1); border-radius: 2px; cursor: pointer; margin: 20px 0 16px; }
.timeline-fill { position: absolute; height: 100%; background: var(--accent); border-radius: 2px; }
.thumb { position: absolute; top: -6px; width: 16px; height: 16px; background: var(--accent); border-radius: 50%; transform: translateX(-50%); box-shadow: 0 0 10px rgba(0,229,255,0.5); cursor: grab; }
.marker { position: absolute; top: -8px; transform: translateX(-50%); cursor: pointer; }
.marker-dot { display: block; width: 8px; height: 8px; border-radius: 50%; background: var(--text-muted); margin: 0 auto 4px; }
.marker.active .marker-dot { background: var(--accent); box-shadow: 0 0 6px rgba(0,229,255,0.5); }
.marker.completed .marker-dot { background: var(--success); }
.marker-label { font-size: 10px; color: var(--text-muted); white-space: nowrap; }
.controls { display: flex; align-items: center; gap: 8px; justify-content: center; }
.ctrl-btn { background: transparent; border: 1px solid var(--border); color: var(--accent); padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 14px; }
.ctrl-btn:hover { border-color: var(--accent); background: rgba(0,229,255,0.1); }
.speed-select { padding: 4px 8px; font-size: 12px; }
</style>
