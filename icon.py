from PIL import Image, ImageDraw


def create_icon(size: int = 64, dark: bool = False) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    for y in range(size):
        t = y / size
        r = int(255 * (1 - t) + 230 * t)
        g = int(59 * (1 - t) + 69 * t)
        b = int(48 * (1 - t) + 130 * t)
        for x in range(size):
            dx = x - size / 2
            dy = y - size / 2
            if dx * dx + dy * dy <= (size / 2) ** 2:
                img.putpixel((x, y), (r, g, b, 255))

    draw = ImageDraw.Draw(img)
    stroke_color = (255, 255, 255, 240)
    stroke_width = max(2, size // 20)
    center_y = size / 2
    amplitude = size / 5
    points = []

    for x in range(size):
        t = x / size
        y = center_y
        if 0.35 < t < 0.65:
            local = (t - 0.35) / 0.3
            if local < 0.25:
                y = center_y + amplitude * 0.4 * (local / 0.25)
            elif local < 0.4:
                y = center_y - amplitude * 1.2 * ((local - 0.25) / 0.15)
            elif local < 0.55:
                y = center_y + amplitude * 0.8 * ((local - 0.4) / 0.15)
            elif local < 0.75:
                y = center_y - amplitude * 0.3 * ((local - 0.55) / 0.2)
            else:
                y = center_y + amplitude * 0.3 * (1 - (local - 0.75) / 0.25)
        points.append((x, y))

    draw.line(points, fill=stroke_color, width=stroke_width, joint="curve")
    return img


def create_tray_icon() -> Image.Image:
    return create_icon(64)