<template>
  <div class="narrative-panel">
    <h3 v-if="title" class="narrative-title">{{ title }}</h3>
    <div class="narrative-scroll" ref="scrollContainer">
      <div v-for="(entry, i) in entries" :key="i"
        :class="['narrative-entry', { active: i === activeIndex, highlight: entry.highlight }]"
        @click="$emit('select', i)">
        <div class="entry-time mono-number">{{ entry.time }}</div>
        <div class="entry-content">
          <span v-if="entry.type" class="entry-type" :class="entry.type">{{ entry.type }}</span>
          <p class="entry-text">{{ entry.text }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{
  entries: Array<{
    time: string
    text: string
    type?: string
    highlight?: boolean
  }>
  activeIndex?: number
  title?: string
}>()
defineEmits(['select'])

const scrollContainer = ref<HTMLElement>()

watch(() => props.activeIndex, async (idx) => {
  if (idx !== undefined && scrollContainer.value) {
    await nextTick()
    const el = scrollContainer.value.children[idx] as HTMLElement
    el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
})
</script>

<style scoped>
.narrative-panel { padding: 12px 0; }
.narrative-title { font-size: 14px; color: var(--text-secondary); font-weight: 500; margin-bottom: 12px; }
.narrative-scroll { max-height: 400px; overflow-y: auto; }
.narrative-scroll::-webkit-scrollbar { width: 4px; }
.narrative-scroll::-webkit-scrollbar-thumb { background: rgba(0,229,255,0.2); border-radius: 2px; }
.narrative-entry { display: flex; gap: 12px; padding: 10px 12px; cursor: pointer; border-radius: 6px; transition: background 0.2s; border-left: 2px solid transparent; }
.narrative-entry:hover { background: rgba(0,229,255,0.03); }
.narrative-entry.active { background: rgba(0,229,255,0.06); border-left-color: var(--accent); }
.narrative-entry.highlight { border-left-color: #ffaa00; }
.entry-time { font-size: 11px; color: var(--text-muted); min-width: 50px; padding-top: 2px; }
.entry-content { flex: 1; }
.entry-type { font-size: 10px; padding: 1px 6px; border-radius: 3px; margin-right: 6px; }
.entry-type.buy { background: rgba(0,255,136,0.15); color: #00ff88; }
.entry-type.sell { background: rgba(255,51,102,0.15); color: #ff3366; }
.entry-type.event { background: rgba(124,58,237,0.15); color: #7c3aed; }
.entry-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; margin: 4px 0 0; }
</style>
