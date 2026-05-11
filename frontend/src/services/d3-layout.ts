import * as d3 from 'd3'
import type { GraphNode, GraphEdge, GraphData } from '@/stores/graph'

export interface D3ForceLayoutOptions {
  width: number
  height: number
  chargeStrength?: number
  linkDistance?: number
  centerStrength?: number
  collisionRadius?: number
}

export function createForceLayout(data: GraphData, options: D3ForceLayoutOptions) {
  const {
    width,
    height,
    chargeStrength = -300,
    linkDistance = 120,
    centerStrength = 0.05,
    collisionRadius = 30
  } = options

  const nodes = data.nodes.map(n => ({ ...n }))
  const links = data.edges.map(e => ({
    ...e,
    source: typeof e.source === 'string' ? e.source : e.source.id,
    target: typeof e.target === 'string' ? e.target : e.target.id
  }))

  const simulation = d3.forceSimulation(nodes as any)
    .force('link', d3.forceLink(links as any).id((d: any) => d.id).distance(linkDistance))
    .force('charge', d3.forceManyBody().strength(chargeStrength))
    .force('center', d3.forceCenter(width / 2, height / 2).strength(centerStrength))
    .force('collision', d3.forceCollide().radius(collisionRadius))
    .force('x', d3.forceX(width / 2).strength(0.03))
    .force('y', d3.forceY(height / 2).strength(0.03))

  return { simulation, nodes, links }
}

export function getNodeColor(type: string): string {
  const colors: Record<string, string> = {
    event: '#00e5ff',
    decision: '#7c3aed',
    outcome: '#00ff88',
    factor: '#ffaa00',
    whale: '#ff3366',
    token: '#00e5ff'
  }
  return colors[type] || '#8892a0'
}

export function getNodeRadius(importance: number): number {
  return 8 + importance * 20
}

export function getEdgeColor(type: string): string {
  const colors: Record<string, string> = {
    causal: '#00e5ff',
    correlation: '#7c3aed',
    temporal: '#8892a0',
    transfer: '#ffaa00'
  }
  return colors[type] || '#4a5568'
}

export function getStrokeDasharray(type: string): string {
  switch (type) {
    case 'causal': return 'none'
    case 'correlation': return '5,5'
    case 'temporal': return '2,4'
    default: return 'none'
  }
}
