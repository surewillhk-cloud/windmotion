<template>
  <div ref="container" class="graph-container">
    <svg ref="svg" :width="width" :height="height">
      <g ref="graphGroup">
        <g class="edges">
          <line v-for="edge in edges" :key="edge.id"
            :x1="edge.x1" :y1="edge.y1" :x2="edge.x2" :y2="edge.y2"
            :class="['edge', { active: edge.active, verified: edge.verified }]"
            :stroke="edge.active ? '#00e5ff' : '#4a5568'"
            :stroke-width="edge.strength === 'strong' ? 3 : edge.strength === 'medium' ? 2 : 1"
            :stroke-dasharray="edge.verified ? 'none' : '5,5'"
          />
        </g>
        <g class="nodes">
          <g v-for="node in nodes" :key="node.id"
            :transform="`translate(${node.x}, ${node.y})`"
            class="node" :class="{ active: node.active }"
            @click="$emit('nodeClick', node)"
            @mousedown="startDrag($event, node)">
            <circle :r="node.size || 20" :fill="nodeColor(node.type)"
              :stroke="node.active ? '#00e5ff' : 'rgba(0,229,255,0.3)'"
              stroke-width="1.5"
              :filter="node.active ? 'url(#glow)' : ''" />
            <text dy="4" text-anchor="middle" fill="#e0e0e0" font-size="11"
              font-family="JetBrains Mono, monospace">
              {{ node.label?.substring(0, 6) }}
            </text>
          </g>
        </g>
      </g>
      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps<{ graphData: any }>()
defineEmits(['nodeClick'])

const container = ref<HTMLElement>()
const svg = ref<SVGSVGElement>()
const graphGroup = ref<SVGGElement>()
const width = ref(600)
const height = ref(400)

interface GraphNode { id: string; label: string; type: string; x: number; y: number; size: number; active: boolean; fx?: number; fy?: number }
interface GraphEdge { id: string; source: any; target: any; x1: number; y1: number; x2: number; y2: number; strength: string; active: boolean; verified: boolean }

const nodes = ref<GraphNode[]>([])
const edges = ref<GraphEdge[]>([])

let simulation: d3.Simulation<any, any>

function nodeColor(type: string): string {
  const colors: Record<string, string> = {
    factor: '#00e5ff', variable: '#ffffff', event: '#7c3aed',
    decision: '#ffaa00', result: '#00ff88'
  }
  return colors[type] || '#4a5568'
}

function startDrag(event: MouseEvent, node: GraphNode) {
  const onMove = (e: MouseEvent) => {
    node.fx = e.offsetX
    node.fy = e.offsetY
    node.x = e.offsetX
    node.y = e.offsetY
    updateEdges()
  }
  const onEnd = () => {
    node.fx = undefined
    node.fy = undefined
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onEnd)
  }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onEnd)
}

function updateEdges() {
  edges.value = edges.value.map(e => {
    const src = typeof e.source === 'object' ? e.source : nodes.value.find(n => n.id === e.source)
    const tgt = typeof e.target === 'object' ? e.target : nodes.value.find(n => n.id === e.target)
    return { ...e, x1: src?.x || 0, y1: src?.y || 0, x2: tgt?.x || 0, y2: tgt?.y || 0 }
  })
}

function initGraph() {
  if (!props.graphData || !container.value) return

  width.value = container.value.clientWidth || 600
  height.value = container.value.clientHeight || 400

  const g = props.graphData
  nodes.value = (g.nodes || []).map((n: any) => ({
    ...n, x: width.value / 2 + (Math.random() - 0.5) * 200,
    y: height.value / 2 + (Math.random() - 0.5) * 200,
    size: n.type === 'result' ? 25 : 20, active: false
  }))

  edges.value = (g.edges || []).map((e: any, i: number) => ({
    ...e, id: `e${i}`, x1: 0, y1: 0, x2: 0, y2: 0, active: false
  }))

  simulation = d3.forceSimulation(nodes.value)
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width.value / 2, height.value / 2))
    .force('link', d3.forceLink(edges.value).id((d: any) => d.id).distance(100))
    .on('tick', () => { updateEdges() })
}

watch(() => props.graphData, () => initGraph(), { deep: true })
onMounted(() => initGraph())
</script>

<style scoped>
.graph-container { width: 100%; height: 100%; min-height: 400px; background: rgba(0,0,0,0.2); border-radius: 8px; overflow: hidden; }
.node { cursor: pointer; }
.node:hover circle { filter: url(#glow); }
.edge.verified { opacity: 0.8; }
</style>
