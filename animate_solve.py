from PIL import Image, ImageDraw

# This file created with assistance from GPT-4.

# Load the content from the text file
with open("data/to_animate.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Split content by "Got:" and take the first part to ignore everything after "Got:"
content = content.split("Got:")[0].strip()

# Split the content by empty lines to get individual grids
grids = content.split("\n\n")

# Convert string representation of grids to lists of lists
grids = [grid.split("\n") for grid in grids]

# Dictionary mapping emojis to colors
color_map = {
    "⬜": (255, 255, 255),  # White
    "🟧": (169, 169, 169),  # Darker Gray
    "⬛": (0, 0, 0),        # Black
}

tile_size = 50  # You can adjust this based on your preference

images = []

for grid in grids:
    # Filter out lines that don't contain any of the relevant emojis
    grid = [line for line in grid if any(emoji in line for emoji in color_map.keys())]

    rows = len(grid)
    cols = len(grid[0])
    img = Image.new('RGB', (cols * tile_size, rows * tile_size))
    d = ImageDraw.Draw(img)
    
    for y, row in enumerate(grid):
        for x, emoji in enumerate(row):
            upper_left = (x * tile_size, y * tile_size)
            bottom_right = ((x + 1) * tile_size, (y + 1) * tile_size)
            d.rectangle([upper_left, bottom_right], fill=color_map[emoji])
    
    images.append(img)

# Determine the duration for each frame to make the entire animation last 7 seconds
total_frames_for_animation = len(images)
duration_per_frame = 7000 // total_frames_for_animation  # 7000ms = 7 seconds


# Display the final frame for an additional 5 seconds (30 frames at 6fps)
for _ in range(30):
    images.append(images[-1])


# Calculate durations
durations = [duration_per_frame] * total_frames_for_animation + [167] * 30  # 167ms per frame for 6fps

images[0].save('animated_nonogram.gif',
               save_all=True, append_images=images[1:], optimize=True, duration=durations, loop=0)


