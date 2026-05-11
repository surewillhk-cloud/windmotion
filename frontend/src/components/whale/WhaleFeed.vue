<template>
  <div class="whale-feed">
    <div v-if="!items?.length" class="feed-empty">
      <span class="empty-icon">📡</span>
      <span class="empty-text">Waiting for whale activity...</span>
    </div>
    <TransitionGroup name="feed" tag="div" class="feed-list">
      <div v-for="item in items" :key="item.id || item.address" class="feed-item" @click="$emit('click', item)">
        <div class="feed-icon" :class="item.type">
          {{ item.type === 'buy' ? '▲' : item.type === 'sell' ? '▼' : '●' }}
        </div>
        <div class="feed-content">
          <div class="feed-header">
            <span class="feed-addr mono-number">{{ shortAddr(item.address) }}</span>
            <span class="feed-time mono-number">{{ item.time || 'now' }}</span>
          </div>
          <div class="feed-detail">
            <span class="feed-action">{{ item.action || item.type }}</span>
            <span v-if="item.token" class="feed-token">{{ item.token }}</span>
            <span v-if="item.amount" class="feed-amount mono-number">{{ item.amount }}</span>
          </div>
          <div v-if="item.usd_value" class="feed-value">
            <span class="mono-number">${{ formatNumber(item.usd_value) }}</span>
          </div>
        </div>
        <button class="feed-analyze" @click.stop="$emit('analyze', item.address)">🔍</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<any>
}>()
defineEmits(['click', 'analyze'])

function shortAddr(addr: string) {
  return addr ? `${addr.slice(0, 6)}...${addr.slice(-4)}` : ''
}

function formatNumber(n: number): string {
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M'
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K'
  return n.toFixed(0)
}
</script>

<style scoped>
.whale-feed { max-height: 600px; overflow-y: auto; }
.whale-feed::-webkit-scrollbar { width: 4px; }
.whale-feed::-webkit-scrollbar-thumb { background: rgba(0,229,255,0.2); border-radius: 2px; }
.feed-empty { text-align: center; padding: 40px 20px; color: var(--text-muted); }
.empty-icon { font-size: 32px; display: block; margin-bottom: 8px; }
.empty-text { font-size: 13px; }
.feed-list { display: flex; flex-direction: column; gap: 6px; }
.feed-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 6px; cursor: pointer; transition: background 0.2s; border: 1px solid transparent; }
.feed-item:hover { background: rgba(0,229,255,0.04); border-color: rgba(0,229,255,0.1); }
.feed-icon { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
.feed-icon.buy { background: rgba(0,255,136,0.15); color: #00ff88; }
.feed-icon.sell { background: rgba(255,51,102,0.15); color: #ff3366; }
.feed-content { flex: 1; min-width: 0; }
.feed-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
.feed-addr { font-size: 13px; color: var(--accent); }
.feed-time { font-size: 10px; color: var(--text-muted); }
.feed-detail { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.feed-action { color: var(--text-secondary); }
.feed-token { color: var(--text-primary); font-weight: 500; }
.feed-amount { color: var(--accent); }
.feed-value { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.feed-analyze { background: transparent; border: 1px solid var(--border); border-radius: 4px; padding: 4px 8px; cursor: pointer; font-size: 14px; transition: all 0.2s; }
.feed-analyze:hover { border-color: var(--accent); background: rgba(0,229,255,0.1); }
.feed-enter-active { transition: all 0.3s ease; }
.feed-leave-active { transition: all 0.2s ease; }
.feed-enter-from { opacity: 0; transform: translateY(-10px); }
.feed-leave-to { opacity: 0; transform: translateX(20px); }
</style>
