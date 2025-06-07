from PIL import Image

def process_glyph_pixels(img):
    """Convert colored pixels to black, keep alpha, and make transparent areas white."""
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if a > 10:  # Visible pixel → BLACK
                pixels[x, y] = (0, 0, 0, a)
            else:  # Transparent pixel → WHITE (fully transparent)
                pixels[x, y] = (255, 255, 255, 0)
    return img

# Open the reorganized image
input_image = Image.open("bescii-chars.png")
input_image = input_image.convert("RGBA")  # Ensure it has an alpha channel

# Process every pixel
output_image = process_glyph_pixels(input_image)

# Save the result
output_image.save("font_texture.png")
print("Done! Saved as 'font_texture.png'")