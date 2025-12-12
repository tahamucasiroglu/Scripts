"""Başlangıç sihirbazı - Otomatik kurulum"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import platform
from typing import Callable, Optional

from core.installer import Installer


class StartupWizard:
    """Otomatik kurulum sihirbazı"""

    def __init__(self):
        self.ffmpeg_ok = False
        self.nvenc_ok = False
        self.nvenc_encoders = []
        self.cancelled = False

        self.root = tk.Tk()
        self.root.title("VideoConverter")
        self.root.geometry("450x300")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._center_window()
        self._create_widgets()

        # Kontrolü başlat
        self.root.after(300, self._start_check)

    def _center_window(self):
        """Pencereyi ortala"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 225
        y = (self.root.winfo_screenheight() // 2) - 150
        self.root.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Widget'ları oluştur"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Başlık
        ttk.Label(
            main_frame,
            text="VideoConverter",
            font=("", 16, "bold")
        ).pack(pady=(0, 5))

        ttk.Label(
            main_frame,
            text="Sistem kontrol ediliyor...",
            foreground="gray"
        ).pack(pady=(0, 15))

        # Durum frame
        status_frame = ttk.LabelFrame(main_frame, text="Durum", padding=10)
        status_frame.pack(fill="x", pady=10)

        # FFmpeg durumu
        ffmpeg_row = ttk.Frame(status_frame)
        ffmpeg_row.pack(fill="x", pady=3)
        self.ffmpeg_icon = ttk.Label(ffmpeg_row, text="⏳", font=("", 12))
        self.ffmpeg_icon.pack(side="left")
        self.ffmpeg_status = ttk.Label(ffmpeg_row, text="FFmpeg kontrol ediliyor...")
        self.ffmpeg_status.pack(side="left", padx=10)

        # GPU durumu
        gpu_row = ttk.Frame(status_frame)
        gpu_row.pack(fill="x", pady=3)
        self.gpu_icon = ttk.Label(gpu_row, text="⏳", font=("", 12))
        self.gpu_icon.pack(side="left")
        self.gpu_status = ttk.Label(gpu_row, text="GPU kontrol ediliyor...")
        self.gpu_status.pack(side="left", padx=10)

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )
        self.progress_bar.pack(fill="x", pady=15)

        # Mesaj
        self.message_label = ttk.Label(
            main_frame,
            text="",
            foreground="gray",
            wraplength=400
        )
        self.message_label.pack(pady=5)

        # Butonlar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)

        self.cancel_btn = ttk.Button(btn_frame, text="Iptal", command=self._on_close)
        self.cancel_btn.pack(side="right")

    def _start_check(self):
        """Kontrol başlat"""
        thread = threading.Thread(target=self._do_check, daemon=True)
        thread.start()

    def _do_check(self):
        """Kontrolleri yap"""
        # FFmpeg kontrol
        self._update_ui("FFmpeg kontrol ediliyor...", 10)
        self.ffmpeg_ok, ffmpeg_msg = Installer.check_ffmpeg()

        if self.ffmpeg_ok:
            self._set_ffmpeg_ok(ffmpeg_msg)
        else:
            # FFmpeg yok - kuralım mı?
            self._set_ffmpeg_missing()
            return

        # NVENC kontrol
        self._check_gpu()

    def _set_ffmpeg_ok(self, version: str):
        """FFmpeg kurulu"""
        def update():
            self.ffmpeg_icon.config(text="✅")
            self.ffmpeg_status.config(text="FFmpeg kurulu", foreground="green")
            self.progress_var.set(50)
        self.root.after(0, update)

    def _set_ffmpeg_missing(self):
        """FFmpeg kurulu değil - kullanıcıya sor"""
        def ask():
            self.ffmpeg_icon.config(text="❌")
            self.ffmpeg_status.config(text="FFmpeg kurulu degil", foreground="red")
            self.gpu_icon.config(text="⏸️")
            self.gpu_status.config(text="Bekliyor...", foreground="gray")
            self.progress_var.set(0)

            # Kullanıcıya sor
            result = messagebox.askyesno(
                "FFmpeg Gerekli",
                "FFmpeg kurulu degil.\n\n"
                "FFmpeg video donusturme icin gereklidir.\n"
                "Simdi otomatik olarak kurayim mi?\n\n"
                "(Internet baglantisi gerekli)",
                parent=self.root
            )

            if result:
                self._install_ffmpeg()
            else:
                messagebox.showerror(
                    "Kurulum Gerekli",
                    "FFmpeg olmadan program calismaz.\n"
                    "Program kapatiliyor.",
                    parent=self.root
                )
                self._on_close()

        self.root.after(0, ask)

    def _install_ffmpeg(self):
        """FFmpeg kur"""
        def update_progress(msg, pct=None):
            def do_update():
                self.message_label.config(text=msg)
                if pct is not None:
                    self.progress_var.set(pct * 0.5)  # 0-50 arası
            self.root.after(0, do_update)

        def do_install():
            self.root.after(0, lambda: self.ffmpeg_status.config(
                text="Kuruluyor...", foreground="orange"
            ))

            success, message = Installer.install_ffmpeg(update_progress)

            if success:
                self.ffmpeg_ok = True
                self.root.after(0, lambda: self._set_ffmpeg_ok("Yeni kuruldu"))
                self.root.after(0, lambda: self.message_label.config(text=""))
                # GPU kontrolüne geç
                self._check_gpu()
            else:
                def show_error():
                    self.ffmpeg_icon.config(text="❌")
                    self.ffmpeg_status.config(text="Kurulum basarisiz", foreground="red")
                    messagebox.showerror(
                        "Kurulum Hatasi",
                        f"FFmpeg kurulamadi:\n\n{message}\n\n"
                        "Manuel kurulum yapin veya internet baglantinizi kontrol edin.",
                        parent=self.root
                    )
                    self._on_close()
                self.root.after(0, show_error)

        thread = threading.Thread(target=do_install, daemon=True)
        thread.start()

    def _check_gpu(self):
        """GPU kontrol et"""
        self._update_ui("GPU kontrol ediliyor...", 60)

        # NVIDIA GPU var mı?
        gpu_ok, gpu_name = Installer.check_nvidia_gpu()

        if gpu_ok:
            # NVENC çalışıyor mu?
            self.nvenc_ok, self.nvenc_encoders = Installer.check_nvenc()

            if self.nvenc_ok:
                self._set_gpu_ok(gpu_name)
            else:
                # GPU var ama NVENC yok - sürücü sorunu
                self._set_gpu_driver_issue(gpu_name)
        else:
            # GPU yok
            self._set_gpu_missing()

    def _set_gpu_ok(self, gpu_name: str):
        """GPU hazır"""
        def update():
            self.gpu_icon.config(text="✅")
            self.gpu_status.config(
                text=f"GPU aktif: {gpu_name}",
                foreground="green"
            )
            self.progress_var.set(100)
            self.message_label.config(text="Sistem hazir!")
            self._complete()
        self.root.after(0, update)

    def _set_gpu_driver_issue(self, gpu_name: str):
        """GPU var ama sürücü sorunu - kurulum sor"""
        def ask():
            self.gpu_icon.config(text="⚠️")
            self.gpu_status.config(
                text=f"GPU bulundu ({gpu_name}) - NVENC pasif",
                foreground="orange"
            )
            self.progress_var.set(70)

            # Kullanıcıya sor
            result = messagebox.askyesno(
                "GPU Surucusu Gerekli",
                f"NVIDIA GPU bulundu: {gpu_name}\n\n"
                "Ancak GPU hizlandirma (NVENC) aktif degil.\n"
                "NVIDIA suruculerini simdi kurayim mi?\n\n"
                "(Kurulum sonrasi bilgisayar yeniden baslatilmali)",
                parent=self.root
            )

            if result:
                self._install_nvidia_driver()
            else:
                # CPU ile devam et
                self.gpu_status.config(
                    text="GPU pasif - CPU kullanilacak",
                    foreground="gray"
                )
                self.progress_var.set(100)
                self.message_label.config(
                    text="GPU hizlandirma olmadan devam ediliyor."
                )
                self._complete()

        self.root.after(0, ask)

    def _install_nvidia_driver(self):
        """NVIDIA sürücü kur"""
        def update_progress(msg, pct=None):
            def do_update():
                self.message_label.config(text=msg)
                if pct is not None:
                    self.progress_var.set(70 + (pct * 0.3))  # 70-100 arası
            self.root.after(0, do_update)

        def do_install():
            self.root.after(0, lambda: self.gpu_status.config(
                text="Surucu kuruluyor...", foreground="orange"
            ))

            success, message = Installer.install_nvidia_driver(update_progress)

            def show_result():
                if success:
                    self.gpu_icon.config(text="✅")
                    self.gpu_status.config(text="Surucu kuruldu", foreground="green")
                    messagebox.showinfo(
                        "Kurulum Tamamlandi",
                        f"{message}\n\n"
                        "Bilgisayari yeniden baslattiktan sonra\n"
                        "GPU hizlandirma aktif olacak.",
                        parent=self.root
                    )
                else:
                    self.gpu_icon.config(text="⚠️")
                    self.gpu_status.config(text="Surucu kurulamadi", foreground="orange")
                    messagebox.showwarning(
                        "Kurulum",
                        f"{message}",
                        parent=self.root
                    )

                self.progress_var.set(100)
                self.message_label.config(text="")
                self._complete()

            self.root.after(0, show_result)

        thread = threading.Thread(target=do_install, daemon=True)
        thread.start()

    def _set_gpu_missing(self):
        """GPU yok - CPU kullanılacak"""
        def update():
            self.gpu_icon.config(text="ℹ️")
            self.gpu_status.config(
                text="GPU bulunamadi - CPU kullanilacak",
                foreground="gray"
            )
            self.progress_var.set(100)
            self.message_label.config(
                text="NVIDIA ekran karti ile daha hizli donusum yapilabilir."
            )
            self._complete()
        self.root.after(0, update)

    def _update_ui(self, message: str, progress: float):
        """UI güncelle"""
        def update():
            self.message_label.config(text=message)
            self.progress_var.set(progress)
        self.root.after(0, update)

    def _complete(self):
        """Tamamlandı - devam et"""
        def do_complete():
            # 1 saniye bekle ve devam et
            self.cancel_btn.config(text="Basla", command=self._continue)
            self.root.after(1500, self._continue)
        self.root.after(0, do_complete)

    def _continue(self):
        """Ana uygulamaya geç"""
        self.root.destroy()

    def _on_close(self):
        """Kapat"""
        self.cancelled = True
        self.ffmpeg_ok = False
        self.root.destroy()

    def run(self) -> tuple:
        """
        Sihirbazı çalıştır

        Returns:
            (ffmpeg_ok, nvenc_ok, nvenc_encoders) veya (False, False, []) iptal edilirse
        """
        self.root.mainloop()

        if self.cancelled:
            return False, False, []

        return self.ffmpeg_ok, self.nvenc_ok, self.nvenc_encoders


def check_and_setup() -> tuple:
    """
    Sistem kontrolü ve kurulum

    Returns:
        (ffmpeg_ok, nvenc_ok, nvenc_encoders) veya None (iptal)
    """
    wizard = StartupWizard()
    ffmpeg_ok, nvenc_ok, nvenc_encoders = wizard.run()

    if not ffmpeg_ok:
        return None

    return ffmpeg_ok, nvenc_ok, nvenc_encoders
