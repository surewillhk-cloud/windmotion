<template>
  <div class="signal-layer">
    <div v-for="signal in signals" :key="signal.id"
      class="signal-item" :class="[signal.type, { active: signal.active }]"
      :style="{ left: `${signal.x}%`, top: `${signal.y}%` }"
      @click="$emit('signalClick', signal)">
      <span class="signal-icon">{{ signalIcon(signal.type) }}</span>
      <div class="signal-tooltip">
        <span class="signal-label">{{ signal.label }}</span>
        <span v-if="signal.value" class="signal-value mono-number">{{ signal.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  signals: Array<{
    id: string
    type: 'buy' | 'sell' | 'alert' | 'whale'
    label: string
    value?: string
    x: number
    y: number
    active?: boolean
  }>
}>()
defineEmits(['signalClick'])

function signalIcon(type: string): string {
  const icons: Record<string, string> = {
    buy: '▲', sell: '▼', alert: '⚡', whale: '🐋'
  }
  return icons[type] || '●'
}
</script>

<style scoped>
.signal-layer { position: absolute; inset: 0; pointer-events: none; }
.signal-item { position: absolute; pointer-events: auto; cursor: pointer; transform: translate(-50%, -50%); z-index: 10; }
.signal-icon { display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; font-size: 12px; transition: all 0.2s; }
.signal-item.buy .signal-icon { background: rgba(0,255,136,0.2); color: #00ff88; border: 1px solid rgba(0,255,136,0.4); }
.signal-item.sell .signal-icon { background: rgba(255,51,102,0.2); color: #ff3366; border: 1px solid rgba(255,51,102,0.4); }
.signal-item.alert .signal-icon { background: rgba(255,170,0,0.2); color: #ffaa00; border: 1px solid rgba(255,170,0,0.4); }
.signal-item.whale .signal-icon { background: rgba(0,229,255,0.2); color: #00e5ff; border: 1px solid rgba(0,229,255,0.4); }
.signal-item.active .signal-icon { box-shadow: 0 0 12px rgba(0,229,255,0.5); transform: scale(1.2); }
.signal-tooltip { position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%); padding: 4px 8px; background: #111827; border: 1px solid var(--border); border-radius: 4px; white-space: nowrap; opacity: 0; pointer-events: none; transition: opacity 0.2s; margin-bottom: 4px; }
.signal-item:hover .signal-tooltip { opacity: 1; }
.signal-label { font-size: 11px; color: var(--text-primary); display: block; }
.signal-value { font-size: 12px; color: var(--accent); }
</style>
