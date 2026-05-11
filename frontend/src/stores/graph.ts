import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface GraphNode {
  id: string
  label: string
  type: 'event' | 'decision' | 'outcome' | 'factor' | 'whale' | 'token'
  x: number
  y: number
  vx?: number
  vy?: number
  fx?: number | null
  fy?: number | null
  importance: number
  color?: string
  size?: number
  metadata?: Record<string, any>
}

export interface GraphEdge {
  id: string
  source: string | GraphNode
  target: string | GraphNode
  weight: number
  type: 'causal' | 'correlation' | 'temporal' | 'transfer'
  label?: string
  animated?: boolean
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export const useGraphStore = defineStore('graph', () => {
  const currentGraph = ref<GraphData>({
    nodes: [
      { id: 'n1', label: '大量买入 ETH', type: 'event', x: 0, y: 0, importance: 0.9 },
      { id: 'n2', label: 'Gas 费飙升', type: 'factor', x: 0, y: 0, importance: 0.6 },
      { id: 'n3', label: 'DEX 流动性变化', type: 'event', x: 0, y: 0, importance: 0.7 },
      { id: 'n4', label: '价格突破阻力位', type: 'outcome', x: 0, y: 0, importance: 0.85 },
      { id: 'n5', label: '止损触发', type: 'decision', x: 0, y: 0, importance: 0.5 },
      { id: 'n6', label: '获利了结', type: 'decision', x: 0, y: 0, importance: 0.75 },
      { id: 'n7', label: '后续买入', type: 'event', x: 0, y: 0, importance: 0.65 }
    ],
    edges: [
      { id: 'e1', source: 'n1', target: 'n3', weight: 0.8, type: 'causal', label: '引起', animated: true },
      { id: 'e2', source: 'n1', target: 'n2', weight: 0.6, type: 'correlation', label: '相关' },
      { id: 'e3', source: 'n3', target: 'n4', weight: 0.7, type: 'causal', label: '导致', animated: true },
      { id: 'e4', source: 'n4', target: 'n5', weight: 0.4, type: 'temporal', label: '之后' },
      { id: 'e5', source: 'n4', target: 'n6', weight: 0.9, type: 'causal', label: '触发', animated: true },
      { id: 'e6', source: 'n6', target: 'n7', weight: 0.5, type: 'temporal', label: '随后' }
    ]
  })

  const selectedNode = ref<GraphNode | null>(null)
  const hoveredNode = ref<GraphNode | null>(null)
  const graphLayout = ref<'force' | 'radial' | 'hierarchical'>('force')

  function selectNode(node: GraphNode | null) {
    selectedNode.value = node
  }

  function setHoveredNode(node: GraphNode | null) {
    hoveredNode.value = node
  }

  function updateGraph(data: GraphData) {
    currentGraph.value = data
  }

  function setLayout(layout: 'force' | 'radial' | 'hierarchical') {
    graphLayout.value = layout
  }

  return {
    currentGraph,
    selectedNode,
    hoveredNode,
    graphLayout,
    selectNode,
    setHoveredNode,
    updateGraph,
    setLayout
  }
})
