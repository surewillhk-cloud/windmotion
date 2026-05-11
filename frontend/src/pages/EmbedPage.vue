<template>
  <div class="embed-page">
    <div class="embed-header" v-if="!autoplay">
      <div class="embed-brand">
        <img v-if="brandLogo" :src="brandLogo" class="brand-logo" alt="logo" />
        <span class="brand-name">{{ brandName }}</span>
      </div>
      <div class="embed-controls">
        <select v-model="currentLang" class="lang-select glow-input" @change="changeLang">
          <option v-for="lang in languages" :key="lang.code" :value="lang.code">{{ lang.label }}</option>
        </select>
        <GlowButton variant="primary" @click="startAnalysis">Start</GlowButton>
      </div>
    </div>

    <WindTunnelEmbed
      ref="embedRef"
      :case-data="currentCase"
      :lang="currentLang"
      :autoplay="autoplay"
      @complete="onComplete" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import GlowButton from '@/components/common/GlowButton.vue'
import WindTunnelEmbed from '@/../embed/WindTunnelEmbed.vue'

const { locale } = useI18n()

const embedRef = ref()
const currentLang = ref('zh')
const autoplay = ref(false)
const brandName = ref('Wind Motion')
const brandLogo = ref('')

const languages = [
  { code: 'zh', label: '中文' },
  { code: 'en', label: 'English' },
  { code: 'ja', label: '日本語' },
  { code: 'ko', label: '한국어' },
  { code: 'es', label: 'Español' },
  { code: 'de', label: 'Deutsch' },
  { code: 'fr', label: 'Français' }
]

const cases = ref<any[]>([])
const currentCaseId = ref('')

const currentCase = computed(() => {
  return cases.value.find(c => c.id === currentCaseId.value) || cases.value[0]
})

function changeLang() {
  locale.value = currentLang.value
}

function startAnalysis() {
  embedRef.value?.start()
}

function onComplete(result: any) {
  console.log('Analysis complete:', result)
}

onMounted(() => {
  // Parse URL params
  const params = new URLSearchParams(window.location.search)
  if (params.get('brand')) brandName.value = params.get('brand')!
  if (params.get('logo')) brandLogo.value = params.get('logo')!
  if (params.get('lang')) {
    currentLang.value = params.get('lang')!
    locale.value = currentLang.value
  }
  if (params.get('autoplay') === 'true') autoplay.value = true
  if (params.get('case')) currentCaseId.value = params.get('case')!

  // Load cases
  import('@/../embed/cases/token-x-10x.json').then(m => cases.value.push(m.default || m))
  import('@/../embed/cases/eth-whale-escape.json').then(m => cases.value.push(m.default || m))
  import('@/../embed/cases/cross-chain-hunter.json').then(m => cases.value.push(m.default || m))
})
</script>

<style scoped>
.embed-page { min-height: 100vh; background: #050a14; display: flex; flex-direction: column; }
.embed-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; border-bottom: 1px solid rgba(0,229,255,0.1); }
.embed-brand { display: flex; align-items: center; gap: 10px; }
.brand-logo { height: 28px; width: auto; }
.brand-name { font-size: 16px; font-family: var(--font-mono); color: #00e5ff; font-weight: 600; }
.embed-controls { display: flex; gap: 10px; align-items: center; }
.lang-select { padding: 6px 10px; font-size: 12px; background: rgba(0,0,0,0.3); border: 1px solid rgba(0,229,255,0.2); border-radius: 4px; color: #e0e0e0; }
.glow-input:focus { border-color: #00e5ff; outline: none; }
</style>
