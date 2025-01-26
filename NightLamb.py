import pygame
import sys
import math
import time
import os
from itertools import cycle
from tkinter import Tk, Button, Label, StringVar, Scale, HORIZONTAL, filedialog, colorchooser

# Pygame'i başlat
pygame.init()

# Ekran boyutunu al
infoObject = pygame.display.Info()
ekran_genislik = infoObject.current_w
ekran_yukseklik = infoObject.current_h

# Tam ekran pencere oluştur
screen = pygame.display.set_mode((ekran_genislik, ekran_yukseklik), pygame.NOFRAME)
pygame.mouse.set_visible(False)

# Renkler
gokkusagi_renkleri = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
renk_dongusu = cycle(gokkusagi_renkleri)
yanip_sonme_renk = (255, 255, 255)  # Varsayılan beyaz renk

# Mod ve ayar değişkenleri
mod = "rengarenk"
sure = 10  # Saniye cinsinden süre
parlaklik = 1.0
video_yolu = ""
resim_klasoru = ""

# Tkinter ile seçim ekranı oluştur
root = Tk()
root.title("Gece Lambası Mod Seçimi")
root.geometry("400x500")

mod_var = StringVar(value="rengarenk")
sure_var = StringVar(value="10")
parlaklik_var = StringVar(value="1.0")

Label(root, text="Mod Seçimi:").pack()
Button(root, text="Rengarenk", command=lambda: mod_var.set("rengarenk")).pack()
Button(root, text="Yanıp Sönme", command=lambda: mod_var.set("yanip_sonme")).pack()
Button(root, text="Video Oynatma", command=lambda: mod_var.set("video")).pack()
Button(root, text="Sergi", command=lambda: mod_var.set("sergi")).pack()

Label(root, text="Süre Seçimi (saniye):").pack()
Scale(root, from_=3, to=120, orient=HORIZONTAL, variable=sure_var).pack()

Label(root, text="Parlaklık Ayarı:").pack()
Scale(root, from_=0.1, to=1.0, resolution=0.1, orient=HORIZONTAL, variable=parlaklik_var).pack()

renk_dizisi = []

def renk_ekle():
    renk = colorchooser.askcolor()[0]
    if renk:
        renk_dizisi.append((int(renk[0]), int(renk[1]), int(renk[2])))
        global renk_dongusu
        renk_dongusu = cycle(renk_dizisi)

Button(root, text="Rengarenk için Renk Ekle", command=renk_ekle).pack()


def yanip_sonme_renk_sec():
    renk = colorchooser.askcolor()[0]
    if renk:
        global yanip_sonme_renk
        yanip_sonme_renk = (int(renk[0]), int(renk[1]), int(renk[2]))

Button(root, text="Yanıp Sönme İçin Renk Seç", command=yanip_sonme_renk_sec).pack()

Button(root, text="Video Seç", command=lambda: filedialog.askopenfilename()).pack()
Button(root, text="Resim Klasörü Seç", command=lambda: filedialog.askdirectory()).pack()

Button(root, text="Başlat", command=lambda: [root.quit(), root.destroy()]).pack()

root.mainloop()

# Seçilen değerleri al
mod = mod_var.get()
sure = max(3.0, float(sure_var.get()))
parlaklik = float(parlaklik_var.get())

# Renk geçişi için başlangıç zamanı
baslangic_zamani = time.time()
renk1 = next(renk_dongusu)
renk2 = next(renk_dongusu)

# FPS ayarı
fps = 120
saat = pygame.time.Clock()

# Gece lambası çalışırken
while True:
    try:
        # Çıkış kontrolü (ESC tuşu)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        # Modlara göre ekranı güncelle
        if mod == "rengarenk":
            gecen_sure = time.time() - baslangic_zamani
            if gecen_sure >= sure:
                baslangic_zamani = time.time()
                renk1 = renk2
                renk2 = next(renk_dongusu)
            oran = gecen_sure / sure
            oran = max(0.0, min(1.0, oran))
            renk = (
                round(renk1[0] + (renk2[0] - renk1[0]) * oran),
                round(renk1[1] + (renk2[1] - renk1[1]) * oran),
                round(renk1[2] + (renk2[2] - renk1[2]) * oran),
            )
            renk = (max(0, min(255, renk[0])), max(0, min(255, renk[1])), max(0, min(255, renk[2])))
            screen.fill(renk)

        elif mod == "yanip_sonme":
            gecen_sure = time.time() - baslangic_zamani
            parlaklik_orani = (1 + math.sin(gecen_sure * 2 * 3.14159 / sure)) / 2 if sure != 0 else 0
            renk = (
                int(yanip_sonme_renk[0] * parlaklik_orani),
                int(yanip_sonme_renk[1] * parlaklik_orani),
                int(yanip_sonme_renk[2] * parlaklik_orani),
            )
            screen.fill(renk)

        elif mod == "video" and video_yolu:
            # Video oynatma kodu buraya eklenebilir
            pass

        elif mod == "sergi" and resim_klasoru:
            # Resim gösterme kodu buraya eklenebilir
            pass

        # Parlaklık ayarı
        overlay = pygame.Surface((ekran_genislik, ekran_yukseklik))
        overlay.set_alpha(int((1 - parlaklik) * 255))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Ekranı güncelle
        pygame.display.flip()
        saat.tick(fps)
    except ValueError as e:
        print(f"Hata: {e}")
        pygame.quit()
        sys.exit()
