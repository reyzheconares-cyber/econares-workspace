#!/usr/bin/env python3
"""
Thermal Coal Infographic - ECONARES Dashboard
Corporate Memphis style, 16:9 landscape
"""
from PIL import Image, ImageDraw, ImageFont
import os

WIDTH, HEIGHT = 1920, 1080
COLORS = {
    'bg_dark': '#1a2634',
    'bg_card': '#243447',
    'primary': '#4ecdc4',
    'secondary': '#ff6b6b',
    'tertiary': '#ffe66d',
    'quaternary': '#95e1d3',
    'text_white': '#ffffff',
    'text_gray': '#a0aec0',
    'accent_blue': '#5a7d9a',
}

img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['bg_dark'])
draw = ImageDraw.Draw(img)

try:
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    kpi_label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    kpi_value_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
    kpi_unit_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    brand_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except:
    title_font = subtitle_font = kpi_label_font = kpi_value_font = kpi_unit_font = brand_font = small_font = ImageFont.load_default()

draw.text((WIDTH//2, 80), "THERMAL COAL MARKET OVERVIEW", fill=COLORS['text_white'], font=title_font, anchor='mt')
draw.text((WIDTH//2, 140), "Indonesian Coal Index | Price Benchmarking", fill=COLORS['text_gray'], font=subtitle_font, anchor='mt')

kpis = [
    {'label': 'ICI GAR 5500', 'price': '$84.50', 'unit': '/MT', 'color': COLORS['primary']},
    {'label': 'GAR 4200', 'price': '$63.80', 'unit': '/MT', 'color': COLORS['secondary']},
    {'label': 'GAR 5800', 'price': '$89.70', 'unit': '/MT', 'color': COLORS['tertiary']},
    {'label': 'PH Demand', 'price': '40M', 'unit': 'MT/yr', 'color': COLORS['quaternary']},
    {'label': 'MGEN Ash', 'price': '<10%', 'unit': 'spec', 'color': COLORS['accent_blue']},
]

card_width, card_height, card_y, card_spacing = 340, 200, 250, 40
start_x = (WIDTH - (5 * card_width + 4 * card_spacing)) // 2

for i, kpi in enumerate(kpis):
    x = start_x + i * (card_width + card_spacing)
    draw.rounded_rectangle([x+6, card_y+6, x+card_width+6, card_y+card_height+6], radius=12, fill='#0d1520')
    draw.rounded_rectangle([x, card_y, x+card_width, card_y+card_height], radius=12, fill=COLORS['bg_card'])
    draw.rounded_rectangle([x, card_y, x+card_width, card_y+12], radius=6, fill=kpi['color'])
    circle_x, circle_y = x + card_width//2, card_y + 60
    draw.ellipse([circle_x-30, circle_y-30, circle_x+30, circle_y+30], fill=kpi['color'])
    draw.text((circle_x, circle_y), "●", fill=COLORS['bg_dark'], font=subtitle_font, anchor='mm')
    draw.text((x+card_width//2, card_y+115), kpi['price'], fill=COLORS['text_white'], font=kpi_value_font, anchor='mt')
    draw.text((x+card_width//2, card_y+150), kpi['unit'], fill=COLORS['text_gray'], font=kpi_unit_font, anchor='mt')
    draw.text((x+card_width//2, card_y+180), kpi['label'], fill=COLORS['text_gray'], font=kpi_label_font, anchor='mt')

draw.ellipse([20, 420, 180, 580], fill=COLORS['primary'])
draw.ellipse([1700, 430, 1900, 630], fill=COLORS['secondary'])
draw.ellipse([240, 780, 360, 900], fill=COLORS['tertiary'])
draw.ellipse([1560, 810, 1740, 990], fill=COLORS['quaternary'])
draw.rectangle([50, 700, 200, 730], fill=COLORS['accent_blue'])
draw.rectangle([1720, 750, 1820, 775], fill=COLORS['primary'])

draw.text((WIDTH//2, 530), "KEY DEFINITIONS", fill=COLORS['text_white'], font=subtitle_font, anchor='mt')
info_items = [('GAR', 'Gross Calorific Value'), ('ICI', 'Indonesian Coal Index'), ('MT', 'Metric Tonne'), ('PH', 'Philippines')]
info_spacing, info_start_x = 400, 450
for idx, (label, value) in enumerate(info_items):
    x = info_start_x + idx * info_spacing
    draw.text((x, 590), label, fill=COLORS['primary'], font=kpi_label_font, anchor='mt')
    draw.text((x, 615), value, fill=COLORS['text_gray'], font=kpi_unit_font, anchor='mt')

draw.rectangle([100, 980, 1820, 983], fill=COLORS['accent_blue'])
draw.text((WIDTH//2, 1020), "ECONARES", fill=COLORS['primary'], font=brand_font, anchor='mt')
draw.text((WIDTH//2, 1060), "May 2026", fill=COLORS['text_gray'], font=small_font, anchor='mt')

output_path = '/home/mauiclaw/ECONARES_WORKSPACE/infographics/thermal-coal-deck.png'
img.save(output_path, 'PNG')
print(f"Infographic saved to: {output_path}")
