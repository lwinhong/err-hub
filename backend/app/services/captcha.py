import io
import json
import random
import string
import time
import base64
from hashlib import md5

from PIL import Image, ImageDraw, ImageFont, ImageFilter


CAPTCHA_WIDTH = 320
CAPTCHA_HEIGHT = 160
SLIDE_SIZE = 48
CAPTCHA_TTL = 120
SLIDE_TOLERANCE = 8


def _random_color(low=0, high=255):
    return tuple(random.randint(low, high) for _ in range(3))


def _generate_noise(draw, width, height):
    for _ in range(80):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=_random_color(64, 200))


def _generate_lines(draw, width, height):
    for _ in range(6):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=_random_color(64, 200), width=2)


def _draw_slide_slot(draw, x, y, size):
    draw.rounded_rectangle(
        [(x, y), (x + size, y + size)],
        radius=size // 4,
        fill=(0, 0, 0),
    )


def generate_captcha():
    bg_color = _random_color(200, 240)
    bg = Image.new('RGB', (CAPTCHA_WIDTH, CAPTCHA_HEIGHT), bg_color)
    draw = ImageDraw.Draw(bg)

    _generate_noise(draw, CAPTCHA_WIDTH, CAPTCHA_HEIGHT)
    _generate_lines(draw, CAPTCHA_WIDTH, CAPTCHA_HEIGHT)

    target_x = random.randint(80, CAPTCHA_WIDTH - SLIDE_SIZE - 20)
    target_y = (CAPTCHA_HEIGHT - SLIDE_SIZE) // 2

    _draw_slide_slot(draw, target_x, target_y, SLIDE_SIZE)

    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        font = ImageFont.load_default()

    text = ''.join(random.choices(string.ascii_uppercase, k=4))
    text_color = _random_color(100, 180)
    for i, ch in enumerate(text):
        tx = 20 + i * 40
        ty = random.randint(40, CAPTCHA_HEIGHT - 50)
        draw.text((tx, ty), ch, fill=text_color, font=font)

    bg = bg.filter(ImageFilter.SMOOTH)

    token_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    ts = int(time.time())
    token_payload = json.dumps({"k": token_key, "o": target_x, "t": ts})

    bg_buf = io.BytesIO()
    bg.save(bg_buf, format='PNG')
    bg_b64 = base64.b64encode(bg_buf.getvalue()).decode()

    slide = Image.new('RGBA', (SLIDE_SIZE, CAPTCHA_HEIGHT), (0, 0, 0, 0))
    slide_draw = ImageDraw.Draw(slide)
    slide_draw.rounded_rectangle(
        [(0, target_y), (SLIDE_SIZE, target_y + SLIDE_SIZE)],
        radius=SLIDE_SIZE // 4,
        fill=(100, 100, 100, 200),
        outline=(255, 255, 255, 255),
        width=2,
    )
    slide_buf = io.BytesIO()
    slide.save(slide_buf, format='PNG')
    slide_b64 = base64.b64encode(slide_buf.getvalue()).decode()

    return {
        "bg_image": f"data:image/png;base64,{bg_b64}",
        "slide_image": f"data:image/png;base64,{slide_b64}",
        "token": token_payload,
        "captcha_id": token_key,
        "expire": CAPTCHA_TTL,
        "slide_size": SLIDE_SIZE,
        "img_width": CAPTCHA_WIDTH,
        "img_height": CAPTCHA_HEIGHT,
    }


def verify_captcha(token_payload, offset_x):
    try:
        data = json.loads(token_payload)
        target = data["o"]
        ts = data["t"]
    except (json.JSONDecodeError, KeyError):
        return False

    if time.time() - ts > CAPTCHA_TTL:
        return False

    return abs(offset_x - target) <= SLIDE_TOLERANCE
