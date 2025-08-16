
from PIL import Image, ImageDraw
import os

def create_icon(size, filename):
    # Create a simple icon with gradient background
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient-like background
    for i in range(size):
        color_val = int(102 + (126 - 102) * (i / size))  # #667eea gradient
        draw.line([(0, i), (size, i)], fill=(color_val, color_val, 234))
    
    # Draw simple dollar sign
    center = size // 2
    font_size = size // 3
    
    # Draw dollar sign outline
    draw.ellipse([center-font_size//2, center-font_size//2, 
                  center+font_size//2, center+font_size//2], 
                 fill='white', outline='#333', width=3)
    
    # Draw $ symbol
    draw.text((center-font_size//4, center-font_size//3), '$', 
              fill='#333', anchor='mm')
    
    img.save(f'static/{filename}')
    print(f'Created {filename}')

if __name__ == '__main__':
    create_icon(192, 'icon-192.png')
    create_icon(512, 'icon-512.png')
