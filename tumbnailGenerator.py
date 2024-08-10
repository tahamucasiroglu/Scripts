from PIL import Image, ImageDraw, ImageFont

def add_numbers_to_image(image_path, output_folder, start_number, end_number, position, font_path, font_size, text_color):
    img = Image.open(image_path)
    img = img.resize((1920, 1080), Image.Resampling.NEAREST)
    font = ImageFont.truetype(font_path, font_size)
    for number in range(start_number, end_number + 1):
        temp_img = img.copy()
        draw = ImageDraw.Draw(temp_img)
        text = str(number)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = position[0] - text_width // 2
        text_y = position[1] - text_height // 2
        draw.text((text_x, text_y), text, font=font, fill=text_color)
        output_path = f"{output_folder}/image_{text}.png"
        temp_img.save(output_path)
        print(f"{number} resmi çıktı.")

add_numbers_to_image(
    image_path="C:/Users/taham/OneDrive/Masaüstü/Russia Backgraund.png",
    output_folder="C:/Users/taham/OneDrive/Masaüstü/restlt",
    start_number=0,
    end_number=5,
    position=(960, 540),
    font_path="arial.ttf",
    font_size=650,
    text_color=(255, 255, 255)
)
