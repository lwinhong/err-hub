/**
 * 将后端返回的 UTC 时间字符串转换为本地时间显示。
 * 后端 isoformat() 输出的是无时区后缀的字符串（如 "2024-01-15T10:30:00"），
 * 需要追加 'Z' 标记为 UTC，再由 Date 自动转换为本地时间。
 */
export const formatTime = (t) => {
  if (!t) return '-'
  const locale = localStorage.getItem('locale') === 'en' ? 'en-US' : 'zh-CN'
  // 如果已有时区信息（Z / +08:00），直接解析
  if (t.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(t)) {
    return new Date(t).toLocaleString(locale)
  }
  // 无时区信息，视为 UTC
  return new Date(t + 'Z').toLocaleString(locale)
}
