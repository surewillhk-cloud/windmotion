<template>
  <div class="settings-page">
    <h1 class="page-title glow-text">{{ t('settings.title') || 'Settings' }}</h1>

    <div class="settings-sections">
      <!-- API Keys -->
      <section class="settings-section glow-card">
        <h2>API Key Management</h2>
        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Blockchain API</span>
            <span class="setting-desc">BSCScan, Etherscan, etc.</span>
          </div>
          <input v-model="settings.blockchainApiKey" type="password" class="glow-input" placeholder="Enter API key" />
        </div>
        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Social API</span>
            <span class="setting-desc">Twitter, Telegram monitoring</span>
          </div>
          <input v-model="settings.socialApiKey" type="password" class="glow-input" placeholder="Enter API key" />
        </div>
        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">AI Model API</span>
            <span class="setting-desc">LLM provider key</span>
          </div>
          <input v-model="settings.aiApiKey" type="password" class="glow-input" placeholder="Enter API key" />
        </div>
      </section>

      <!-- Notifications -->
      <section class="settings-section glow-card">
        <h2>Notification Configuration</h2>
        <div class="setting-row toggle-row">
          <div class="setting-info">
            <span class="setting-label">Enable Notifications</span>
            <span class="setting-desc">Receive alerts for whale activity</span>
          </div>
          <button :class="['toggle-btn', { active: settings.notificationsEnabled }]" @click="settings.notificationsEnabled = !settings.notificationsEnabled">
            {{ settings.notificationsEnabled ? 'ON' : 'OFF' }}
          </button>
        </div>
        <div v-if="settings.notificationsEnabled">
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Telegram Bot Token</span>
              <span class="setting-desc">For Telegram notifications</span>
            </div>
            <input v-model="settings.telegramToken" type="password" class="glow-input" placeholder="Bot token" />
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Discord Webhook</span>
              <span class="setting-desc">For Discord notifications</span>
            </div>
            <input v-model="settings.discordWebhook" type="text" class="glow-input" placeholder="Webhook URL" />
          </div>
          <div class="setting-row">
            <div class="setting-info">
              <span class="setting-label">Email Address</span>
              <span class="setting-desc">For email alerts</span>
            </div>
            <input v-model="settings.email" type="email" class="glow-input" placeholder="your@email.com" />
          </div>
        </div>
      </section>

      <!-- Model Routing -->
      <section class="settings-section glow-card">
        <h2>Model Routing</h2>
        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Graph Analysis</span>
            <span class="setting-desc">Model for causal graph construction</span>
          </div>
          <select v-model="settings.graphModel" class="glow-input">
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-4-turbo">GPT-4 Turbo</option>
            <option value="claude-3">Claude 3</option>
            <option value="local">Local Model</option>
          </select>
        </div>
        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Probability Estimation</span>
            <span class="setting-desc">Model for probability calculations</span>
          </div>
          <select v-model="settings.probModel" class="glow-input">
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-4-turbo">GPT-4 Turbo</option>
            <option value="claude-3">Claude 3</option>
            <option value="local">Local Model</option>
          </select>
        </div>
        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Report Generation</span>
            <span class="setting-desc">Model for final report writing</span>
          </div>
          <select v-model="settings.reportModel" class="glow-input">
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-4-turbo">GPT-4 Turbo</option>
            <option value="claude-3">Claude 3</option>
            <option value="local">Local Model</option>
          </select>
        </div>
      </section>

      <!-- Language -->
      <section class="settings-section glow-card">
        <h2>Language & Display</h2>
        <div class="setting-row">
          <div class="setting-info">
            <span class="setting-label">Language</span>
            <span class="setting-desc">Interface language</span>
          </div>
          <select v-model="settings.language" class="glow-input" @change="changeLang">
            <option value="zh">中文</option>
            <option value="en">English</option>
            <option value="ja">日本語</option>
            <option value="ko">한국어</option>
          </select>
        </div>
        <div class="setting-row toggle-row">
          <div class="setting-info">
            <span class="setting-label">Scanline Effect</span>
            <span class="setting-desc">CRT scanline overlay</span>
          </div>
          <button :class="['toggle-btn', { active: settings.scanline }]" @click="settings.scanline = !settings.scanline">
            {{ settings.scanline ? 'ON' : 'OFF' }}
          </button>
        </div>
      </section>
    </div>

    <div class="settings-actions">
      <GlowButton variant="primary" @click="saveSettings">Save Settings</GlowButton>
      <GlowButton variant="ghost" @click="resetSettings">Reset to Default</GlowButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import GlowButton from '@/components/common/GlowButton.vue'

const { t, locale } = useI18n()

const settings = reactive({
  blockchainApiKey: '',
  socialApiKey: '',
  aiApiKey: '',
  notificationsEnabled: false,
  telegramToken: '',
  discordWebhook: '',
  email: '',
  graphModel: 'gpt-4',
  probModel: 'gpt-4',
  reportModel: 'gpt-4-turbo',
  language: locale.value || 'zh',
  scanline: true
})

function changeLang() {
  locale.value = settings.language
}

function saveSettings() {
  localStorage.setItem('wm_settings', JSON.stringify(settings))
}

function resetSettings() {
  Object.assign(settings, {
    blockchainApiKey: '', socialApiKey: '', aiApiKey: '',
    notificationsEnabled: false, telegramToken: '', discordWebhook: '', email: '',
    graphModel: 'gpt-4', probModel: 'gpt-4', reportModel: 'gpt-4-turbo',
    language: 'zh', scanline: true
  })
}
</script>

<style scoped>
.settings-page { padding: 24px; max-width: 800px; margin: 0 auto; }
.page-title { font-size: 24px; font-family: var(--font-mono); color: var(--accent); margin-bottom: 24px; }
.settings-sections { display: flex; flex-direction: column; gap: 16px; }
.settings-section { padding: 20px; }
.settings-section h2 { font-size: 16px; color: var(--text-primary); margin-bottom: 16px; font-weight: 600; }
.setting-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.03); }
.setting-row:last-child { border-bottom: none; }
.setting-info { flex: 1; }
.setting-label { display: block; font-size: 14px; color: var(--text-primary); margin-bottom: 2px; }
.setting-desc { display: block; font-size: 11px; color: var(--text-muted); }
.glow-input { padding: 8px 12px; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-family: var(--font-mono); font-size: 13px; width: 240px; }
.glow-input:focus { border-color: var(--accent); outline: none; box-shadow: 0 0 8px rgba(0,229,255,0.2); }
.toggle-row { height: 48px; }
.toggle-btn { font-size: 12px; padding: 5px 18px; border-radius: 14px; border: 1px solid var(--border); background: transparent; color: var(--text-muted); cursor: pointer; font-family: var(--font-mono); transition: all 0.2s; }
.toggle-btn.active { background: rgba(0,255,136,0.15); border-color: #00ff88; color: #00ff88; }
.settings-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 24px; }
</style>
