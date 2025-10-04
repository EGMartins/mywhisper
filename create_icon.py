#!/usr/bin/env python3
"""Create a simple icon for MyWhisper"""

from PIL import Image, ImageDraw

# Create a 256x256 icon
size = 256
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Draw a microphone shape
# Circle for the mic head
mic_color = (70, 130, 180)  # Steel blue
draw.ellipse([size//3, size//5, 2*size//3, size//2], fill=mic_color)

# Rectangle for the mic body
draw.rectangle([5*size//12, size//2, 7*size//12, 2*size//3], fill=mic_color)

# Stand base
draw.rectangle([size//3, 2*size//3, 2*size//3, 2*size//3 + 10], fill=mic_color)
draw.rectangle([5*size//12, 2*size//3 + 10, 7*size//12, 3*size//4], fill=mic_color)

# Sound waves to indicate recording
wave_color = (100, 150, 200, 128)
for i in range(3):
    offset = i * 15
    draw.arc([size//6 - offset, size//4 - offset, size//3 - offset, size//2 + offset],
             start=210, end=330, fill=wave_color, width=3)
    draw.arc([2*size//3 + offset, size//4 - offset, 5*size//6 + offset, size//2 + offset],
             start=210, end=330, fill=wave_color, width=3)

# Save the icon
image.save('icon.png', 'PNG')
print("Icon created: icon.png")