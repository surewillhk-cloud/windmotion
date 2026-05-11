<template>
  <div class="probability-chart" ref="chartContainer">
    <div ref="chart" class="chart-area" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  data: Array<{ time: string; probability: number; std_dev?: number }>
}>()

const chartContainer = ref<HTMLElement>()
const chart = ref<HTMLElement>()
let echartsInstance: echarts.ECharts

function render() {
  if (!chart.value || !props.data?.length) return

  if (!echartsInstance) {
    echartsInstance = echarts.init(chart.value)
  }

  const upper = props.data.map(d => d.probability + (d.std_dev || 0))
  const lower = props.data.map(d => Math.max(0, d.probability - (d.std_dev || 0)))

  const option = {
    backgroundColor: 'transparent',
    grid: { top: 20, right: 20, bottom: 40, left: 60 },
    xAxis: {
      type: 'category',
      data: props.data.map(d => d.time),
      axisLine: { lineStyle: { color: 'rgba(0,229,255,0.2)' } },
      axisLabel: { color: '#8892a0', fontSize: 10, fontFamily: 'JetBrains Mono' }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLine: { lineStyle: { color: 'rgba(0,229,255,0.2)' } },
      axisLabel: { color: '#8892a0', fontSize: 10, fontFamily: 'JetBrains Mono' },
      splitLine: { lineStyle: { color: 'rgba(0,229,255,0.05)' } }
    },
    series: [
      {
        name: 'Upper',
        type: 'line',
        data: upper,
        lineStyle: { opacity: 0 },
        areaStyle: { color: 'rgba(0,229,255,0.05)' },
        stack: 'confidence',
        symbol: 'none'
      },
      {
        name: 'Lower',
        type: 'line',
        data: lower,
        lineStyle: { opacity: 0 },
        areaStyle: { color: 'rgba(0,229,255,0.05)' },
        stack: 'confidence',
        symbol: 'none'
      },
      {
        name: 'Probability',
        type: 'line',
        data: props.data.map(d => d.probability),
        smooth: true,
        lineStyle: { color: '#00e5ff', width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,229,255,0.15)' },
            { offset: 1, color: 'rgba(0,229,255,0)' }
          ])
        },
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: { color: '#00e5ff' }
      }
    ],
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#111827',
      borderColor: 'rgba(0,229,255,0.3)',
      textStyle: { color: '#e0e0e0', fontFamily: 'JetBrains Mono', fontSize: 12 }
    }
  }

  echartsInstance.setOption(option)
}

onMounted(() => {
  render()
  window.addEventListener('resize', () => echartsInstance?.resize())
})
watch(() => props.data, render, { deep: true })
</script>

<style scoped>
.probability-chart { width: 100%; }
.chart-area { width: 100%; height: 200px; }
</style>
