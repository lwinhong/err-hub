from flask import Blueprint, request, jsonify, current_app

from app.models.setting import SystemSetting
from app.services.captcha import generate_captcha, verify_captcha, CAPTCHA_TTL

bp = Blueprint('captcha_v1', __name__, url_prefix='/api/v1/captcha')

CAPTCHA_STORE_PREFIX = 'captcha:'
FAIL_COUNT_PREFIX = 'captcha_fails:'


def _get_setting_int(key, default):
    val = SystemSetting.get_value(key)
    if val is not None:
        try:
            return int(val)
        except (ValueError, TypeError):
            pass
    return default


def _get_max_fails():
    return _get_setting_int('captcha_max_fails', 10)


def _get_lock_duration():
    return _get_setting_int('captcha_lock_duration', 300)


def _get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr


@bp.route('/generate', methods=['GET'])
def generate():
    ip = _get_client_ip()
    captcha_data = generate_captcha()
    captcha_id = captcha_data["captcha_id"]
    current_app.redis.set(
        f"{CAPTCHA_STORE_PREFIX}{captcha_id}",
        captcha_data["token"],
        ex=CAPTCHA_TTL,
    )
    return jsonify({
        "bg_image": captcha_data["bg_image"],
        "slide_image": captcha_data["slide_image"],
        "captcha_id": captcha_id,
        "expire": captcha_data["expire"],
        "slide_size": captcha_data["slide_size"],
        "img_width": captcha_data["img_width"],
        "img_height": captcha_data["img_height"],
        "target_y": captcha_data["target_y"],
    })


@bp.route('/verify', methods=['POST'])
def verify():
    ip = _get_client_ip()
    max_fails = _get_max_fails()
    lock_duration = _get_lock_duration()

    data = request.get_json()
    if not data or not data.get("captcha_id") or data.get("offset") is None:
        return jsonify({"error": "captcha_id and offset are required"}), 400

    captcha_id = data["captcha_id"]
    offset = int(data["offset"])

    store_key = f"{CAPTCHA_STORE_PREFIX}{captcha_id}"
    token = current_app.redis.get(store_key)
    if not token:
        return jsonify({"error": "Captcha expired or invalid", "success": False}), 400

    current_app.redis.delete(store_key)

    success = verify_captcha(token, offset)
    if not success:
        fail_key = f"{FAIL_COUNT_PREFIX}{ip}"
        fail_count = current_app.redis.incr(fail_key)
        current_app.redis.expire(fail_key, lock_duration)

        if fail_count >= max_fails:
            cooldown_seconds = lock_duration
            return jsonify({
                "success": False,
                "error": "Too many failed attempts, please try again later",
                "cooldown_seconds": cooldown_seconds,
            }), 429

        return jsonify({"success": False, "error": "Verification failed"}), 400

    current_app.redis.delete(f"{FAIL_COUNT_PREFIX}{ip}")

    current_app.redis.set(
        f"captcha_verified:{captcha_id}",
        "1",
        ex=CAPTCHA_TTL,
    )

    return jsonify({"success": True, "captcha_id": captcha_id})


@bp.route('/status', methods=['GET'])
def status():
    ip = _get_client_ip()
    fail_count = 0
    fail_val = current_app.redis.get(f"{FAIL_COUNT_PREFIX}{ip}")
    if fail_val:
        fail_count = int(fail_val)
    return jsonify({
        "fail_count": fail_count,
        "max_fails": _get_max_fails(),
    })
