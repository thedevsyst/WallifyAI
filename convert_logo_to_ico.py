from PIL import Image

# Convert PNG to ICO
png_path = "WallifyAI-logo.png"
ico_path = "WallifyAI-logo.ico"

# Open the PNG file
img = Image.open(png_path)

# Save as ICO
img.save(ico_path, format="ICO", sizes=[(32, 32)])

print(f"Converted {png_path} to {ico_path}")
