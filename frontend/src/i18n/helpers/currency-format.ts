/**
 * Currency formatting helpers for Wind Motion.
 * Supports locale-aware number/currency display across 7 languages.
 */

export type SupportedLocale =
  | 'zh-CN'
  | 'zh-TW'
  | 'en'
  | 'th'
  | 'ko'
  | 'ja'
  | 'vi'

const localeMap: Record<SupportedLocale, string> = {
  'zh-CN': 'zh-CN',
  'zh-TW': 'zh-TW',
  en: 'en-US',
  th: 'th-TH',
  ko: 'ko-KR',
  ja: 'ja-JP',
  vi: 'vi-VN',
}

/**
 * Format a number as USD currency string.
 * Examples: $1,234.56 / ¥1,234 / ₩1,234
 */
export function formatCurrency(
  value: number,
  locale: SupportedLocale = 'en',
  currency: string = 'USD',
  compact: boolean = false
): string {
  const resolved = localeMap[locale] || 'en-US'

  const options: Intl.NumberFormatOptions = {
    style: 'currency',
    currency,
    minimumFractionDigits: compact ? 0 : 2,
    maximumFractionDigits: compact ? 0 : 2,
  }

  if (compact) {
    options.notation = 'compact'
    options.compactDisplay = 'short'
  }

  try {
    return new Intl.NumberFormat(resolved, options).format(value)
  } catch {
    // Fallback for unsupported locale/currency
    return `$${formatNumber(value, locale, compact)}`
  }
}

/**
 * Format a plain number with locale-aware separators.
 */
export function formatNumber(
  value: number,
  locale: SupportedLocale = 'en',
  compact: boolean = false
): string {
  const resolved = localeMap[locale] || 'en-US'

  const options: Intl.NumberFormatOptions = {
    minimumFractionDigits: 0,
    maximumFractionDigits: compact ? 1 : 2,
  }

  if (compact) {
    options.notation = 'compact'
    options.compactDisplay = 'short'
  }

  try {
    return new Intl.NumberFormat(resolved, options).format(value)
  } catch {
    return value.toLocaleString()
  }
}

/**
 * Format a percentage value.
 * Examples: 66.5% / 66.5 %
 */
export function formatPercent(
  value: number,
  locale: SupportedLocale = 'en',
  decimals: number = 1
): string {
  const resolved = localeMap[locale] || 'en-US'

  try {
    return new Intl.NumberFormat(resolved, {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value / 100)
  } catch {
    return `${value.toFixed(decimals)}%`
  }
}

/**
 * Format a crypto amount with appropriate precision.
 * Small amounts get more decimals, large amounts get fewer.
 */
export function formatCrypto(
  value: number,
  symbol: string = '',
  locale: SupportedLocale = 'en'
): string {
  let decimals = 2
  if (Math.abs(value) < 0.01) decimals = 6
  else if (Math.abs(value) < 1) decimals = 4
  else if (Math.abs(value) >= 1000000) decimals = 0

  const formatted = formatNumber(value, locale)
  return symbol ? `${formatted} ${symbol}` : formatted
}

/**
 * Format ROI multiplier.
 * Examples: 3.4x / 0.8x / -1.2x
 */
export function formatROI(value: number): string {
  return `${value.toFixed(1)}x`
}

/**
 * Format large USD values in compact notation.
 * Examples: $2.3M / $500K / $1.2B
 */
export function formatCompactUSD(
  value: number,
  locale: SupportedLocale = 'en'
): string {
  return formatCurrency(value, locale, 'USD', true)
}
