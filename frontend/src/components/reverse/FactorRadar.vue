<template>
  <div class="factor-radar">
    <canvas ref="canvas" :width="size" :height="size" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = defineProps<{
  scores: Record<string, number>
  size?: number
}>()

const canvas = ref<HTMLCanvasElement>()
const size = props.size || 250

function draw() {
  if (!canvas.value) return
  const ctx = canvas.value.getContext('2d')
  if (!ctx) return

  const cx = size / 2
  const cy = size / 2
  const maxR = size / 2 - 30
  const factors = ['F1', 'F2', 'F3', 'F4', 'F5']
  const labels = ['Entry', 'Exit', 'Position', 'Selection', 'Behavior']
  const angle = (Math.PI * 2) / 5

  ctx.clearRect(0, 0, size, size)

  for (let r = 1; r <= 5; r++) {
    const radius = (r / 5) * maxR
    ctx.beginPath()
    for (let i = 0; i <= 5; i++) {
      const a = angle * i - Math.PI / 2
      const x = cx + Math.cos(a) * radius
      const y = cy + Math.sin(a) * radius
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.1)'
    ctx.stroke()
  }

  for (let i = 0; i < 5; i++) {
    const a = angle * i - Math.PI / 2
    ctx.beginPath()
    ctx.moveTo(cx, cy)
    ctx.lineTo(cx + Math.cos(a) * maxR, cy + Math.sin(a) * maxR)
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.2)'
    ctx.stroke()

    const lx = cx + Math.cos(a) * (maxR + 15)
    const ly = cy + Math.sin(a) * (maxR + 15)
    ctx.fillStyle = '#8892a0'
    ctx.font = '11px JetBrains Mono'
    ctx.textAlign = 'center'
    ctx.fillText(labels[i], lx, ly)
  }

  ctx.beginPath()
  for (let i = 0; i <= 5; i++) {
    const idx = i % 5
    const val = (scores[factors[idx]] || 0) / 5
    const a = angle * idx - Math.PI / 2
    const x = cx + Math.cos(a) * maxR * val
    const y = cy + Math.sin(a) * maxR * val
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
  }
  ctx.fillStyle = 'rgba(0, 229, 255, 0.15)'
  ctx.fill()
  ctx.strokeStyle = '#00e5ff'
  ctx.lineWidth = 2
  ctx.stroke()

  for (let i = 0; i < 5; i++) {
    const val = (scores[factors[i]] || 0) / 5
    const a = angle * i - Math.PI / 2
    const x = cx + Math.cos(a) * maxR * val
    const y = cy + Math.sin(a) * maxR * val
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fillStyle = '#00e5ff'
    ctx.fill()
    ctx.strokeStyle = '#00e5ff'
    ctx.lineWidth = 1
    ctx.stroke()
  }
}

onMounted(draw)
watch(() => props.scores, draw, { deep: true })
</script>

<style scoped>
.factor-radar { display: flex; justify-content: center; }
canvas { filter: drop-shadow(0 0 4px rgba(0,229,255,0.3)); }
</style>
