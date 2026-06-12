<template>
  <div class="captcha-slider" :class="{ 'is-success': verified, 'is-loading': loading, 'is-blocked': blocked }">
    <div v-if="!verified && !blocked" class="captcha-slider__track" :style="{ width: imgWidth + 'px', height: imgHeight + 'px' }">
      <img
        v-if="bgImageSrc"
        :src="bgImageSrc"
        class="captcha-slider__bg"
        :style="{ width: imgWidth + 'px', height: imgHeight + 'px' }"
        draggable="false"
      />
      <div
        v-if="slideImageSrc"
        class="captcha-slider__piece"
        :style="{
          left: pieceLeft + 'px',
          width: slideSize + 'px',
          height: imgHeight + 'px',
          backgroundImage: `url(${slideImageSrc})`,
          backgroundSize: `${slideSize}px ${imgHeight}px`
        }"
      />
    </div>
    <div v-if="!verified && !blocked" class="captcha-slider__bar" :style="{ width: imgWidth + 'px' }">
      <div
        class="captcha-slider__handle"
        :style="{ left: handleLeft + 'px', cursor: cooldown > 0 ? 'not-allowed' : 'grab' }"
        @mousedown="onDragStart"
        @touchstart.prevent="onDragStart"
      />
      <span v-if="cooldown > 0" class="captcha-slider__text captcha-slider__text--warning">
        {{ t('captcha.cooldown', { seconds: cooldown }) }}
      </span>
      <span v-else class="captcha-slider__text">{{ t('captcha.slideToVerify') }}</span>
    </div>
    <div v-if="blocked" class="captcha-slider__blocked">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <span>{{ t('captcha.blocked') }}</span>
    </div>
    <div v-if="verified" class="captcha-slider__success" :style="{ width: imgWidth + 'px' }">
      {{ t('captcha.verified') }}
    </div>
    <div v-if="!verified && !blocked && failCount > 0" class="captcha-slider__warning">
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
const BLOCK_AFTER_FAILS = 10

const imgWidth = ref(320)
const imgHeight = ref(160)
const slideSize = ref(48)
const barWidth = ref(320)
const handleSize = 42

const bgImageSrc = ref('')
const slideImageSrc = ref('')

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
let cooldownTimer = null

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
    loading.value = false
  } catch {
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
      emit('verified', captchaId.value)
    } else {
      failCount.value++
      resetSlider()

      if (failCount.value >= BLOCK_AFTER_FAILS) {
        blocked.value = true
      } else if (failCount.value >= MAX_FAIL_COUNT) {
        startCooldown()
      }

      await loadCaptcha()
    }
  } catch {
    failCount.value++
    resetSlider()

    if (failCount.value >= BLOCK_AFTER_FAILS) {
      blocked.value = true
    } else if (failCount.value >= MAX_FAIL_COUNT) {
      startCooldown()
    }

    await loadCaptcha()
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
  bgImageSrc.value = ''
  slideImageSrc.value = ''
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
    cooldownTimer = null
  }
  loadCaptcha()
}

onUnmounted(() => {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
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
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  background: var(--el-fill-color-light);
  user-select: none;
}

.captcha-slider__track {
  position: relative;
  overflow: hidden;
  border-radius: 6px 6px 0 0;
}

.captcha-slider__bg {
  display: block;
  pointer-events: none;
}

.captcha-slider__piece {
  position: absolute;
  top: 0;
  background-repeat: no-repeat;
  pointer-events: none;
  z-index: 2;
  filter: drop-shadow(1px 1px 2px rgba(0, 0, 0, 0.3));
}

.captcha-slider__bar {
  position: relative;
  height: 44px;
  background: var(--el-fill-color-blank);
  border-top: 1px solid var(--el-border-color-lighter);
  border-radius: 0 0 6px 6px;
}

.captcha-slider__handle {
  position: absolute;
  top: 3px;
  left: 0;
  width: 42px;
  height: 38px;
  background: var(--el-color-primary);
  border-radius: 4px;
  cursor: grab;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.captcha-slider__handle:hover {
  background: var(--el-color-primary-light-3);
}

.captcha-slider__handle:active {
  cursor: grabbing;
}

.captcha-slider__handle::after {
  content: '';
  width: 14px;
  height: 14px;
  border-right: 2px solid #fff;
  border-bottom: 2px solid #fff;
  transform: rotate(-45deg);
  margin-left: -2px;
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
  color: var(--el-text-color-placeholder);
  font-size: 13px;
  pointer-events: none;
}

.captcha-slider__text--warning {
  color: var(--el-color-danger);
  font-weight: 500;
}

.captcha-slider__warning {
  padding: 6px 12px;
  background: #fef2f2;
  border-top: 1px solid #fecaca;
  color: #dc2626;
  font-size: 12px;
  border-radius: 0 0 6px 6px;
}

.captcha-slider__blocked {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 88px;
  background: #fef2f2;
  color: #dc2626;
  font-size: 13px;
  font-weight: 500;
  border-radius: 0 0 6px 6px;
}

.captcha-slider__blocked svg {
  width: 20px;
  height: 20px;
}

.captcha-slider__success {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-success);
  font-size: 13px;
  font-weight: 500;
  background: var(--el-color-success-light-9);
  border-radius: 0 0 6px 6px;
}

.captcha-slider.is-loading .captcha-slider__handle {
  opacity: 0.6;
  cursor: not-allowed;
}

.captcha-slider.is-success {
  border-color: var(--el-color-success);
}

.captcha-slider.is-blocked {
  border-color: var(--el-color-danger);
}
</style>
