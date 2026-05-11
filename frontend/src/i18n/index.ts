import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN.json'
import zhTW from './locales/zh-TW.json'
import en from './locales/en.json'
import th from './locales/th.json'
import ko from './locales/ko.json'
import ja from './locales/ja.json'
import vi from './locales/vi.json'

const i18n = createI18n({
  legacy: false,
  locale: navigator.language === 'zh-TW' ? 'zh-TW' : 'zh-CN',
  fallbackLocale: 'en',
  messages: {
    'zh-CN': zhCN,
    'zh-TW': zhTW,
    'en': en,
    'th': th,
    'ko': ko,
    'ja': ja,
    'vi': vi,
  },
})

export default i18n
