import { ref, onMounted, onUnmounted } from 'vue'
import { WS_BASE } from './api'

// ── WSManager: Raw WebSocket connection manager ──
export class WSManager {
  private ws: WebSocket | null = null
  private handlers: Map<string, Set<Function>> = new Map()
  private path = ''
  private reconnectTimer: ReturnType<typeof setTimeout> | undefined
  private _connected = false

  get connected() { return this._connected }

  connect(path: string) {
    this.path = path
    const wsUrl = WS_BASE + path
    try {
      this.ws = new WebSocket(wsUrl)
    } catch {
      this.scheduleReconnect()
      return
    }

    this.ws.onopen = () => {
      this._connected = true
      this.emit('__connected', {})
    }

    this.ws.onmessage = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        this.emit(data.type || 'message', data)
      } catch {
        this.emit('message', { raw: e.data })
      }
    }

    this.ws.onclose = () => {
      this._connected = false
      this.emit('__disconnected', {})
      this.scheduleReconnect()
    }

    this.ws.onerror = () => {
      this._connected = false
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.reconnectTimer = setTimeout(() => this.connect(this.path), 3000)
  }

  on(event: string, handler: Function) {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set())
    this.handlers.get(event)!.add(handler)
  }

  off(event: string, handler?: Function) {
    if (handler) {
      this.handlers.get(event)?.delete(handler)
    } else {
      this.handlers.delete(event)
    }
  }

  emit(event: string, data: any) {
    this.handlers.get(event)?.forEach(fn => {
      try { fn(data) } catch (e) { console.error('WS handler error:', e) }
    })
  }

  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data))
    }
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
    this.ws = null
    this._connected = false
  }
}

// ── useAnalysisWS: Vue composable for analysis progress ──
export function useAnalysisWS(analysisId: string) {
  const progress = ref<any>(null)
  const status = ref<string>('connecting')
  const graphUpdate = ref<any>(null)
  const stageUpdate = ref<any>(null)
  const isConnected = ref(false)

  const manager = new WSManager()

  function connect() {
    manager.connect(`/ws/analysis/${analysisId}/progress`)

    manager.on('__connected', () => {
      isConnected.value = true
      status.value = 'connected'
    })

    manager.on('__disconnected', () => {
      isConnected.value = false
      status.value = 'disconnected'
    })

    manager.on('progress', (data: any) => {
      progress.value = data
    })

    manager.on('status', (data: any) => {
      status.value = data.status || data.state || 'unknown'
    })

    manager.on('graph_update', (data: any) => {
      graphUpdate.value = data
    })

    manager.on('stage_update', (data: any) => {
      stageUpdate.value = data
    })

    manager.on('completed', (data: any) => {
      status.value = 'completed'
      progress.value = data
    })

    manager.on('failed', (data: any) => {
      status.value = 'failed'
      progress.value = data
    })

    // Also handle generic messages
    manager.on('message', (data: any) => {
      if (data.progress) progress.value = data.progress
      if (data.status) status.value = data.status
      if (data.graph) graphUpdate.value = data.graph
      if (data.stage) stageUpdate.value = data.stage
    })
  }

  onMounted(connect)

  onUnmounted(() => {
    manager.disconnect()
  })

  return {
    progress,
    status,
    graphUpdate,
    stageUpdate,
    isConnected,
    send: (data: any) => manager.send(data),
    disconnect: () => manager.disconnect()
  }
}
