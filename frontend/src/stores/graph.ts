import { defineStore } from 'pinia'
import { ref } from 'vue'
import { WSManager } from '@/services/ws'

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
  const currentGraph = ref<GraphData>({ nodes: [], edges: [] })
  const selectedNode = ref<GraphNode | null>(null)
  const hoveredNode = ref<GraphNode | null>(null)
  const graphLayout = ref<'force' | 'radial' | 'hierarchical'>('force')
  const loading = ref(false)

  // WebSocket manager for live graph updates
  let wsManager: WSManager | null = null

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

  // Apply incremental graph updates from WebSocket
  function applyGraphUpdate(update: any) {
    if (!update) return
    if (update.nodes) {
      for (const node of update.nodes) {
        const existing = currentGraph.value.nodes.find(n => n.id === node.id)
        if (existing) {
          Object.assign(existing, node)
        } else {
          currentGraph.value.nodes.push(node)
        }
      }
    }
    if (update.edges) {
      for (const edge of update.edges) {
        const existing = currentGraph.value.edges.find(e => e.id === edge.id)
        if (existing) {
          Object.assign(existing, edge)
        } else {
          currentGraph.value.edges.push(edge)
        }
      }
    }
    if (update.remove_nodes) {
      const ids = new Set(update.remove_nodes)
      currentGraph.value.nodes = currentGraph.value.nodes.filter(n => !ids.has(n.id))
      currentGraph.value.edges = currentGraph.value.edges.filter(e => {
        const src = typeof e.source === 'string' ? e.source : e.source.id
        const tgt = typeof e.target === 'string' ? e.target : e.target.id
        return !ids.has(src) && !ids.has(tgt)
      })
    }
  }

  // Connect to live graph updates via WebSocket
  function connectLiveUpdates(analysisId: string) {
    disconnectLiveUpdates()
    wsManager = new WSManager()
    wsManager.connect(`/ws/analysis/${analysisId}/graph`)
    wsManager.on('graph_update', (data: any) => applyGraphUpdate(data))
    wsManager.on('message', (data: any) => {
      if (data.graph) updateGraph(data.graph)
      if (data.update) applyGraphUpdate(data.update)
    })
  }

  function disconnectLiveUpdates() {
    wsManager?.disconnect()
    wsManager = null
  }

  return {
    currentGraph, selectedNode, hoveredNode, graphLayout, loading,
    selectNode, setHoveredNode, updateGraph, setLayout,
    applyGraphUpdate, connectLiveUpdates, disconnectLiveUpdates
  }
})
