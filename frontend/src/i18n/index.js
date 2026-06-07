import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import en from './locales/en'

const STORAGE_KEY = 'locale'

// 可用语言列表，新增语言只需在此追加即可，无需修改组件
export const languages = [
  { code: 'zh-CN', label: '中文' },
  { code: 'en', label: 'English' },
]

// 语言检测映射：浏览器语言前缀 → i18n code
const langMap = {
  zh: 'zh-CN',
  en: 'en',
}

function detectLocale() {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored && languages.some(l => l.code === stored)) return stored
  const browserLang = navigator.language || ''
  const prefix = browserLang.split('-')[0].toLowerCase()
  return langMap[prefix] || 'en'
}

const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: 'en',
  messages: {
    'zh-CN': zhCN,
    en,
  },
})

export default i18n
export { STORAGE_KEY }
