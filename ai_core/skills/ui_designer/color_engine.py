import colorsys
import math

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def adjust_lightness(hex_color, factor):
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
    
    # 调整亮度 (0.0 - 1.0)
    new_l = max(0.0, min(1.0, l * factor))
    
    r, g, b = colorsys.hls_to_rgb(h, new_l, s)
    return rgb_to_hex((r*255, g*255, b*255))

def generate_palette(base_color):
    """
    基于主色生成 Tailwind 风格的 50-900 色阶
    这比让 LLM 瞎猜颜色要科学、精准得多。
    """
    scales = {
        '50': 1.9, '100': 1.8, '200': 1.6, '300': 1.4, '400': 1.2,
        '500': 1.0, # Base
        '600': 0.9, '700': 0.75, '800': 0.6, '900': 0.45
    }
    
    palette = {}
    for name, factor in scales.items():
        palette[name] = adjust_lightness(base_color, factor)
        
    return palette

def generate_design_tokens(brand_color):
    """生成的不仅是颜色，而是完整的 Design Token JSON"""
    palette = generate_palette(brand_color)
    
    return {
        "colors": {
            "primary": palette,
            "semantic": {
                "success": "#10B981", # 标准开源色值
                "warning": "#F59E0B",
                "error": "#EF4444"
            }
        },
        "spacing": {
            "4": "1rem",
            "8": "2rem"
        },
        "borderRadius": {
            "sm": "0.125rem",
            "md": "0.375rem",
            "lg": "0.5rem"
        }
    }
