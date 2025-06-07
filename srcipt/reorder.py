from PIL import Image

# Open the upscaled image (assuming it's from your previous script)
input_image = Image.open("font_texture_upscaled.png")
original_cols, original_rows = 16, 48
new_cols, new_rows = 24, 32

# Calculate glyph dimensions (from the original upscaled image)
glyph_width = input_image.width // original_cols
glyph_height = input_image.height // original_rows

# Create new image with adjusted layout
new_image = Image.new(
    "RGBA",
    (new_cols * glyph_width, new_rows * glyph_height)
)

# Copy glyphs from old layout to new layout
for i in range(original_cols * original_rows):
    # Calculate source position (old layout)
    old_col = i % original_cols
    old_row = i // original_cols
    
    # Calculate destination position (new layout)
    new_col = i % new_cols
    new_row = i // new_cols
    
    # Only process if within bounds of new image
    if new_row < new_rows:
        # Calculate bounding boxes
        src_box = (
            old_col * glyph_width,
            old_row * glyph_height,
            (old_col + 1) * glyph_width,
            (old_row + 1) * glyph_height
        )
        
        dst_pos = (
            new_col * glyph_width,
            new_row * glyph_height
        )
        
        # Copy the glyph
        glyph = input_image.crop(src_box)
        new_image.paste(glyph, dst_pos)

# Save the result
new_image.save("font_texture_reorganized.png")
print(f"Reorganized texture from {original_cols}x{original_rows} to {new_cols}x{new_rows}")