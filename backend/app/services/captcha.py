import io
import json
import math
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
SSAA = 2


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


TARGET_SHAPES = ['rectangle', 'circle', 'diamond', 'triangle', 'hexagon', 'star']


def _draw_shape(draw, cx, cy, size, shape_type, fill_color, outline_color=None, outline_width=2):
    """Draw a shape at (cx, cy) with given size. cx, cy is the center."""
    r = size // 2 - 2
    if shape_type == 'rectangle':
        x1, y1 = cx - r, cy - r
        x2, y2 = cx + r, cy + r
        draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=size // 6, fill=fill_color, outline=outline_color, width=outline_width)
    elif shape_type == 'circle':
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill_color, outline=outline_color, width=outline_width)
    elif shape_type == 'diamond':
        points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        draw.polygon(points, fill=fill_color, outline=outline_color)
    elif shape_type == 'triangle':
        points = [(cx, cy - r), (cx + r, cy + r), (cx - r, cy + r)]
        draw.polygon(points, fill=fill_color, outline=outline_color)
    elif shape_type == 'hexagon':
        points = [(cx + int(r * math.cos(math.radians(60 * i - 30))),
                    cy + int(r * math.sin(math.radians(60 * i - 30)))) for i in range(6)]
        draw.polygon(points, fill=fill_color, outline=outline_color)
    elif shape_type == 'star':
        outer_r = r
        inner_r = r // 2
        points = []
        for i in range(10):
            angle = math.radians(36 * i - 90)
            radius = outer_r if i % 2 == 0 else inner_r
            points.append((cx + int(radius * math.cos(angle)), cy + int(radius * math.sin(angle))))
        draw.polygon(points, fill=fill_color, outline=outline_color)


def _draw_decoy_shapes(draw, width, height, slide_size, target_x, target_y, count=4):
    """Draw decoy shapes to increase difficulty for automated programs."""
    decoy_shapes = ['circle', 'diamond', 'triangle', 'hexagon', 'star']
    for _ in range(count):
        shape_type = random.choice(decoy_shapes)
        sx = random.randint(20, width - slide_size - 20)
        sy = random.randint(10, height - slide_size - 10)

        if abs(sx - target_x) < slide_size + 10 and abs(sy - target_y) < slide_size + 10:
            continue

        color = _random_color(120, 220)
        outline_color = _random_color(60, 150)
        cx = sx + slide_size // 2
        cy = sy + slide_size // 2
        _draw_shape(draw, cx, cy, slide_size, shape_type, color, outline_color)


def generate_captcha():
    bg_color = _random_color(200, 240)
    bg = Image.new('RGB', (CAPTCHA_WIDTH * SSAA, CAPTCHA_HEIGHT * SSAA), bg_color)
    draw = ImageDraw.Draw(bg)

    _generate_noise(draw, CAPTCHA_WIDTH * SSAA, CAPTCHA_HEIGHT * SSAA)
    _generate_lines(draw, CAPTCHA_WIDTH * SSAA, CAPTCHA_HEIGHT * SSAA)

    target_x = random.randint(80, CAPTCHA_WIDTH - SLIDE_SIZE - 20)
    target_y = random.randint(10, CAPTCHA_HEIGHT - SLIDE_SIZE - 10)

    _draw_decoy_shapes(draw, CAPTCHA_WIDTH * SSAA, CAPTCHA_HEIGHT * SSAA, SLIDE_SIZE * SSAA, target_x * SSAA, target_y * SSAA, count=4)

    target_shape = random.choice(TARGET_SHAPES)
    target_cx = (target_x + SLIDE_SIZE // 2) * SSAA
    target_cy = (target_y + SLIDE_SIZE // 2) * SSAA
    _draw_shape(draw, target_cx, target_cy, SLIDE_SIZE * SSAA, target_shape, (0, 0, 0))

    try:
        font = ImageFont.truetype("arial.ttf", 30 * SSAA)
    except OSError:
        font = ImageFont.load_default()

    text = ''.join(random.choices(string.ascii_uppercase, k=4))
    text_color = _random_color(100, 180)
    for i, ch in enumerate(text):
        tx = (20 + i * 40) * SSAA
        ty = random.randint(40 * SSAA, CAPTCHA_HEIGHT * SSAA - 50 * SSAA)
        draw.text((tx, ty), ch, fill=text_color, font=font)

    bg = bg.resize((CAPTCHA_WIDTH, CAPTCHA_HEIGHT), Image.LANCZOS)

    token_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    ts = int(time.time())
    token_payload = json.dumps({"k": token_key, "o": target_x, "y": target_y, "t": ts})

    bg_buf = io.BytesIO()
    bg.save(bg_buf, format='PNG')
    bg_b64 = base64.b64encode(bg_buf.getvalue()).decode()

    slide = Image.new('RGBA', (SLIDE_SIZE * SSAA, SLIDE_SIZE * SSAA), (0, 0, 0, 0))
    slide_draw = ImageDraw.Draw(slide)
    slide_cx = SLIDE_SIZE * SSAA // 2
    slide_cy = SLIDE_SIZE * SSAA // 2
    _draw_shape(slide_draw, slide_cx, slide_cy, SLIDE_SIZE * SSAA, target_shape, (100, 100, 100, 200), (255, 255, 255, 255))
    slide = slide.resize((SLIDE_SIZE, SLIDE_SIZE), Image.LANCZOS)
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
        "target_y": target_y,
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
