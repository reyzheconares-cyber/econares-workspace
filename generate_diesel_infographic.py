#!/usr/bin/env python3
"""ECONARES Diesel Infographic Generator"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

OUTPUT_PATH = "/home/mauiclaw/ECONARES_WORKSPACE/infographics/diesel-deck.png"
BRAND = "ECONARES"
PERIOD = "May 2026"
kpi_data = [
    {"label": "Platts Gasoil May26", "value": "$160.67/bbl", "icon": "O"},
    {"label": "Asia 10ppm", "value": "$610/MT FOB KR", "icon": "A"},
    {"label": "PH Pump Price", "value": "P58-65/L", "icon": "P"},
    {"label": "IMO 2020 Cap", "value": "0.50%S", "icon": "I"},
    {"label": "Euro IV Sulfur", "value": "0.005%S", "icon": "E"},
]
colors = ['#e94560', '#0f946b', '#3498db', '#f39c12', '#9b59b6']

fig = plt.figure(figsize=(16, 10), facecolor='#1a1a2e')
# Header
ax_h = fig.add_axes([0, 0.88, 1, 0.12])
ax_h.set_facecolor('#16213e')
ax_h.axis('off')
ax_h.text(0.5, 0.6, f"{BRAND} | DIESEL DASHBOARD", ha='center', va='center', fontsize=28, fontweight='bold', color='#e94560')
ax_h.text(0.5, 0.15, f"Market Intelligence -- {PERIOD}", ha='center', va='center', fontsize=14, color='#a0a0a0')
# Main
ax_m = fig.add_axes([0.02, 0.08, 0.96, 0.78])
ax_m.set_facecolor('#0f0f1a')
ax_m.axis('off')
# Cards
card_w = 0.17
card_h = 0.7
start_x = 0.04
y_pos = 0.15
gap = 0.025
for i, kpi in enumerate(kpi_data):
    x = start_x + i * (card_w + gap)
    rect = FancyBboxPatch((x, y_pos), card_w, card_h, boxstyle="round,pad=0.02,rounding_size=0.03", facecolor='#1e1e3f', edgecolor=colors[i], linewidth=2, zorder=2)
    ax_m.add_patch(rect)
    circle = plt.Circle((x + card_w/2, y_pos + card_h - 0.12), 0.055, color=colors[i], zorder=3, alpha=0.9)
    ax_m.add_patch(circle)
    ax_m.text(x + card_w/2, y_pos + card_h - 0.12, kpi['icon'], ha='center', va='center', fontsize=14, zorder=4, color='white')
    ax_m.text(x + card_w/2, y_pos + card_h - 0.28, kpi['label'], ha='center', va='center', fontsize=10, color='#888888', fontweight='bold', zorder=3)
    ax_m.text(x + card_w/2, y_pos + card_h/2 + 0.05, kpi['value'], ha='center', va='center', fontsize=13, color='#ffffff', fontweight='bold', zorder=3)
    ax_m.axhline(y=y_pos + 0.18, xmin=x + 0.05, xmax=x + card_w - 0.05, color=colors[i], linewidth=1.5, alpha=0.6, zorder=3)
# Footer
ax_f = fig.add_axes([0, 0, 1, 0.05])
ax_f.set_facecolor('#16213e')
ax_f.axis('off')
ax_f.text(0.5, 0.5, "(c) 2026 ECONARES | Diesel Market Overview", ha='center', va='center', fontsize=9, color='#666666')
# Top accent
ax_d = fig.add_axes([0, 0.96, 1, 0.04])
ax_d.set_facecolor('#e94560')
ax_d.axis('off')
# Grid
for y in np.arange(0.05, 0.85, 0.15):
    ax_m.axhline(y=y, color='#2a2a4a', linewidth=0.5, alpha=0.3, zorder=1)
plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches='tight', facecolor='#1a1a2e', edgecolor='none')
plt.close()
print(f"Saved: {OUTPUT_PATH}")
