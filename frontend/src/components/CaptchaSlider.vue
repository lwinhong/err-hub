<template>
  <div class="captcha-slider" :class="{ 'is-success': verified, 'is-loading': loading, 'is-blocked': blocked }">
    <!-- 头部工具栏 -->
    <div class="captcha-header">
      <span class="captcha-header__title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        {{ t('captcha.title') }}
      </span>
      <button v-if="!verified && !blocked" class="captcha-refresh" @click="refresh" :disabled="loading">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" :class="{ spinning: loading }"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
      </button>
    </div>

    <!-- 图片区域 -->
    <div v-if="!blocked" class="captcha-slider__track" :style="{ width: imgWidth + 'px', height: imgHeight + 'px' }">
      <img
        v-if="bgImageSrc && !verified"
        :src="bgImageSrc"
        class="captcha-slider__bg"
        :style="{ width: imgWidth + 'px', height: imgHeight + 'px' }"
        draggable="false"
      />
      <div v-else class="captcha-loading">
        <div class="captcha-loading__spinner"></div>
      </div>
      <div
        v-if="slideImageSrc && !verified"
        class="captcha-slider__piece"
        :style="{
          left: pieceLeft + 'px',
          top: targetY + 'px',
          width: slideSize + 'px',
          height: slideSize + 'px',
          backgroundImage: `url(${slideImageSrc})`,
          backgroundSize: `${slideSize}px ${slideSize}px`
        }"
      />
      <!-- 成功提示覆盖层 -->
      <div v-if="verified" class="captcha-slider__success-overlay">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="24" height="24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        {{ t('captcha.verified') }}
      </div>
    </div>

    <!-- 滑动条 -->
    <div v-if="!verified && !blocked" class="captcha-slider__bar" :style="{ width: imgWidth + 'px' }">
      <div class="captcha-slider__track-line"></div>
      <div
        class="captcha-slider__handle"
        :style="{ left: handleLeft + 'px', cursor: cooldown > 0 ? 'not-allowed' : 'grab' }"
        @mousedown="onDragStart"
        @touchstart.prevent="onDragStart"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18"><polyline points="9 18 15 12 9 6"/></svg>
      </div>
      <div class="captcha-slider__progress" :style="{ width: (handleLeft / (barWidth - handleSize) * 100) + '%' }"></div>
      <span v-if="cooldown > 0" class="captcha-slider__text captcha-slider__text--warning">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        {{ t('captcha.cooldown', { seconds: cooldown }) }}
      </span>
      <span v-else class="captcha-slider__text">{{ t('captcha.slideToVerify') }}</span>
    </div>

    <!-- 被封锁 -->
    <div v-if="blocked" class="captcha-slider__blocked">
      <div class="blocked-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="28" height="28"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      </div>
      <span class="blocked-msg">{{ blockedMessage || t('captcha.cooldown', { seconds: blockedCountdown }) }}</span>
      <span v-if="blockedCountdown > 0" class="blocked-timer">{{ blockedCountdown }}s</span>
      <button class="blocked-retry" @click="refresh">{{ t('captcha.retry') }}</button>
    </div>

    <!-- 失败警告 -->
    <div v-if="!verified && !blocked && failCount > 0" class="captcha-slider__warning">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      {{ t('captcha.failCount', { count: failCount }) }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { generateCaptcha, verifyCaptcha } from '../api/captcha'

const { t } = useI18n()

const MAX_FAIL_COUNT = 5
const COOLDOWN_SECONDS = 10

const imgWidth = ref(320)
const imgHeight = ref(160)
const slideSize = ref(48)
const barWidth = ref(320)
const handleSize = 42

const bgImageSrc = ref('')
const slideImageSrc = ref('')
const targetY = ref(0)

const loading = ref(false)
const verified = ref(false)
const dragging = ref(false)
const startX = ref(0)
const captchaId = ref('')

const pieceLeft = ref(0)
const handleLeft = ref(0)

const failCount = ref(0)
const cooldown = ref(0)
const blocked = ref(false)
const blockedMessage = ref('')
const blockedCountdown = ref(0)
let cooldownTimer = null
let blockedCountdownTimer = null

const emit = defineEmits(['verified'])

async function loadCaptcha() {
  loading.value = true
  try {
    const res = await generateCaptcha()
    const data = res.data
    captchaId.value = data.captcha_id
    bgImageSrc.value = data.bg_image
    slideImageSrc.value = data.slide_image
    imgWidth.value = data.img_width || 320
    imgHeight.value = data.img_height || 160
    slideSize.value = data.slide_size || 48
    barWidth.value = data.img_width || 320
    targetY.value = data.target_y || 0
  } catch (err) {
    const status = err.response?.status
    if (status === 429) {
      const cooldownSec = err.response?.data?.cooldown_seconds || 60
      blocked.value = true
      blockedMessage.value = t('captcha.cooldown', { seconds: cooldownSec })
      blockedCountdown.value = cooldownSec
      startBlockedCountdown()
    }
  } finally {
    loading.value = false
  }
}

function startCooldown() {
  cooldown.value = COOLDOWN_SECONDS
  cooldownTimer = setInterval(() => {
    cooldown.value--
    if (cooldown.value <= 0) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

function startBlockedCountdown() {
  if (blockedCountdownTimer) clearInterval(blockedCountdownTimer)
  blockedCountdownTimer = setInterval(() => {
    blockedCountdown.value--
    if (blockedCountdown.value <= 0) {
      clearInterval(blockedCountdownTimer)
      blockedCountdownTimer = null
      blocked.value = false
      blockedMessage.value = ''
      refresh()
    } else {
      blockedMessage.value = t('captcha.blocked', { seconds: blockedCountdown.value })
    }
  }, 1000)
}

function onDragStart(e) {
  if (verified.value || loading.value || blocked.value || cooldown.value > 0) return
  dragging.value = true
  startX.value = e.clientX || e.touches?.[0]?.clientX || 0

  const onMove = (ev) => {
    if (!dragging.value) return
    const clientX = ev.clientX || ev.touches?.[0]?.clientX || 0
    let delta = clientX - startX.value
    delta = Math.max(0, Math.min(delta, barWidth.value - handleSize))
    handleLeft.value = delta
    pieceLeft.value = delta
  }

  const onEnd = async () => {
    dragging.value = false
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onEnd)
    document.removeEventListener('touchmove', onMove)
    document.removeEventListener('touchend', onEnd)

    if (handleLeft.value < 5) {
      resetSlider()
      return
    }

    await doVerify(handleLeft.value)
  }

  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onEnd)
  document.addEventListener('touchmove', onMove, { passive: false })
  document.addEventListener('touchend', onEnd)
}

async function doVerify(offset) {
  loading.value = true
  try {
    const res = await verifyCaptcha(captchaId.value, Math.round(offset))
    if (res.data.success) {
      verified.value = true
      setTimeout(() => {
        emit('verified', captchaId.value)
      }, 500)
    } else {
      failCount.value++
      resetSlider()

      if (failCount.value >= MAX_FAIL_COUNT) {
        startCooldown()
      }

      await loadCaptcha()
    }
  } catch (err) {
    const status = err.response?.status
    const cooldownSec = err.response?.data?.cooldown_seconds
    if (status === 429 && cooldownSec) {
      blocked.value = true
      blockedMessage.value = t('captcha.cooldown', { seconds: cooldownSec })
      blockedCountdown.value = cooldownSec
      startBlockedCountdown()
    } else {
      failCount.value++
      resetSlider()

      if (failCount.value >= MAX_FAIL_COUNT) {
        startCooldown()
      }

      await loadCaptcha()
    }
  } finally {
    loading.value = false
  }
}

function resetSlider() {
  handleLeft.value = 0
  pieceLeft.value = 0
}

function refresh() {
  resetSlider()
  verified.value = false
  failCount.value = 0
  cooldown.value = 0
  blocked.value = false
  blockedMessage.value = ''
  blockedCountdown.value = 0
  bgImageSrc.value = ''
  slideImageSrc.value = ''
  targetY.value = 0
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
    cooldownTimer = null
  }
  if (blockedCountdownTimer) {
    clearInterval(blockedCountdownTimer)
    blockedCountdownTimer = null
  }
  loadCaptcha()
}

onUnmounted(() => {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
  }
  if (blockedCountdownTimer) {
    clearInterval(blockedCountdownTimer)
  }
})

defineExpose({ refresh, verified })

onMounted(() => {
  loadCaptcha()
})
</script>

<style scoped>
.captcha-slider {
  width: 320px;
  border-radius: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  overflow: hidden;
  user-select: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

/* ── 头部 ── */
.captcha-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.captcha-header__title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.captcha-refresh {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-blank);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
  transition: all 0.2s;
}

.captcha-refresh:hover:not(:disabled) {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  background: rgba(var(--el-color-primary-rgb), 0.04);
}

.captcha-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.captcha-refresh svg.spinning {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── 图片区域 ── */
.captcha-slider__track {
  position: relative;
  overflow: hidden;
  background: var(--el-fill-color-light);
}

.captcha-slider__bg {
  display: block;
  pointer-events: none;
}

.captcha-loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.captcha-loading__spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--el-border-color-lighter);
  border-top-color: var(--el-color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.captcha-slider__piece {
  position: absolute;
  top: 0;
  background-repeat: no-repeat;
  pointer-events: none;
  z-index: 2;
  filter: drop-shadow(1px 1px 3px rgba(0, 0, 0, 0.3));
  border-radius: 4px;
}

/* ── 滑动条 ── */
.captcha-slider__bar {
  position: relative;
  height: 48px;
  background: var(--el-fill-color-light);
  border-top: 1px solid var(--el-border-color-lighter);
}

.captcha-slider__track-line {
  position: absolute;
  top: 50%;
  left: 16px;
  right: 16px;
  height: 2px;
  background: var(--el-border-color-lighter);
  border-radius: 1px;
  transform: translateY(-50%);
}

.captcha-slider__progress {
  position: absolute;
  top: 50%;
  left: 16px;
  height: 2px;
  background: var(--el-color-primary);
  border-radius: 1px;
  transform: translateY(-50%);
  transition: width 0.05s;
  opacity: 0.4;
}

.captcha-slider__handle {
  position: absolute;
  top: 50%;
  left: 0;
  width: 42px;
  height: 38px;
  margin-top: -19px;
  background: linear-gradient(135deg, var(--el-color-primary), var(--el-color-primary-light-3));
  border-radius: 10px;
  cursor: grab;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 2px 8px rgba(var(--el-color-primary-rgb), 0.3);
  transition: box-shadow 0.2s, transform 0.1s;
}

.captcha-slider__handle:hover {
  box-shadow: 0 4px 16px rgba(var(--el-color-primary-rgb), 0.4);
}

.captcha-slider__handle:active {
  cursor: grabbing;
  transform: scale(1.05);
}

.captcha-slider__text {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--el-text-color-placeholder);
  font-size: 13px;
  pointer-events: none;
}

.captcha-slider__text--warning {
  color: var(--el-color-danger);
  font-weight: 600;
}

/* ── 警告 ── */
.captcha-slider__warning {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(239, 68, 68, 0.06);
  border-top: 1px solid rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-size: 12px;
  font-weight: 500;
}

/* ── 被封锁 ── */
.captcha-slider__blocked {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 24px 16px;
  background: rgba(239, 68, 68, 0.04);
  color: #ef4444;
  font-size: 13px;
  font-weight: 500;
}

.blocked-msg {
  text-align: center;
  line-height: 1.4;
}

.blocked-timer {
  font-size: 24px;
  font-weight: 700;
  color: #ef4444;
  font-variant-numeric: tabular-nums;
}

.blocked-retry {
  padding: 6px 16px;
  border-radius: 8px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  background: rgba(239, 68, 68, 0.06);
  color: #ef4444;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 4px;
}

.blocked-retry:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

/* ── 成功 ── */
.captcha-slider__success {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #22c55e;
  font-size: 14px;
  font-weight: 600;
  background: rgba(34, 197, 94, 0.06);
  border-top: 1px solid rgba(34, 197, 94, 0.1);
}

/* ── 状态样式 ── */
.captcha-slider.is-loading .captcha-slider__handle {
  opacity: 0.6;
  cursor: not-allowed;
}

.captcha-slider.is-success {
  border-color: rgba(34, 197, 94, 0.3);
}

.captcha-slider.is-blocked {
  border-color: rgba(239, 68, 68, 0.3);
}
.captcha-slider__success-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(34, 197, 94, 0.9);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  z-index: 10;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
