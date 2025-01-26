from PIL import Image, ImageDraw, ImageFont

def add_numbers_to_image(image_path, output_folder, start_number, end_number, position, font_path, font_size, text_color):
    img = Image.open(image_path)
    img = img.resize((1920, 1080), Image.Resampling.NEAREST)
    font = ImageFont.truetype(font_path, font_size)
    
    for number in range(start_number, end_number + 1):
        temp_img = img.copy()
        draw = ImageDraw.Draw(temp_img)
        text = str(number)
        draw.text(position, text, font=font, fill=text_color)
        output_path = f"{output_folder}/image_{text}.png"
        temp_img.save(output_path)
        print(f"{number} resmi çıktı.")


# add_numbers_to_image(
#     image_path="C:/Users/taham/OneDrive/Masaüstü/Russia Backgraund.png",
#     output_folder="C:/Users/taham/OneDrive/Masaüstü/restlt",
#     start_number=0,
#     end_number=10,
#     position=(750, 350),
#     font_path="arial.ttf",
#     font_size=650,
#     text_color=(255, 255, 255)
# )

add_numbers_to_image(
    image_path="C:/Users/taham/OneDrive/Masaüstü/The Zoro-Austrians .jpg",
    #image_path="C:/Users/taham/OneDrive/Masaüstü/image_1.png",
    output_folder="C:/Users/taham/OneDrive/Masaüstü/The Zoro-Austrians",
    start_number=0,
    end_number=20,
    #position=(200, -120),
    position=(-20, -120),
    font_path="arial.ttf",
    font_size=650,
    text_color=(255, 255, 255)
)










