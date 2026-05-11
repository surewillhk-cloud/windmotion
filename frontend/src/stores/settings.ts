import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import * as api from '@/services/api'

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

const defaultSettings: AppSettings = {
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

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings>({ ...defaultSettings })
  const isLoaded = ref(false)

  // Load from localStorage first, then sync with backend
  function loadSettings() {
    try {
      const saved = localStorage.getItem('windmotion-settings')
      if (saved) {
        settings.value = { ...defaultSettings, ...JSON.parse(saved) }
      }
    } catch (e) {
      console.error('Failed to load settings from localStorage:', e)
    }
    isLoaded.value = true
  }

  // Sync settings with backend
  async function syncFromServer() {
    try {
      const data = await api.getSettings()
      if (data && typeof data === 'object') {
        settings.value = { ...settings.value, ...data }
        saveToLocal()
      }
    } catch {
      // Backend might not be available yet - use local settings
    }
  }

  function saveToLocal() {
    try {
      localStorage.setItem('windmotion-settings', JSON.stringify(settings.value))
    } catch (e) {
      console.error('Failed to save settings:', e)
    }
  }

  async function saveSettings() {
    saveToLocal()
    try {
      await api.updateSettings(settings.value)
    } catch {
      // Save locally even if backend fails
    }
  }

  function updateSetting<K extends keyof AppSettings>(key: K, value: AppSettings[K]) {
    settings.value[key] = value
    saveToLocal()
  }

  function resetSettings() {
    settings.value = { ...defaultSettings }
    saveToLocal()
  }

  // Auto-save on changes
  watch(settings, saveToLocal, { deep: true })

  // Initialize
  loadSettings()

  return {
    settings, isLoaded,
    loadSettings, saveSettings, syncFromServer,
    updateSetting, resetSettings
  }
})
