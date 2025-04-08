from PIL import Image

# this script makes a bad sized texture map a nicer size (what i needed at that time)
# and adds the missing "space" -> an empty glyph before the first texture :)

# Load the original texture map
original_image = Image.open("bescii-chars.png")
width, height = original_image.size
glyph_width = width // 51  # Width of each glyph
glyph_height = height // 15  # Height of each glyph

# Calculate new dimensions
new_rows = 48
new_cols = 16  # Fixed at 16 columns

# Create a new blank image
new_image = Image.new("RGBA", (new_cols * glyph_width, new_rows * glyph_height))

# Extract and repack glyphs
for y_old in range(15):  # Original height (15 rows)
    for x_old in range(51):  # Original width (51 columns)
        # Calculate position in old texture
        x1_old = x_old * glyph_width
        y1_old = y_old * glyph_height
        x2_old = x1_old + glyph_width
        y2_old = y1_old + glyph_height
        
        # Extract glyph
        glyph = original_image.crop((x1_old, y1_old, x2_old, y2_old))
        
        # Calculate position in new texture
        index = y_old * 51 + x_old  # Linear index in the old texture
        x_new = (index % new_cols) * glyph_width  # Column in new texture
        y_new = (index // new_cols) * glyph_height  # Row in new texture
        
        # Paste glyph into new texture
        new_image.paste(glyph, (x_new, y_new))

# Save the new texture map
new_image.save("font_texture.png")





# Load the original texture map
original_width, original_height = original_image.size

# Calculate glyph dimensions
glyph_width = original_width // 51  # Original columns were 51
glyph_height = original_height // 15  # Original rows were 15

# New dimensions (16 columns × 48 rows)
new_cols = 16
new_rows = 48

# Create a new blank image with transparent background
new_image = Image.new("RGBA", (new_cols * glyph_width, new_rows * glyph_height))

# Create a transparent "empty" glyph
empty_glyph = Image.new("RGBA", (glyph_width, glyph_height), (0, 0, 0, 0))

# Step 1: Place the empty glyph at position 0 (first cell)
new_image.paste(empty_glyph, (0, 0))

# Step 2: Reposition all original glyphs starting at index 1
for y_old in range(15):
    for x_old in range(51):
        # Calculate the original index (0-based)
        original_index = y_old * 51 + x_old
        
        # Calculate the new index (shifted by +1 to leave position 0 empty)
        new_index = original_index + 1

        # Calculate coordinates in the new texture map
        x_new = (new_index % new_cols) * glyph_width
        y_new = (new_index // new_cols) * glyph_height

        # Extract the glyph from the original texture
        x1_old = x_old * glyph_width
        y1_old = y_old * glyph_height
        x2_old = x1_old + glyph_width
        y2_old = y1_old + glyph_height
        glyph = original_image.crop((x1_old, y1_old, x2_old, y2_old))

        # Paste the glyph into the new texture (starting at new_index = 1)
        new_image.paste(glyph, (x_new, y_new))

# Save the modified texture map
new_image.save("font_texture_16x48_with_empty.png")