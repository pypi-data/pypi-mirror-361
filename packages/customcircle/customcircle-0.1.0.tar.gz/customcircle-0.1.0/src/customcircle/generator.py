from PIL import Image, ImageDraw, ImageFont

def draw_circle_with_name(name, output_path="circle.png", size=300):
    # Create a blank square image
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image)

    # Draw circle
    center = (size // 2, size // 2)
    radius = size // 2 - 10
    draw.ellipse([
        (center[0] - radius, center[1] - radius),
        (center[0] + radius, center[1] + radius)
    ], outline="black", width=4)

    # Add name text
    font_size = size // 10
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Use textbbox instead of textsize (new Pillow)
    bbox = draw.textbbox((0, 0), name, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_position = (center[0] - text_width // 2, center[1] - text_height // 2)

    draw.text(text_position, name, fill="black", font=font)
    image.save(output_path)
    print(f"Circle image saved as {output_path}")
