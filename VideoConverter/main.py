#!/usr/bin/env python3
"""
VideoConverter - Kapsamli Video Donusturucu
Python + Tkinter ile gelistirilmis, FFmpeg tabanli video donusturme araci.
NVIDIA NVENC GPU hizlandirma destekli.
"""
import sys
import os

# Proje klasorunu path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.startup_wizard import check_and_setup


def main():
    """Ana fonksiyon"""
    try:
        # Sistem kontrolü ve kurulum sihirbazı
        result = check_and_setup()

        if result is None:
            # Kullanıcı iptal etti veya FFmpeg kurulamadı
            print("FFmpeg bulunamadi veya kurulum iptal edildi.")
            sys.exit(1)

        ffmpeg_ok, nvenc_ok, nvenc_encoders = result

        if not ffmpeg_ok:
            print("FFmpeg kurulu degil. Uygulama kapatiliyor.")
            sys.exit(1)

        # Ana uygulamayı başlat
        from gui.main_window import MainWindow

        app = MainWindow(nvenc_available=nvenc_ok, nvenc_encoders=nvenc_encoders)
        app.run()

    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
