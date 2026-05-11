import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export interface AppSettings {
  language: string
  theme: 'dark' | 'light'
  timezone: string
  apiEndpoint: string
  wsEndpoint: string
  refreshInterval: number
  maxRetries: number
  enableSound: boolean
  enableDesktopNotification: boolean
  apiKey: string
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings>({
    language: 'zh-CN',
    theme: 'dark',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    apiEndpoint: '/api',
    wsEndpoint: '/ws',
    refreshInterval: 30,
    maxRetries: 3,
    enableSound: true,
    enableDesktopNotification: false,
    apiKey: ''
  })

  const isLoaded = ref(false)

  function loadSettings() {
    try {
      const saved = localStorage.getItem('windmotion-settings')
      if (saved) {
        const parsed = JSON.parse(saved)
        settings.value = { ...settings.value, ...parsed }
      }
    } catch (e) {
      console.error('Failed to load settings:', e)
    }
    isLoaded.value = true
  }

  function saveSettings() {
    try {
      localStorage.setItem('windmotion-settings', JSON.stringify(settings.value))
    } catch (e) {
      console.error('Failed to save settings:', e)
    }
  }

  function updateSetting<K extends keyof AppSettings>(key: K, value: AppSettings[K]) {
    settings.value[key] = value
    saveSettings()
  }

  function resetSettings() {
    settings.value = {
      language: 'zh-CN',
      theme: 'dark',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      apiEndpoint: '/api',
      wsEndpoint: '/ws',
      refreshInterval: 30,
      maxRetries: 3,
      enableSound: true,
      enableDesktopNotification: false,
      apiKey: ''
    }
    saveSettings()
  }

  watch(settings, saveSettings, { deep: true })

  loadSettings()

  return {
    settings,
    isLoaded,
    loadSettings,
    saveSettings,
    updateSetting,
    resetSettings
  }
})
