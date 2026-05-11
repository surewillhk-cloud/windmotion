<template>
  <span :class="['mono-number', { changed: showChange }]">{{ displayValue }}</span>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { formatCurrency, formatPercent, formatNumber } from '@/i18n/helpers/number-format'

const props = defineProps<{
  value: number
  format?: 'currency' | 'percent' | 'number' | 'raw'
  prefix?: string
  suffix?: string
}>()

const showChange = ref(false)
const prevValue = ref(props.value)

const displayValue = computed(() => {
  let formatted: string
  switch (props.format) {
    case 'currency': formatted = formatCurrency(props.value); break
    case 'percent': formatted = formatPercent(props.value); break
    case 'number': formatted = formatNumber(props.value); break
    default: formatted = String(props.value)
  }
  return `${props.prefix || ''}${formatted}${props.suffix || ''}`
})

watch(() => props.value, (newVal) => {
  if (newVal !== prevValue.value) {
    showChange.value = true
    prevValue.value = newVal
    setTimeout(() => { showChange.value = false }, 300)
  }
})
</script>

<style scoped>
.changed { animation: data-pulse 0.3s ease; }
@keyframes data-pulse {
  0% { color: var(--text-primary); }
  50% { color: var(--accent); text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }
  100% { color: var(--text-primary); }
}
</style>
