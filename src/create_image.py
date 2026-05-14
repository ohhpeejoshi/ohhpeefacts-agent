import os
import logging
import textwrap
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

COLOR_SCHEMES = {
    "dark": {"bg": (13, 13, 13), "text": (255, 255, 255), "accent": (155, 89, 182), "secondary": (204, 204, 204)},
    "vibrant": {"bg": (26, 26, 46), "text": (255, 255, 255), "accent": (0, 201, 255), "secondary": (170, 170, 255)},
    "minimal": {"bg": (245, 245, 245), "text": (26, 26, 26), "accent": (45, 52, 54), "secondary": (85, 85, 85)},
    "cosmic": {"bg": (10, 10, 46), "text": (255, 255, 255), "accent": (0, 210, 255), "secondary": (170, 170, 255)},
    "earthy": {"bg": (45, 74, 34), "text": (245, 245, 220), "accent": (200, 169, 81), "secondary": (212, 197, 160)}
}

def apply_opacity(color: Tuple[int, int, int], opacity_percent: int) -> Tuple[int, int, int, int]:
    return (*color, int(255 * (opacity_percent / 100.0)))

def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception as e:
        logger.warning(f"Could not load font {path}. Using default. Error: {e}")
        return ImageFont.load_default()

def draw_radial_bg(img: Image.Image, bg_color: Tuple[int, int, int]):
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([0, 0, 1080, 1080], fill=(*bg_color, 255))
    steps = 20
    for i in range(steps):
        factor = 1.0 + ((i + 1) * 0.02)
        r = min(255, max(5, int(bg_color[0] * factor)))
        g = min(255, max(5, int(bg_color[1] * factor)))
        b = min(255, max(5, int(bg_color[2] * factor)))
        
        shrink = i * 20
        bbox = [shrink, shrink, 1080 - shrink, 1080 - shrink]
        draw.rounded_rectangle(bbox, radius=100, fill=(r, g, b, 255))

def create_instagram_image(content: Dict[str, str], output_dir: str = "output") -> str:
    """
    Creates the Instagram image given the fact content.
    Returns the file path of the saved image.
    """
    mood = content.get("image_mood", "dark").lower()
    if mood not in COLOR_SCHEMES:
        mood = "dark"
    scheme = COLOR_SCHEMES[mood]
    
    # Layer 1: Background
    img = Image.new("RGBA", (1080, 1080), (*scheme["bg"], 255))
    draw_radial_bg(img, scheme["bg"])
    
    # Layer 2: Logo Watermark
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    logo_path_png = os.path.join(assets_dir, "logo.png")
    logo_path_jpg = os.path.join(assets_dir, "logo.jpg")
    
    logo_path = logo_path_png if os.path.exists(logo_path_png) else (logo_path_jpg if os.path.exists(logo_path_jpg) else None)
    
    if logo_path:
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # Resize within 700x700
            logo.thumbnail((700, 700), Image.Resampling.LANCZOS)
            
            # Apply 35/255 opacity
            r, g, b, a = logo.split()
            a = a.point(lambda x: int(x * (35 / 255.0)))
            logo = Image.merge("RGBA", (r, g, b, a))
            
            x = (1080 - logo.width) // 2
            y = (1080 - logo.height) // 2
            img.alpha_composite(logo, (x, y))
        except Exception as e:
            logger.warning(f"Failed to load or composite logo: {e}")
    else:
        logger.warning("Logo file not found in assets. Skipping watermark.")

    draw = ImageDraw.Draw(img, "RGBA")
    font_bold_path = os.path.join(assets_dir, "font_bold.ttf")
    font_regular_path = os.path.join(assets_dir, "font_regular.ttf")
    
    # Layer 4 (Top): Topic Label
    topic_text = f"🔬 {content.get('topic', 'FACT').upper()}"
    topic_font = get_font(font_bold_path, 32)
    # Using textbbox to center text
    bbox = draw.textbbox((0, 0), topic_text, font=topic_font)
    tw = bbox[2] - bbox[0]
    draw.text(((1080 - tw) / 2, 90), topic_text, font=topic_font, fill=(*scheme["accent"], 255))
    
    # Thin line below topic
    line_y = 145
    line_w = 180
    line_color = apply_opacity(scheme["accent"], 50)
    draw.line([(1080 - line_w) / 2, line_y, (1080 + line_w) / 2, line_y], fill=line_color, width=2)
    
    # Text scaling and wrapping logic
    fact_text = content.get("image_text", "")
    font_size = 68
    max_width = 1080 - 200 # 880px max width
    
    wrapped_lines = []
    final_font = None
    
    while font_size >= 20:
        final_font = get_font(font_bold_path, font_size)
        
        # Word wrap: max 22 characters per line
        wrapper = textwrap.TextWrapper(width=22)
        lines = wrapper.wrap(fact_text)
        
        if len(lines) > 5:
            font_size -= 4
            continue
            
        # Check pixel width
        too_wide = False
        for line in lines:
            line_bbox = draw.textbbox((0, 0), line, font=final_font)
            line_w = line_bbox[2] - line_bbox[0]
            if line_w > max_width:
                too_wide = True
                break
                
        if too_wide:
            font_size -= 4
        else:
            wrapped_lines = lines
            break
            
    if not wrapped_lines:
        wrapped_lines = textwrap.wrap(fact_text, width=22)[:5]
        final_font = get_font(font_bold_path, 30)

    # Draw Text and Drop Shadow (Layer 3 and 4)
    # Vertically centre text block between y=300 and y=780
    line_height = font_size * 1.2
    total_text_height = len(wrapped_lines) * line_height
    start_y = 300 + ((780 - 300) - total_text_height) / 2
    
    shadow_color = (0, 0, 0, int(255 * 0.40)) # 40% opacity black
    
    for i, line in enumerate(wrapped_lines):
        line_bbox = draw.textbbox((0, 0), line, font=final_font)
        line_w = line_bbox[2] - line_bbox[0]
        x = (1080 - line_w) / 2
        y = start_y + (i * line_height)
        
        # Drop shadow
        draw.text((x + 3, y + 3), line, font=final_font, fill=shadow_color)
        
        # Actual text
        draw.text((x, y), line, font=final_font, fill=(*scheme["text"], 255))
        
    # Bottom Branding Bar
    branding_line_color = apply_opacity(scheme["text"], 25)
    padding = 80
    draw.line([padding, 900, 1080 - padding, 900], fill=branding_line_color, width=1)
    
    branding_text = "A fact a day  •  @ohhpeefacts"
    branding_font = get_font(font_regular_path, 28)
    bbox = draw.textbbox((0, 0), branding_text, font=branding_font)
    bw = bbox[2] - bbox[0]
    
    branding_color = apply_opacity(scheme["secondary"], 65)
    draw.text(((1080 - bw) / 2, 920), branding_text, font=branding_font, fill=branding_color)
    
    # Save Image
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    out_path = os.path.join(output_dir, f"ohhpeefacts_{date_str}.jpg")
    
    final_img = img.convert("RGB")
    final_img.save(out_path, "JPEG", quality=95)
    
    return out_path
