<template>
  <div id="app-root">
    <nav v-if="!isEmbed" class="top-nav">
      <div class="nav-brand">
        <span class="brand-icon">◆</span>
        <span class="brand-text">WIND MOTION</span>
      </div>
      <div class="nav-links">
        <router-link to="/dashboard">{{ t('nav.dashboard') }}</router-link>
        <router-link to="/filters">{{ t('nav.filters') }}</router-link>
        <router-link to="/history">{{ t('nav.history') }}</router-link>
        <router-link to="/whales">{{ t('nav.whales') }}</router-link>
        <router-link to="/recommend">{{ t('nav.recommend') }}</router-link>
        <router-link to="/settings">{{ t('nav.settings') }}</router-link>
      </div>
      <div class="nav-actions">
        <select v-model="locale" class="lang-select glow-input">
          <option value="zh-CN">简体中文</option>
          <option value="zh-TW">繁體中文</option>
          <option value="en">English</option>
          <option value="th">ภาษาไทย</option>
          <option value="ko">한국어</option>
          <option value="ja">日本語</option>
          <option value="vi">Tiếng Việt</option>
        </select>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
const route = useRoute()
const isEmbed = computed(() => route.path === '/embed')
</script>

<style lang="scss" scoped>
#app-root {
  min-height: 100vh;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-icon {
  color: var(--accent);
  font-size: 20px;
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}

.brand-text {
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 2px;
  color: var(--accent);
}

.nav-links {
  display: flex;
  gap: 24px;

  a {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 14px;
    transition: color 0.2s;

    &:hover, &.router-link-active {
      color: var(--accent);
    }
  }
}

.lang-select {
  padding: 4px 8px;
  font-size: 12px;
}
</style>
