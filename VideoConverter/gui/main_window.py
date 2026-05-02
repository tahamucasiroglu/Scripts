"""Ana pencere"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional, Dict, Any

from core.ffmpeg_utils import FFmpegUtils
from core.converter import VideoConverter, BatchConverter
from core.presets import PRESETS, get_preset, get_all_preset_names
from core.estimator import Estimator
from core.i18n import I18N
from .settings_panel import SettingsPanel
from .progress_dialog import ProgressDialog, BatchProgressDialog


class MainWindow:
    """Ana uygulama penceresi"""

    def __init__(self, nvenc_available: bool = False, nvenc_encoders: list = None):
        self.root = tk.Tk()
        self.root.title("TM Video Converter - Taha Mucasiroglu Video Converter")
        self.root.geometry("850x780")
        self.root.minsize(700, 650)

        # Durum değişkenleri
        self.video_info: Optional[Dict] = None
        self.nvenc_available = nvenc_available
        self.nvenc_encoders = nvenc_encoders or []
        self.converter = VideoConverter()
        self.batch_converter = BatchConverter()
        self.source_files = []
        self.i18n = I18N(default_language="tr")

        # Stil
        self._setup_style()

        # Widget'ları oluştur
        self._create_widgets()

        # Başlangıç tahminini güncelle
        self._update_estimate()

    def _setup_style(self):
        """Tkinter stilini ayarla"""
        style = ttk.Style()
        style.theme_use("clam")

        # Buton stilleri
        style.configure("Convert.TButton", font=("", 11, "bold"), padding=10)
        style.configure("TLabelframe.Label", font=("", 10, "bold"))

    def _create_widgets(self):
        """Widget'ları oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Başlık
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 10))

        title_label = ttk.Label(
            title_frame,
            text="TM Video Converter",
            font=("", 16, "bold")
        )
        title_label.pack(side="left")

        # GPU durumu
        gpu_text = "GPU: Aktif (NVENC)" if self.nvenc_available else "GPU: Pasif (CPU)"
        gpu_color = "green" if self.nvenc_available else "gray"
        self.gpu_label = ttk.Label(title_frame, text=gpu_text, foreground=gpu_color)
        self.gpu_label.pack(side="right")

        self.language_var = tk.StringVar(value="tr")
        self.language_combo = ttk.Combobox(
            title_frame,
            textvariable=self.language_var,
            values=self.i18n.available_languages(),
            state="readonly",
            width=5
        )
        self.language_combo.pack(side="right", padx=10)
        self.language_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        # ==================== DOSYA SEÇİMİ ====================
        file_frame = ttk.LabelFrame(main_frame, text="Dosya Secimi", padding=10)
        file_frame.pack(fill="x", pady=5)

        # Kaynak video
        source_frame = ttk.Frame(file_frame)
        source_frame.pack(fill="x", pady=2)

        ttk.Label(source_frame, text="Kaynak Video:", width=15).pack(side="left")

        self.source_var = tk.StringVar()
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_var, width=50)
        self.source_entry.pack(side="left", fill="x", expand=True, padx=5)

        ttk.Button(source_frame, text="Sec...", command=self._select_source).pack(side="left")

        batch_frame = ttk.Frame(file_frame)
        batch_frame.pack(fill="x", pady=(8, 0))

        ttk.Label(batch_frame, text="Paralel Is:", width=15).pack(side="left")
        self.parallel_var = tk.IntVar(value=1)
        self.parallel_spin = ttk.Spinbox(
            batch_frame,
            from_=1,
            to=8,
            textvariable=self.parallel_var,
            width=5
        )
        self.parallel_spin.pack(side="left", padx=5)

        self.queue_label = ttk.Label(batch_frame, text="Secili dosya: 0", foreground="gray")
        self.queue_label.pack(side="left", padx=15)

        # Çıktı klasörü
        output_frame = ttk.Frame(file_frame)
        output_frame.pack(fill="x", pady=2)

        ttk.Label(output_frame, text="Cikti Klasoru:", width=15).pack(side="left")

        self.output_dir_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=5)

        ttk.Button(output_frame, text="Sec...", command=self._select_output_dir).pack(side="left")

        # Video bilgisi
        self.video_info_label = ttk.Label(
            file_frame,
            text="Video bilgisi: Dosya secilmedi",
            foreground="gray"
        )
        self.video_info_label.pack(anchor="w", pady=(10, 0))

        # ==================== DÖNÜŞÜM TİPİ ====================
        preset_frame = ttk.LabelFrame(main_frame, text="Donusum Tipi", padding=10)
        preset_frame.pack(fill="x", pady=5)

        ttk.Label(preset_frame, text="Profil:").pack(side="left")

        self.preset_var = tk.StringVar(value="TS -> MP4 (GPU Hizli)")
        self.preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=get_all_preset_names(),
            state="readonly",
            width=40
        )
        self.preset_combo.pack(side="left", padx=10)
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_change)

        # Preset açıklama
        self.preset_desc_label = ttk.Label(
            preset_frame,
            text="NVIDIA GPU ile hizli donusum",
            foreground="gray"
        )
        self.preset_desc_label.pack(side="left", padx=10)

        # ==================== AYARLAR PANELİ ====================
        self.settings_panel = SettingsPanel(main_frame, on_change=self._on_settings_change)
        self.settings_panel.pack(fill="x", pady=5)
        self.settings_panel.set_nvenc_available(self.nvenc_available)

        # ==================== TAHMİN ====================
        estimate_frame = ttk.LabelFrame(main_frame, text="Tahmin", padding=10)
        estimate_frame.pack(fill="x", pady=5)

        estimate_grid = ttk.Frame(estimate_frame)
        estimate_grid.pack(fill="x")

        ttk.Label(estimate_grid, text="Tahmini Boyut:").grid(row=0, column=0, sticky="w", padx=5)
        self.est_size_label = ttk.Label(estimate_grid, text="-", font=("", 10, "bold"))
        self.est_size_label.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(estimate_grid, text="Tahmini Sure:").grid(row=0, column=2, sticky="w", padx=20)
        self.est_duration_label = ttk.Label(estimate_grid, text="-", font=("", 10, "bold"))
        self.est_duration_label.grid(row=0, column=3, sticky="w", padx=5)

        ttk.Label(estimate_grid, text="Not:").grid(row=0, column=4, sticky="w", padx=20)
        self.est_info_label = ttk.Label(estimate_grid, text="-", foreground="gray")
        self.est_info_label.grid(row=0, column=5, sticky="w", padx=5)

        # ==================== DÖNÜŞTÜR BUTONU ====================
        self.convert_btn = ttk.Button(
            main_frame,
            text="DONUSTURMEYE BASLA",
            style="Convert.TButton",
            command=self._start_convert
        )
        self.convert_btn.pack(fill="x", pady=15)

        # ==================== DURUM ÇUBUĞU ====================
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", side="bottom")

        self.status_label = ttk.Label(status_frame, text="Hazir", foreground="gray")
        self.status_label.pack(side="left")

        # Başlangıç preset'ini uygula
        self._on_preset_change()

    def _select_source(self):
        """Kaynak video seç"""
        filetypes = [
            ("Medya Dosyalari", "*.ts *.m2ts *.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.mp3 *.wav *.m4a *.aac *.flac *.ogg"),
            ("Video Dosyalari", "*.ts *.m2ts *.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm"),
            ("Ses Dosyalari", "*.mp3 *.wav *.m4a *.aac *.flac *.ogg"),
            ("Tum Dosyalar", "*.*")
        ]
        paths = filedialog.askopenfilenames(filetypes=filetypes)
        if paths:
            self.source_files = list(paths)
            first_path = self.source_files[0]

            if len(self.source_files) == 1:
                self.source_var.set(first_path)
            else:
                self.source_var.set(f"{len(self.source_files)} dosya secildi")

            self.queue_label.config(text=f"Secili dosya: {len(self.source_files)}")
            self._load_video_info(first_path)

            # Çıktı klasörünü otomatik ayarla
            if not self.output_dir_var.get():
                self.output_dir_var.set(os.path.dirname(first_path))

    def _select_output_dir(self):
        """Çıktı klasörü seç"""
        path = filedialog.askdirectory()
        if path:
            self.output_dir_var.set(path)

    def _load_video_info(self, path: str):
        """Video bilgisini yükle"""
        self.status_label.config(text="Video bilgisi yukleniyor...")
        self.root.update()

        self.video_info = FFmpegUtils.get_video_info(path)

        if self.video_info:
            duration = self.video_info["duration"]
            width = self.video_info["width"]
            height = self.video_info["height"]
            fps = self.video_info["fps"]
            size_mb = self.video_info["size"] / (1024 * 1024)
            vcodec = self.video_info["video_codec"]

            info_text = (
                f"Sure: {self._format_time(duration)} | "
                f"Cozunurluk: {width}x{height} | "
                f"FPS: {fps} | "
                f"Boyut: {size_mb:.1f} MB | "
                f"Codec: {vcodec}"
            )
            self.video_info_label.config(text=info_text, foreground="black")
            self._update_estimate()
        else:
            self.video_info_label.config(
                text="Video bilgisi alinamadi!",
                foreground="red"
            )

        self.status_label.config(text="Hazir")

    def _on_preset_change(self, event=None):
        """Preset değiştiğinde"""
        preset_name = self.preset_var.get()
        preset = get_preset(preset_name)

        if preset:
            # Açıklamayı güncelle
            self.preset_desc_label.config(text=preset.get("description", ""))

            # Ayarları uygula
            self.settings_panel.apply_preset(preset)

            # Sadece ses modu
            audio_only = preset.get("audio_only", False)
            self.settings_panel.set_audio_only(audio_only)

            self._update_estimate()

    def _on_settings_change(self, settings: Dict[str, Any]):
        """Ayarlar değiştiğinde"""
        self._update_estimate()

    def _on_language_change(self, event=None):
        self.i18n.set_language(self.language_var.get())
        self.status_label.config(text=self.i18n.t("ready"))

    def _update_estimate(self):
        """Tahmini güncelle"""
        if not self.video_info:
            self.est_size_label.config(text="-")
            self.est_duration_label.config(text="-")
            self.est_info_label.config(text="-")
            return

        settings = self.settings_panel.get_settings()
        estimate = Estimator.estimate_with_preset(self.video_info, settings)

        self.est_size_label.config(text=estimate.get("size", "-"))
        self.est_duration_label.config(text=estimate.get("duration", "-"))
        self.est_info_label.config(text=estimate.get("info", "-"))

    def _start_convert(self):
        """Dönüştürmeyi başlat"""
        # Validasyon
        sources = self.source_files or ([self.source_var.get()] if self.source_var.get() else [])
        sources = [source for source in sources if source and os.path.exists(source)]
        if not sources:
            messagebox.showerror("Hata", "Gecerli bir kaynak video secin!")
            return

        if len(sources) > 1:
            self._start_batch_convert(sources)
            return

        source = sources[0]

        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showerror("Hata", "Cikti klasoru secin!")
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Hata", f"Klasor olusturulamadi: {e}")
                return

        # Çıktı dosya adı
        preset = get_preset(self.preset_var.get())
        output_format = preset.get("output_format", ".mp4") if preset else ".mp4"

        base_name = os.path.splitext(os.path.basename(source))[0]
        output_path = os.path.join(output_dir, f"{base_name}_converted{output_format}")

        # Dosya varsa sor
        if os.path.exists(output_path):
            if not messagebox.askyesno(
                "Dosya Var",
                f"'{os.path.basename(output_path)}' zaten mevcut.\nUzerine yazilsin mi?"
            ):
                return

        # Ayarları al
        settings = self.settings_panel.get_settings()

        # Ses-only kontrolü
        if preset and preset.get("audio_only"):
            settings["vcodec"] = None
            settings["audio_only"] = True

        # İlerleme dialog
        duration = self.video_info["duration"] if self.video_info else 0

        self.progress_dialog = ProgressDialog(
            self.root,
            title="Donusturuluyor...",
            on_cancel=self._cancel_convert
        )
        self.progress_dialog.set_file_info(os.path.basename(source), duration)

        # Callback'leri ayarla
        def on_progress(progress):
            progress["total_time"] = duration
            progress["status"] = "Kodlaniyor..."
            self.root.after(0, lambda: self.progress_dialog.update_progress(progress))

        def on_complete(output):
            self.root.after(0, lambda: self._on_convert_complete(output))

        def on_error(error):
            self.root.after(0, lambda: self._on_convert_error(error))

        self.converter.set_callbacks(
            progress=on_progress,
            complete=on_complete,
            error=on_error
        )

        # Dönüştürmeyi başlat
        self.convert_btn.config(state="disabled")
        self.converter.convert(source, output_path, settings, duration)

    def _start_batch_convert(self, sources):
        output_dir = self.output_dir_var.get()
        if not output_dir:
            messagebox.showerror("Hata", "Cikti klasoru secin!")
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("Hata", f"Klasor olusturulamadi: {e}")
                return

        preset = get_preset(self.preset_var.get())
        output_format = preset.get("output_format", ".mp4") if preset else ".mp4"
        settings = self.settings_panel.get_settings()

        if preset and preset.get("audio_only"):
            settings["vcodec"] = None
            settings["audio_only"] = True

        self.batch_converter.clear_queue()
        planned_outputs = set()
        for source in sources:
            output_path = self._make_output_path(source, output_dir, output_format, planned_outputs)
            planned_outputs.add(output_path.lower())
            self.batch_converter.add_to_queue(source, output_path, settings.copy())

        self.batch_dialog = BatchProgressDialog(
            self.root,
            total_files=len(sources),
            on_cancel=self._cancel_batch_convert
        )

        def on_batch_progress(completed, total, queue):
            self.root.after(0, lambda: self.batch_dialog.update_overall(completed))

        def on_item_progress(index, item, progress):
            filename = os.path.basename(item["input"])
            percent = progress.get("percent", item.get("progress", 0))
            self.root.after(0, lambda: self.batch_dialog.update_current(filename, percent))

        def on_batch_complete(queue):
            self.root.after(0, lambda: self._on_batch_complete(queue))

        self.batch_converter.set_callbacks(
            batch_progress=on_batch_progress,
            item_progress=on_item_progress,
            complete=on_batch_complete
        )

        self.convert_btn.config(state="disabled")
        self.status_label.config(text="Toplu donusturme calisiyor...")
        self.batch_converter.start(max_workers=self.parallel_var.get())

    def _make_output_path(self, source, output_dir, output_format, reserved=None):
        reserved = reserved or set()
        base_name = os.path.splitext(os.path.basename(source))[0]
        candidate = os.path.join(output_dir, f"{base_name}_converted{output_format}")
        counter = 2

        while os.path.exists(candidate) or candidate.lower() in reserved:
            candidate = os.path.join(output_dir, f"{base_name}_converted_{counter}{output_format}")
            counter += 1

        return candidate

    def _cancel_batch_convert(self):
        self.batch_converter.cancel()

    def _cancel_convert(self):
        """Dönüştürmeyi iptal et"""
        self.converter.cancel()

    def _on_convert_complete(self, output_path: str):
        """Dönüştürme tamamlandı"""
        self.progress_dialog.set_complete()
        self.convert_btn.config(state="normal")

        # Dosya boyutunu göster
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            size_mb = size / (1024 * 1024)
            if size_mb >= 1024:
                size_str = f"{size_mb/1024:.2f} GB"
            else:
                size_str = f"{size_mb:.1f} MB"

            messagebox.showinfo(
                "Tamamlandi",
                f"Dosya basariyla olusturuldu!\n\n"
                f"Konum: {output_path}\n"
                f"Boyut: {size_str}"
            )

    def _on_convert_error(self, error: str):
        """Dönüştürme hatası"""
        self.progress_dialog.set_error(error)
        self.convert_btn.config(state="normal")

    def _on_batch_complete(self, queue):
        completed = sum(1 for item in queue if item.get("status") == "completed")
        failed = sum(1 for item in queue if item.get("status") == "failed")
        cancelled = sum(1 for item in queue if item.get("status") == "cancelled")

        self.batch_dialog.set_complete()
        self.convert_btn.config(state="normal")
        self.status_label.config(text="Hazir")

        details = []
        for item in queue:
            if item.get("status") != "completed":
                details.append(f"- {os.path.basename(item['input'])}: {item.get('error', item.get('status'))}")

        message = (
            f"Toplu donusturme tamamlandi.\n\n"
            f"Basarili: {completed}\n"
            f"Hatali: {failed}\n"
            f"Iptal: {cancelled}"
        )
        if details:
            message += "\n\nHatalar:\n" + "\n".join(details[:10])

        messagebox.showinfo("Toplu Donusturme", message)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Süreyi formatla"""
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    def run(self):
        """Uygulamayı çalıştır"""
        self.root.mainloop()
