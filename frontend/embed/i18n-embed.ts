/**
 * Embed-specific i18n for Wind Tunnel Embed.
 * Lightweight translations for embed page (no external dependency).
 * Supports 7 languages as specified in design doc §13.3.
 */

export type EmbedLang = 'zh-CN' | 'zh-TW' | 'en' | 'th' | 'ko' | 'ja' | 'vi'

interface EmbedMessages {
  liveInference: string
  stage: string
  step: string
  complete: string
  elapsed: string
  agents: string
  calls: string
  cost: string
  graphBuild: string
  eventChain: string
  probability: string
  deliberation: string
  report: string
  contactUs: string
  tryDemo: string
  poweredBy: string
  autoPlay: string
  speed: string
  prev: string
  next: string
  restart: string
  pause: string
}

const messages: Record<EmbedLang, EmbedMessages> = {
  'zh-CN': {
    liveInference: '实时推演',
    stage: '阶段',
    step: '步骤',
    complete: '完成',
    elapsed: '已用时',
    agents: '个 Agent',
    calls: '次调用',
    cost: '成本',
    graphBuild: '因果图谱构建',
    eventChain: '事件链处理',
    probability: '概率定价',
    deliberation: '审议',
    report: '报告生成',
    contactUs: '联系我们',
    tryDemo: '试用 Demo',
    poweredBy: '由 {brand} 提供支持',
    autoPlay: '自动播放',
    speed: '速度',
    prev: '上一步',
    next: '下一步',
    restart: '重新开始',
    pause: '暂停',
  },
  'zh-TW': {
    liveInference: '即時推演',
    stage: '階段',
    step: '步驟',
    complete: '完成',
    elapsed: '已用時',
    agents: '個 Agent',
    calls: '次調用',
    cost: '成本',
    graphBuild: '因果圖譜構建',
    eventChain: '事件鏈處理',
    probability: '概率定價',
    deliberation: '審議',
    report: '報告生成',
    contactUs: '聯繫我們',
    tryDemo: '試用 Demo',
    poweredBy: '由 {brand} 提供支持',
    autoPlay: '自動播放',
    speed: '速度',
    prev: '上一步',
    next: '下一步',
    restart: '重新開始',
    pause: '暫停',
  },
  en: {
    liveInference: 'LIVE INFERENCE',
    stage: 'Stage',
    step: 'Step',
    complete: 'Complete',
    elapsed: 'Elapsed',
    agents: 'Agents',
    calls: 'calls',
    cost: 'Cost',
    graphBuild: 'Causal Graph Build',
    eventChain: 'Event Chain',
    probability: 'Probability Pricing',
    deliberation: 'Deliberation',
    report: 'Report',
    contactUs: 'Contact Us',
    tryDemo: 'Try Demo',
    poweredBy: 'Powered by {brand}',
    autoPlay: 'Auto',
    speed: 'Speed',
    prev: 'Prev',
    next: 'Next',
    restart: 'Restart',
    pause: 'Pause',
  },
  th: {
    liveInference: 'การอนุมานสด',
    stage: 'ขั้นตอน',
    step: 'ขั้น',
    complete: 'เสร็จสิ้น',
    elapsed: 'เวลาที่ใช้',
    agents: 'เอเจนต์',
    calls: 'ครั้ง',
    cost: 'ต้นทุน',
    graphBuild: 'สร้างกราฟสาเหตุ',
    eventChain: 'ห่วงโซ่เหตุการณ์',
    probability: 'กำหนดราคาความน่าจะเป็น',
    deliberation: 'การพิจารณา',
    report: 'รายงาน',
    contactUs: 'ติดต่อเรา',
    tryDemo: 'ทดลอง Demo',
    poweredBy: 'ขับเคลื่อนโดย {brand}',
    autoPlay: 'เล่นอัตโนมัติ',
    speed: 'ความเร็ว',
    prev: 'ก่อนหน้า',
    next: 'ถัดไป',
    restart: 'เริ่มใหม่',
    pause: 'หยุดชั่วคราว',
  },
  ko: {
    liveInference: '실시간 추론',
    stage: '단계',
    step: '步骤',
    complete: '완료',
    elapsed: '경과',
    agents: '에이전트',
    calls: '호출',
    cost: '비용',
    graphBuild: '인과 그래프 구축',
    eventChain: '이벤트 체인',
    probability: '확률 가격 책정',
    deliberation: '심의',
    report: '보고서',
    contactUs: '문의하기',
    tryDemo: '데모 체험',
    poweredBy: '{brand} 제공',
    autoPlay: '자동 재생',
    speed: '속도',
    prev: '이전',
    next: '다음',
    restart: '다시 시작',
    pause: '일시 정지',
  },
  ja: {
    liveInference: 'ライブ推論',
    stage: 'ステージ',
    step: 'ステップ',
    complete: '完了',
    elapsed: '経過',
    agents: 'エージェント',
    calls: '回',
    cost: 'コスト',
    graphBuild: '因果グラフ構築',
    eventChain: 'イベントチェーン',
    probability: '確率価格設定',
    deliberation: '審議',
    report: 'レポート',
    contactUs: 'お問い合わせ',
    tryDemo: 'デモを試す',
    poweredBy: '{brand} 提供',
    autoPlay: '自動再生',
    speed: '速度',
    prev: '前へ',
    next: '次へ',
    restart: '再開',
    pause: '一時停止',
  },
  vi: {
    liveInference: 'Suy luận trực tiếp',
    stage: 'Giai đoạn',
    step: 'Bước',
    complete: 'Hoàn thành',
    elapsed: 'Đã trôi qua',
    agents: 'Agent',
    calls: 'lần gọi',
    cost: 'Chi phí',
    graphBuild: 'Xây dựng đồ thị nhân quả',
    eventChain: 'Chuỗi sự kiện',
    probability: 'Định giá xác suất',
    deliberation: 'Thảo luận',
    report: 'Báo cáo',
    contactUs: 'Liên hệ',
    tryDemo: 'Thử Demo',
    poweredBy: 'Được hỗ trợ bởi {brand}',
    autoPlay: 'Tự động phát',
    speed: 'Tốc độ',
    prev: 'Trước',
    next: 'Tiếp',
    restart: 'Bắt đầu lại',
    pause: 'Tạm dừng',
  },
}

/**
 * Get embed translation for a key in the specified language.
 */
export function t(key: keyof EmbedMessages, lang: EmbedLang = 'en', vars?: Record<string, string>): string {
  const msg = messages[lang]?.[key] || messages.en[key] || key
  if (vars) {
    return Object.entries(vars).reduce((s, [k, v]) => s.replace(`{${k}}`, v), msg)
  }
  return msg
}

/**
 * Detect language from URL param or browser locale.
 */
export function detectEmbedLang(): EmbedLang {
  const urlLang = new URLSearchParams(window.location.search).get('lang')
  if (urlLang && urlLang in messages) return urlLang as EmbedLang

  const browserLang = navigator.language
  if (browserLang.startsWith('zh-CN')) return 'zh-CN'
  if (browserLang.startsWith('zh-TW') || browserLang.startsWith('zh-Hant')) return 'zh-TW'
  if (browserLang.startsWith('th')) return 'th'
  if (browserLang.startsWith('ko')) return 'ko'
  if (browserLang.startsWith('ja')) return 'ja'
  if (browserLang.startsWith('vi')) return 'vi'
  return 'en'
}

export { messages }
export type { EmbedMessages }
