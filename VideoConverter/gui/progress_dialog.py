"""İlerleme gösterge penceresi"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


class ProgressDialog(tk.Toplevel):
    """Dönüştürme ilerleme penceresi"""

    def __init__(
        self,
        parent,
        title: str = "Dönüştürülüyor...",
        on_cancel: Optional[Callable] = None
    ):
        super().__init__(parent)
        self.title(title)
        self.on_cancel = on_cancel

        # Pencere ayarları
        self.geometry("500x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Kapatma düğmesi işlevi
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        """Widget'ları oluştur"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Dosya bilgisi
        self.file_label = ttk.Label(
            main_frame,
            text="Hazırlanıyor...",
            font=("", 10, "bold")
        )
        self.file_label.pack(anchor="w", pady=(0, 10))

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
            length=460
        )
        self.progress_bar.pack(fill="x", pady=5)

        # Yüzde label
        self.percent_label = ttk.Label(main_frame, text="0%", font=("", 12, "bold"))
        self.percent_label.pack(pady=5)

        # Detay bilgileri frame
        detail_frame = ttk.LabelFrame(main_frame, text="Detaylar", padding=10)
        detail_frame.pack(fill="x", pady=10)

        # Sol kolon
        left_frame = ttk.Frame(detail_frame)
        left_frame.pack(side="left", fill="x", expand=True)

        # Süre
        time_frame = ttk.Frame(left_frame)
        time_frame.pack(fill="x", pady=2)
        ttk.Label(time_frame, text="Süre:", width=10).pack(side="left")
        self.time_label = ttk.Label(time_frame, text="00:00 / 00:00")
        self.time_label.pack(side="left")

        # Frame
        frame_frame = ttk.Frame(left_frame)
        frame_frame.pack(fill="x", pady=2)
        ttk.Label(frame_frame, text="Frame:", width=10).pack(side="left")
        self.frame_label = ttk.Label(frame_frame, text="0")
        self.frame_label.pack(side="left")

        # Sağ kolon
        right_frame = ttk.Frame(detail_frame)
        right_frame.pack(side="right", fill="x", expand=True)

        # FPS
        fps_frame = ttk.Frame(right_frame)
        fps_frame.pack(fill="x", pady=2)
        ttk.Label(fps_frame, text="FPS:", width=10).pack(side="left")
        self.fps_label = ttk.Label(fps_frame, text="0")
        self.fps_label.pack(side="left")

        # Hız
        speed_frame = ttk.Frame(right_frame)
        speed_frame.pack(fill="x", pady=2)
        ttk.Label(speed_frame, text="Hız:", width=10).pack(side="left")
        self.speed_label = ttk.Label(speed_frame, text="0x")
        self.speed_label.pack(side="left")

        # Boyut
        size_frame = ttk.Frame(right_frame)
        size_frame.pack(fill="x", pady=2)
        ttk.Label(size_frame, text="Boyut:", width=10).pack(side="left")
        self.size_label = ttk.Label(size_frame, text="0 MB")
        self.size_label.pack(side="left")

        # Durum mesajı
        self.status_label = ttk.Label(
            main_frame,
            text="Başlatılıyor...",
            foreground="gray"
        )
        self.status_label.pack(pady=5)

        # İptal butonu
        self.cancel_btn = ttk.Button(
            main_frame,
            text="İptal",
            command=self._on_cancel_click
        )
        self.cancel_btn.pack(pady=10)

    def _center_window(self):
        """Pencereyi ortala"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _on_cancel_click(self):
        """İptal butonuna tıklandı"""
        self.status_label.config(text="İptal ediliyor...", foreground="orange")
        self.cancel_btn.config(state="disabled")
        if self.on_cancel:
            self.on_cancel()

    def _on_close(self):
        """Pencere kapatılmaya çalışıldı"""
        self._on_cancel_click()

    def update_progress(self, progress: dict):
        """İlerlemeyi güncelle"""
        if "percent" in progress:
            percent = min(100, progress["percent"])
            self.progress_var.set(percent)
            self.percent_label.config(text=f"{percent:.1f}%")

        if "current_time" in progress:
            current = progress["current_time"]
            total = progress.get("total_time", 0)
            self.time_label.config(
                text=f"{self._format_time(current)} / {self._format_time(total)}"
            )

        if "frame" in progress:
            self.frame_label.config(text=str(progress["frame"]))

        if "fps" in progress:
            self.fps_label.config(text=f"{progress['fps']:.1f}")

        if "speed" in progress:
            self.speed_label.config(text=f"{progress['speed']:.2f}x")

        if "size" in progress:
            size_mb = progress["size"] / (1024 * 1024)
            if size_mb >= 1024:
                self.size_label.config(text=f"{size_mb/1024:.2f} GB")
            else:
                self.size_label.config(text=f"{size_mb:.1f} MB")

        if "status" in progress:
            self.status_label.config(text=progress["status"], foreground="gray")

        self.update_idletasks()

    def set_file_info(self, filename: str, total_duration: float = 0):
        """Dosya bilgisini ayarla"""
        self.file_label.config(text=f"Dosya: {filename}")
        self.total_duration = total_duration

    def set_status(self, status: str, color: str = "gray"):
        """Durum mesajını ayarla"""
        self.status_label.config(text=status, foreground=color)

    def set_complete(self):
        """Tamamlandı durumu"""
        self.progress_var.set(100)
        self.percent_label.config(text="100%")
        self.status_label.config(text="Tamamlandı!", foreground="green")
        self.cancel_btn.config(text="Kapat", command=self.destroy)

    def set_error(self, message: str):
        """Hata durumu"""
        self.status_label.config(text=f"Hata: {message}", foreground="red")
        self.cancel_btn.config(text="Kapat", command=self.destroy)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Saniyeyi formatlı string'e çevir"""
        if seconds < 0:
            return "00:00"
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"


class BatchProgressDialog(tk.Toplevel):
    """Toplu dönüştürme ilerleme penceresi"""

    def __init__(self, parent, total_files: int, on_cancel: Optional[Callable] = None):
        super().__init__(parent)
        self.title("Toplu Dönüştürme")
        self.on_cancel = on_cancel
        self.total_files = total_files

        self.geometry("500x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Genel ilerleme
        ttk.Label(main_frame, text="Genel İlerleme:", font=("", 10, "bold")).pack(anchor="w")

        self.overall_var = tk.DoubleVar(value=0)
        self.overall_bar = ttk.Progressbar(
            main_frame,
            variable=self.overall_var,
            maximum=100,
            length=460
        )
        self.overall_bar.pack(fill="x", pady=5)

        self.overall_label = ttk.Label(main_frame, text="0 / 0 dosya")
        self.overall_label.pack(anchor="w")

        # Mevcut dosya
        ttk.Label(main_frame, text="Mevcut Dosya:", font=("", 10, "bold")).pack(anchor="w", pady=(15, 0))

        self.current_var = tk.DoubleVar(value=0)
        self.current_bar = ttk.Progressbar(
            main_frame,
            variable=self.current_var,
            maximum=100,
            length=460
        )
        self.current_bar.pack(fill="x", pady=5)

        self.current_label = ttk.Label(main_frame, text="Hazırlanıyor...")
        self.current_label.pack(anchor="w")

        # İptal
        self.cancel_btn = ttk.Button(main_frame, text="İptal", command=self._on_cancel)
        self.cancel_btn.pack(pady=15)

    def _center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (250)
        y = (self.winfo_screenheight() // 2) - (100)
        self.geometry(f"+{x}+{y}")

    def _on_cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()

    def update_overall(self, completed: int):
        percent = (completed / self.total_files) * 100
        self.overall_var.set(percent)
        self.overall_label.config(text=f"{completed} / {self.total_files} dosya")

    def update_current(self, filename: str, percent: float):
        self.current_var.set(percent)
        self.current_label.config(text=filename)

    def set_complete(self):
        self.overall_var.set(100)
        self.current_label.config(text="Tamamlandı!")
        self.cancel_btn.config(text="Kapat")
