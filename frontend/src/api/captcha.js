import request from './index'

export function generateCaptcha() {
  return request.get('captcha/generate')
}

export function verifyCaptcha(captcha_id, offset) {
  return request.post('captcha/verify', { captcha_id, offset })
}
