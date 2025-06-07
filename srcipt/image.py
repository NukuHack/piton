from PIL import Image

def upscale_glyph(glyph, factor=2):
    """Upscale a glyph by a factor, blending pixels for smoothness."""
    if not isinstance(glyph, Image.Image):
        raise ValueError("Input must be a PIL Image object")
    
    width, height = glyph.size
    if width == 0 or height == 0:
        return glyph.copy()
    
    new_width = width * factor
    new_height = height * factor
    upscaled = Image.new("RGBA", (new_width, new_height))

    # Get all original pixels at once for better performance
    original_pixels = glyph.load()
    
    # Step 1: Copy original pixels to new positions (factor*x, factor*y)
    for y in range(height):
        for x in range(width):
            upscaled.putpixel((x * factor, y * factor), original_pixels[x, y])

    # Step 2: Fill horizontal gaps (average left and right)
    for y in range(0, new_height, factor):
        for x in range(1, new_width, 2):
            left_x = x - 1
            right_x = x + 1 if x + 1 < new_width else left_x
            left = upscaled.getpixel((left_x, y))
            right = upscaled.getpixel((right_x, y))
            blended = tuple((l + r) // 2 for l, r in zip(left, right))
            upscaled.putpixel((x, y), blended)

    # Step 3: Fill vertical gaps (average top and bottom)
    for y in range(1, new_height, 2):
        for x in range(0, new_width, factor):
            top_y = y - 1
            bottom_y = y + 1 if y + 1 < new_height else top_y
            top = upscaled.getpixel((x, top_y))
            bottom = upscaled.getpixel((x, bottom_y))
            blended = tuple((t + b) // 2 for t, b in zip(top, bottom))
            upscaled.putpixel((x, y), blended)

    # Step 4: Fill diagonal gaps (average 4 nearest pixels)
    for y in range(1, new_height, 2):
        for x in range(1, new_width, 2):
            # Get neighboring coordinates with boundary checks
            left = x - 1
            right = x + 1 if x + 1 < new_width else left
            top = y - 1
            bottom = y + 1 if y + 1 < new_height else top
            
            # Get neighboring pixels
            tl = upscaled.getpixel((left, top))   # Top-left
            tr = upscaled.getpixel((right, top))    # Top-right
            bl = upscaled.getpixel((left, bottom))  # Bottom-left
            br = upscaled.getpixel((right, bottom)) # Bottom-right
            
            # Blend all available neighbors
            blended = tuple((a + b + c + d) // 4 for a, b, c, d in zip(tl, tr, bl, br))
            upscaled.putpixel((x, y), blended)

    return upscaled

width, height = 16, 48

# Load the original texture map
original_image = Image.open("bescii-chars.png")
img_width, img_height = original_image.size
glyph_width = img_width // width  # Original glyph width
glyph_height = img_height // height  # Original glyph height

# Calculate upscaled dimensions
upscaled_glyph_width = glyph_width * 2
upscaled_glyph_height = glyph_height * 2

# Create a new blank image with upscaled dimensions
new_image = Image.new(
    "RGBA",
    (width * upscaled_glyph_width, height * upscaled_glyph_height)
)

# Process each glyph in the original image
for row in range(height):
    for col in range(width):
        # Calculate the bounding box of the current glyph
        left = col * glyph_width
        upper = row * glyph_height
        right = left + glyph_width
        lower = upper + glyph_height
        
        # Extract the glyph
        glyph = original_image.crop((left, upper, right, lower))
        
        # Upscale the glyph
        upscaled_glyph = upscale_glyph(glyph)
        
        # Calculate the position in the new image
        new_left = col * upscaled_glyph_width
        new_upper = row * upscaled_glyph_height
        
        # Paste the upscaled glyph into the new image
        new_image.paste(upscaled_glyph, (new_left, new_upper))

# Save the result
new_image.save("font_texture_upscaled.png")