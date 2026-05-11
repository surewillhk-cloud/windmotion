import { ref, onMounted, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'

export interface WebSocketOptions {
  url?: string
  autoConnect?: boolean
  reconnection?: boolean
  reconnectionAttempts?: number
  reconnectionDelay?: number
}

export function useWebSocket(options: WebSocketOptions = {}) {
  const {
    url = '/ws',
    autoConnect = true,
    reconnection = true,
    reconnectionAttempts = 5,
    reconnectionDelay = 3000
  } = options

  const socket = ref<Socket | null>(null)
  const isConnected = ref(false)
  const reconnectCount = ref(0)
  const lastError = ref<string | null>(null)

  const listeners = new Map<string, Set<Function>>()

  function connect() {
    if (socket.value?.connected) return

    socket.value = io(url, {
      autoConnect,
      reconnection,
      reconnectionAttempts,
      reconnectionDelay,
      transports: ['websocket', 'polling']
    })

    socket.value.on('connect', () => {
      isConnected.value = true
      reconnectCount.value = 0
      lastError.value = null
    })

    socket.value.on('disconnect', (reason: string) => {
      isConnected.value = false
      console.warn('WebSocket disconnected:', reason)
    })

    socket.value.on('connect_error', (error: Error) => {
      lastError.value = error.message
      reconnectCount.value++
    })

    // Re-register existing listeners
    listeners.forEach((callbacks, event) => {
      callbacks.forEach(cb => socket.value?.on(event, cb as any))
    })
  }

  function disconnect() {
    socket.value?.disconnect()
    socket.value = null
    isConnected.value = false
  }

  function on(event: string, callback: Function) {
    if (!listeners.has(event)) {
      listeners.set(event, new Set())
    }
    listeners.get(event)!.add(callback)
    socket.value?.on(event, callback as any)
  }

  function off(event: string, callback?: Function) {
    if (callback) {
      listeners.get(event)?.delete(callback)
      socket.value?.off(event, callback as any)
    } else {
      listeners.delete(event)
      socket.value?.off(event)
    }
  }

  function emit(event: string, data?: any) {
    socket.value?.emit(event, data)
  }

  onMounted(() => {
    if (autoConnect) connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    socket,
    isConnected,
    reconnectCount,
    lastError,
    connect,
    disconnect,
    on,
    off,
    emit
  }
}

// Singleton for global whale feed
let globalSocket: Socket | null = null

export function getGlobalSocket(): Socket {
  if (!globalSocket) {
    globalSocket = io('/ws', {
      autoConnect: true,
      reconnection: true,
      transports: ['websocket', 'polling']
    })
  }
  return globalSocket
}
