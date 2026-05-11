<template>
  <div ref="shadowHost" class="windmotion-embed-host" />
</template>

<script setup lang="ts">
/**
 * EmbedApp.vue - Embed entry point with Shadow DOM isolation + postMessage communication
 *
 * Usage:
 *   <script src="https://windmotion.io/embed.js" data-case="token-x-10x" data-brand="MyProject" data-lang="en"><\/script>
 *
 * Or via iframe:
 *   <iframe src="https://windmotion.io/embed?case=token-x-10x&brand=MyProject&lang=en" width="100%" height="700"><\/iframe>
 *
 * postMessage API (parent → embed):
 *   { type: 'windmotion', action: 'play' }
 *   { type: 'windmotion', action: 'pause' }
 *   { type: 'windmotion', action: 'setStage', stage: 2 }
 *   { type: 'windmotion', action: 'setLang', lang: 'en' }
 *
 * postMessage API (embed → parent):
 *   { type: 'windmotion', event: 'ready', data: { brand, case, lang } }
 *   { type: 'windmotion', event: 'stageChange', data: { stage, step } }
 *   { type: 'windmotion', event: 'complete', data: { duration, cost } }
 */
import { ref, onMounted, onUnmounted } from 'vue'

const shadowHost = ref<HTMLElement>()

// Allowed origins for postMessage
const ALLOWED_ORIGINS = ['*'] // In production, restrict to specific domains

function handleMessage(event: MessageEvent) {
  if (!event.data || event.data.type !== 'windmotion') return

  const { action, ...params } = event.data

  switch (action) {
    case 'play':
      // Forward to embedded iframe
      shadowHost.value?.querySelector('iframe')?.contentWindow?.postMessage({ type: 'windmotion', action: 'play' }, '*')
      break
    case 'pause':
      shadowHost.value?.querySelector('iframe')?.contentWindow?.postMessage({ type: 'windmotion', action: 'pause' }, '*')
      break
    case 'setStage':
      shadowHost.value?.querySelector('iframe')?.contentWindow?.postMessage({ type: 'windmotion', action: 'setStage', stage: params.stage }, '*')
      break
    case 'setLang':
      shadowHost.value?.querySelector('iframe')?.contentWindow?.postMessage({ type: 'windmotion', action: 'setLang', lang: params.lang }, '*')
      break
  }
}

function postToParent(event: string, data: any) {
  window.parent.postMessage({ type: 'windmotion', event, data }, '*')
}

onMounted(() => {
  // Listen for messages from parent
  window.addEventListener('message', handleMessage)

  // Notify parent that embed is ready
  const urlParams = new URLSearchParams(window.location.search)
  postToParent('ready', {
    brand: urlParams.get('brand') || 'Wind Motion',
    case: urlParams.get('case') || 'default',
    lang: urlParams.get('lang') || navigator.language,
  })
})

onUnmounted(() => {
  window.removeEventListener('message', handleMessage)
})

/**
 * Creates a Shadow DOM-isolated embed instance.
 * Call this from a vanilla JS entry point to mount the embed in a shadow root.
 */
export function createShadowEmbed(container: HTMLElement, options: Record<string, string> = {}) {
  const shadow = container.attachShadow({ mode: 'open' })

  // Inject scoped styles
  const style = document.createElement('style')
  style.textContent = `
    :host { all: initial; display: block; font-family: 'Noto Sans SC', sans-serif; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    iframe { width: 100%; height: 100%; border: none; border-radius: 8px; }
  `
  shadow.appendChild(style)

  // Create iframe with embed URL
  const iframe = document.createElement('iframe')
  const params = new URLSearchParams(options)
  iframe.src = `/embed?${params.toString()}`
  iframe.loading = 'lazy'
  iframe.style.width = '100%'
  iframe.style.height = options.height || '700px'
  iframe.style.border = 'none'
  iframe.style.borderRadius = '12px'
  shadow.appendChild(iframe)

  // Relay postMessage between iframe and parent
  window.addEventListener('message', (event) => {
    if (event.data?.type === 'windmotion') {
      // Forward to parent
      if (window.parent !== window) {
        window.parent.postMessage(event.data, '*')
      }
    }
  })

  return {
    play: () => iframe.contentWindow?.postMessage({ type: 'windmotion', action: 'play' }, '*'),
    pause: () => iframe.contentWindow?.postMessage({ type: 'windmotion', action: 'pause' }, '*'),
    setStage: (stage: number) => iframe.contentWindow?.postMessage({ type: 'windmotion', action: 'setStage', stage }, '*'),
    setLang: (lang: string) => iframe.contentWindow?.postMessage({ type: 'windmotion', action: 'setLang', lang }, '*'),
    destroy: () => { shadow.innerHTML = '' }
  }
}
</script>

<style scoped>
.windmotion-embed-host {
  width: 100%;
  min-height: 500px;
  border-radius: 12px;
  overflow: hidden;
}
</style>
