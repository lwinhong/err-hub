from flask import Blueprint, request, jsonify, current_app

from app.services.captcha import generate_captcha, verify_captcha, CAPTCHA_TTL

bp = Blueprint('captcha_v1', __name__, url_prefix='/api/v1/captcha')

CAPTCHA_STORE_PREFIX = 'captcha:'
FAIL_COUNT_PREFIX = 'captcha_fails:'
BLOCK_PREFIX = 'captcha_block:'
MAX_FAILS = 10
BLOCK_TTL = 300


def _get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr


@bp.route('/generate', methods=['GET'])
def generate():
    ip = _get_client_ip()
    if current_app.redis.get(f"{BLOCK_PREFIX}{ip}"):
        return jsonify({"error": "Too many failed attempts, please try again later"}), 429

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
    })


@bp.route('/verify', methods=['POST'])
def verify():
    ip = _get_client_ip()
    if current_app.redis.get(f"{BLOCK_PREFIX}{ip}"):
        return jsonify({"error": "Too many failed attempts, please try again later", "success": False}), 429

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
        current_app.redis.expire(fail_key, BLOCK_TTL)

        if fail_count >= MAX_FAILS:
            current_app.redis.set(f"{BLOCK_PREFIX}{ip}", "1", ex=BLOCK_TTL)
            return jsonify({"success": False, "error": "Too many failed attempts, blocked"}), 429

        return jsonify({"success": False, "error": "Verification failed"}), 400

    current_app.redis.delete(f"{FAIL_COUNT_PREFIX}{ip}")

    current_app.redis.set(
        f"captcha_verified:{captcha_id}",
        "1",
        ex=CAPTCHA_TTL,
    )

    return jsonify({"success": True, "captcha_id": captcha_id})
