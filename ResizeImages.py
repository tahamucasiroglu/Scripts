from PIL import Image
import os

def resize_images_in_folder(folder_path, output_folder, max_width, max_height):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            img_path = os.path.join(folder_path, filename)
            img = Image.open(img_path)
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            output_path = os.path.join(output_folder, filename)
            img.save(output_path)
            print(f"{filename} boyutu küçültüldü ve {output_path} konumuna kaydedildi.")

resize_images_in_folder(
    folder_path="C:/Users/taham/OneDrive/Masaüstü/The Zoro-Austrians",  # Girdi klasörü
    output_folder="C:/Users/taham/OneDrive/Masaüstü/The Zoro-Austrians Resize",  # Çıktı klasörü
    max_width=1280,  # Maksimum genişlik
    max_height=720  # Maksimum yükseklik
)
