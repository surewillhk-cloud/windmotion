<template>
  <div class="whale-card glow-card" @click="$emit('click', whale)">
    <div class="whale-header">
      <span class="address mono-number">{{ shortAddress(whale.address) }}</span>
      <span class="score" :style="{ color: scoreColor }">{{ whale.score?.toFixed(0) }}/100</span>
    </div>
    <div class="whale-stats">
      <div class="stat">
        <span class="stat-label">Profit</span>
        <span class="stat-value mono-number">{{ formatCurrency(whale.total_profit_usd) }}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Win Rate</span>
        <span class="stat-value mono-number">{{ whale.win_rate?.toFixed(0) }}%</span>
      </div>
      <div class="stat">
        <span class="stat-label">ROI</span>
        <span class="stat-value mono-number">{{ whale.roi?.toFixed(1) }}x</span>
      </div>
      <div class="stat">
        <span class="stat-label">Trades</span>
        <span class="stat-value mono-number">{{ whale.trade_count }}</span>
      </div>
    </div>
    <div class="whale-tags">
      <span v-for="tag in whale.labels" :key="tag" class="tag">{{ tag }}</span>
    </div>
    <div class="whale-actions">
      <GlowButton variant="primary" @click.stop="$emit('analyze', whale.address)">
        {{ t('common.analyze') }}
      </GlowButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import GlowButton from '@/components/common/GlowButton.vue'
import { formatCurrency } from '@/i18n/helpers/number-format'

const { t } = useI18n()
const props = defineProps<{ whale: any }>()
defineEmits(['click', 'analyze'])

function shortAddress(addr: string) {
  return addr ? `${addr.slice(0, 6)}...${addr.slice(-4)}` : ''
}

const scoreColor = computed(() => {
  const s = props.whale.score || 0
  if (s >= 80) return '#00ff88'
  if (s >= 60) return '#00e5ff'
  if (s >= 40) return '#ffaa00'
  return '#ff3366'
})
</script>

<style scoped>
.whale-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.address { font-size: 14px; color: var(--accent); }
.score { font-family: var(--font-mono); font-size: 16px; font-weight: 600; }
.whale-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 12px; }
.stat { text-align: center; }
.stat-label { display: block; font-size: 10px; color: var(--text-muted); text-transform: uppercase; }
.stat-value { display: block; font-size: 13px; color: var(--text-primary); }
.whale-tags { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 12px; }
.tag { font-size: 10px; padding: 2px 8px; border-radius: 10px; background: rgba(0,229,255,0.1); color: var(--accent); border: 1px solid rgba(0,229,255,0.2); }
.whale-actions { display: flex; justify-content: flex-end; }
</style>
