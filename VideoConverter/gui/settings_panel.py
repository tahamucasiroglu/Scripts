"""Ayarlar paneli"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional
from core.presets import (
    VIDEO_PRESETS, RESOLUTIONS, FPS_OPTIONS,
    VIDEO_BITRATES, AUDIO_BITRATES
)


# Codec tanımları
GPU_VIDEO_CODECS = [
    ("h264_nvenc", "H.264 (GPU - Hizli)"),
    ("hevc_nvenc", "H.265/HEVC (GPU - Kucuk Boyut)"),
]

CPU_VIDEO_CODECS = [
    ("libx264", "H.264 (CPU - Uyumlu)"),
    ("libx265", "H.265/HEVC (CPU - Kucuk Boyut)"),
    ("libxvid", "XVID (CPU - Eski Uyumluluk)"),
    ("mpeg4", "MPEG-4 (CPU - Eski Format)"),
    ("libvpx-vp9", "VP9 (CPU - Web)"),
]

COPY_CODEC = [
    ("copy", "Kopyala (Kalite Korunur - Cok Hizli)"),
]

AUDIO_CODECS = [
    ("aac", "AAC (Standart)"),
    ("libmp3lame", "MP3 (Uyumlu)"),
    ("ac3", "AC3 (DVD/Bluray)"),
    ("flac", "FLAC (Kayipsiz)"),
    ("pcm_s16le", "WAV/PCM (Kayipsiz)"),
    ("libopus", "Opus (Kucuk Boyut)"),
    ("copy", "Kopyala (Degistirme)"),
]


class SettingsPanel(ttk.LabelFrame):
    """Video/Ses ayarları paneli"""

    def __init__(self, parent, on_change: Optional[Callable] = None):
        super().__init__(parent, text="Ayarlar", padding=10)
        self.on_change = on_change
        self.nvenc_available = False
        self.use_gpu = True  # Varsayılan GPU

        self._create_widgets()

    def _create_widgets(self):
        """Widget'ları oluştur"""

        # ==================== İŞLEMCİ SEÇİMİ (GPU/CPU) ====================
        processor_frame = ttk.LabelFrame(self, text="Islemci Secimi", padding=5)
        processor_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.processor_var = tk.StringVar(value="gpu")

        self.gpu_radio = ttk.Radiobutton(
            processor_frame,
            text="GPU (NVIDIA - Cok Hizli)",
            variable=self.processor_var,
            value="gpu",
            command=self._on_processor_change
        )
        self.gpu_radio.pack(side="left", padx=20)

        self.cpu_radio = ttk.Radiobutton(
            processor_frame,
            text="CPU (Yavas ama Her Yerde Calisir)",
            variable=self.processor_var,
            value="cpu",
            command=self._on_processor_change
        )
        self.cpu_radio.pack(side="left", padx=20)

        self.copy_radio = ttk.Radiobutton(
            processor_frame,
            text="Sadece Format Degistir (En Hizli)",
            variable=self.processor_var,
            value="copy",
            command=self._on_processor_change
        )
        self.copy_radio.pack(side="left", padx=20)

        # ==================== VIDEO AYARLARI ====================
        video_frame = ttk.LabelFrame(self, text="Video Ayarlari", padding=5)
        video_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Video Codec
        ttk.Label(video_frame, text="Video Codec:").grid(row=0, column=0, sticky="w", pady=2)
        self.vcodec_var = tk.StringVar(value="h264_nvenc")
        self.vcodec_combo = ttk.Combobox(
            video_frame,
            textvariable=self.vcodec_var,
            state="readonly",
            width=30
        )
        self.vcodec_combo.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.vcodec_combo.bind("<<ComboboxSelected>>", self._on_setting_change)

        # Video Bitrate
        ttk.Label(video_frame, text="Bitrate (kbps):").grid(row=1, column=0, sticky="w", pady=2)
        self.bitrate_var = tk.StringVar(value="5000")
        self.bitrate_combo = ttk.Combobox(
            video_frame,
            textvariable=self.bitrate_var,
            values=[str(b) for b in VIDEO_BITRATES],
            width=30
        )
        self.bitrate_combo.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.bitrate_combo.bind("<<ComboboxSelected>>", self._on_setting_change)
        self.bitrate_combo.bind("<KeyRelease>", self._on_setting_change)

        # Preset (hız/kalite dengesi)
        ttk.Label(video_frame, text="Kalite/Hiz:").grid(row=2, column=0, sticky="w", pady=2)
        self.preset_var = tk.StringVar(value="fast")
        self.preset_combo = ttk.Combobox(
            video_frame,
            textvariable=self.preset_var,
            values=VIDEO_PRESETS,
            state="readonly",
            width=30
        )
        self.preset_combo.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_setting_change)

        # Çözünürlük
        ttk.Label(video_frame, text="Cozunurluk:").grid(row=3, column=0, sticky="w", pady=2)
        self.resolution_var = tk.StringVar(value="Orijinal")
        self.resolution_combo = ttk.Combobox(
            video_frame,
            textvariable=self.resolution_var,
            values=list(RESOLUTIONS.keys()),
            state="readonly",
            width=30
        )
        self.resolution_combo.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.resolution_combo.bind("<<ComboboxSelected>>", self._on_setting_change)

        # FPS
        ttk.Label(video_frame, text="FPS:").grid(row=4, column=0, sticky="w", pady=2)
        self.fps_var = tk.StringVar(value="Orijinal")
        self.fps_combo = ttk.Combobox(
            video_frame,
            textvariable=self.fps_var,
            values=list(FPS_OPTIONS.keys()),
            state="readonly",
            width=30
        )
        self.fps_combo.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        self.fps_combo.bind("<<ComboboxSelected>>", self._on_setting_change)

        # ==================== SES AYARLARI ====================
        audio_frame = ttk.LabelFrame(self, text="Ses Ayarlari", padding=5)
        audio_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Audio Codec
        ttk.Label(audio_frame, text="Ses Codec:").grid(row=0, column=0, sticky="w", pady=2)
        self.acodec_var = tk.StringVar(value="aac")
        self.acodec_combo = ttk.Combobox(
            audio_frame,
            textvariable=self.acodec_var,
            values=[f"{c[0]} - {c[1]}" for c in AUDIO_CODECS],
            state="readonly",
            width=25
        )
        self.acodec_combo.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.acodec_combo.bind("<<ComboboxSelected>>", self._on_audio_codec_change)

        # Audio Bitrate
        ttk.Label(audio_frame, text="Ses Bitrate:").grid(row=1, column=0, sticky="w", pady=2)
        self.audio_bitrate_var = tk.StringVar(value="192")
        self.audio_bitrate_combo = ttk.Combobox(
            audio_frame,
            textvariable=self.audio_bitrate_var,
            values=[str(b) for b in AUDIO_BITRATES],
            state="readonly",
            width=25
        )
        self.audio_bitrate_combo.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.audio_bitrate_combo.bind("<<ComboboxSelected>>", self._on_setting_change)

        # ==================== HIZ AYARLARI ====================
        speed_frame = ttk.LabelFrame(self, text="Hiz Ayarlari", padding=5)
        speed_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # Hız aktif/pasif
        self.speed_enabled_var = tk.BooleanVar(value=False)
        self.speed_check = ttk.Checkbutton(
            speed_frame,
            text="Video Hizini Degistir",
            variable=self.speed_enabled_var,
            command=self._toggle_speed
        )
        self.speed_check.grid(row=0, column=0, columnspan=3, sticky="w", pady=2)

        # Hız değeri
        ttk.Label(speed_frame, text="Hiz:").grid(row=1, column=0, sticky="w", pady=2)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(
            speed_frame,
            from_=0.25,
            to=10.0,
            variable=self.speed_var,
            orient="horizontal",
            length=120,
            command=self._on_speed_change
        )
        self.speed_scale.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.speed_scale.state(["disabled"])

        self.speed_label = ttk.Label(speed_frame, text="1.0x", width=6)
        self.speed_label.grid(row=1, column=2, sticky="w", padx=5)

        # Hızlı preset butonları
        speed_presets_frame = ttk.Frame(speed_frame)
        speed_presets_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=2)

        for speed in [0.5, 1.0, 2.0, 4.0, 10.0]:
            btn = ttk.Button(
                speed_presets_frame,
                text=f"{speed}x",
                width=5,
                command=lambda s=speed: self._set_speed(s)
            )
            btn.pack(side="left", padx=2)

        # ==================== RENK AYARLARI ====================
        color_frame = ttk.LabelFrame(self, text="Renk Ayarlari", padding=5)
        color_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

        # Renk aktif/pasif
        self.color_enabled_var = tk.BooleanVar(value=False)
        self.color_check = ttk.Checkbutton(
            color_frame,
            text="Renk Duzenle",
            variable=self.color_enabled_var,
            command=self._toggle_color
        )
        self.color_check.grid(row=0, column=0, columnspan=3, sticky="w", pady=2)

        # Parlaklık
        ttk.Label(color_frame, text="Parlaklik:").grid(row=1, column=0, sticky="w", pady=2)
        self.brightness_var = tk.DoubleVar(value=0)
        self.brightness_scale = ttk.Scale(
            color_frame,
            from_=-1.0,
            to=1.0,
            variable=self.brightness_var,
            orient="horizontal",
            length=100,
            command=self._on_color_change
        )
        self.brightness_scale.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.brightness_scale.state(["disabled"])
        self.brightness_label = ttk.Label(color_frame, text="0", width=5)
        self.brightness_label.grid(row=1, column=2)

        # Kontrast
        ttk.Label(color_frame, text="Kontrast:").grid(row=2, column=0, sticky="w", pady=2)
        self.contrast_var = tk.DoubleVar(value=1.0)
        self.contrast_scale = ttk.Scale(
            color_frame,
            from_=0.0,
            to=2.0,
            variable=self.contrast_var,
            orient="horizontal",
            length=100,
            command=self._on_color_change
        )
        self.contrast_scale.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.contrast_scale.state(["disabled"])
        self.contrast_label = ttk.Label(color_frame, text="1.0", width=5)
        self.contrast_label.grid(row=2, column=2)

        # Doygunluk
        ttk.Label(color_frame, text="Doygunluk:").grid(row=3, column=0, sticky="w", pady=2)
        self.saturation_var = tk.DoubleVar(value=1.0)
        self.saturation_scale = ttk.Scale(
            color_frame,
            from_=0.0,
            to=3.0,
            variable=self.saturation_var,
            orient="horizontal",
            length=100,
            command=self._on_color_change
        )
        self.saturation_scale.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.saturation_scale.state(["disabled"])
        self.saturation_label = ttk.Label(color_frame, text="1.0", width=5)
        self.saturation_label.grid(row=3, column=2)

        # Sıfırla butonu
        self.reset_color_btn = ttk.Button(
            color_frame,
            text="Sifirla",
            command=self._reset_colors,
            state="disabled"
        )
        self.reset_color_btn.grid(row=4, column=0, columnspan=3, pady=5)

        # Grid weight
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Başlangıç codec listesini güncelle
        self._update_video_codecs()

    def _update_video_codecs(self):
        """İşlemciye göre video codec listesini güncelle"""
        processor = self.processor_var.get()

        if processor == "copy":
            codecs = COPY_CODEC
            self.vcodec_var.set("copy")
            # Copy modunda diğer ayarları devre dışı bırak
            self._set_encoding_options_state("disabled")
        elif processor == "gpu" and self.nvenc_available:
            codecs = GPU_VIDEO_CODECS + CPU_VIDEO_CODECS + COPY_CODEC
            if "nvenc" not in self.vcodec_var.get():
                self.vcodec_var.set("h264_nvenc")
            self._set_encoding_options_state("!disabled")
        else:
            # CPU veya GPU yok
            codecs = CPU_VIDEO_CODECS + COPY_CODEC
            if "nvenc" in self.vcodec_var.get():
                self.vcodec_var.set("libx264")
            self._set_encoding_options_state("!disabled")

        self.vcodec_combo.config(values=[f"{c[0]} - {c[1]}" for c in codecs])

    def _set_encoding_options_state(self, state: str):
        """Encoding ayarlarının durumunu değiştir"""
        self.bitrate_combo.state([state])
        self.preset_combo.state([state])
        self.resolution_combo.state([state])
        self.fps_combo.state([state])

    def _on_processor_change(self):
        """İşlemci değiştiğinde"""
        self._update_video_codecs()
        self._on_setting_change()

    def _on_audio_codec_change(self, event=None):
        """Ses codec değiştiğinde"""
        selection = self.acodec_combo.get()
        # "copy - Kopyala..." formatından codec adını al
        codec = selection.split(" - ")[0] if " - " in selection else selection
        self.acodec_var.set(codec)

        # Copy ise bitrate'i devre dışı bırak
        if codec == "copy":
            self.audio_bitrate_combo.state(["disabled"])
        else:
            self.audio_bitrate_combo.state(["!disabled"])

        self._on_setting_change()

    def _on_setting_change(self, event=None):
        """Ayar değiştiğinde"""
        # Codec combobox'tan gerçek codec adını al
        vcodec_selection = self.vcodec_combo.get()
        if " - " in vcodec_selection:
            self.vcodec_var.set(vcodec_selection.split(" - ")[0])

        if self.on_change:
            self.on_change(self.get_settings())

    def _on_speed_change(self, value):
        """Hız slider değişti"""
        speed = round(float(value), 2)
        self.speed_label.config(text=f"{speed}x")
        self._on_setting_change()

    def _on_color_change(self, value=None):
        """Renk slider değişti"""
        self.brightness_label.config(text=f"{self.brightness_var.get():.1f}")
        self.contrast_label.config(text=f"{self.contrast_var.get():.1f}")
        self.saturation_label.config(text=f"{self.saturation_var.get():.1f}")
        self._on_setting_change()

    def _toggle_speed(self):
        """Hız ayarlarını aç/kapat"""
        if self.speed_enabled_var.get():
            self.speed_scale.state(["!disabled"])
        else:
            self.speed_scale.state(["disabled"])
            self.speed_var.set(1.0)
            self.speed_label.config(text="1.0x")
        self._on_setting_change()

    def _toggle_color(self):
        """Renk ayarlarını aç/kapat"""
        if self.color_enabled_var.get():
            self.brightness_scale.state(["!disabled"])
            self.contrast_scale.state(["!disabled"])
            self.saturation_scale.state(["!disabled"])
            self.reset_color_btn.config(state="normal")
        else:
            self.brightness_scale.state(["disabled"])
            self.contrast_scale.state(["disabled"])
            self.saturation_scale.state(["disabled"])
            self.reset_color_btn.config(state="disabled")
            self._reset_colors()
        self._on_setting_change()

    def _set_speed(self, speed: float):
        """Hızı ayarla"""
        self.speed_enabled_var.set(True)
        self._toggle_speed()
        self.speed_var.set(speed)
        self.speed_label.config(text=f"{speed}x")
        self._on_setting_change()

    def _reset_colors(self):
        """Renkleri sıfırla"""
        self.brightness_var.set(0)
        self.contrast_var.set(1.0)
        self.saturation_var.set(1.0)
        self._on_color_change()

    def set_nvenc_available(self, available: bool):
        """NVENC kullanılabilirliğini ayarla"""
        self.nvenc_available = available
        if not available:
            # GPU seçeneğini devre dışı bırak
            self.gpu_radio.config(state="disabled")
            self.processor_var.set("cpu")
            self._update_video_codecs()
        else:
            self.gpu_radio.config(state="normal")

    def apply_preset(self, preset: Dict[str, Any]):
        """Preset ayarlarını uygula"""
        # İşlemci seçimi
        if preset.get("vcodec") == "copy":
            self.processor_var.set("copy")
        elif preset.get("gpu") and self.nvenc_available:
            self.processor_var.set("gpu")
        else:
            self.processor_var.set("cpu")

        self._update_video_codecs()

        if "vcodec" in preset and preset["vcodec"]:
            vcodec = preset["vcodec"]
            # GPU yoksa CPU'ya düş
            if not self.nvenc_available and "nvenc" in vcodec:
                vcodec = "libx264" if "264" in vcodec else "libx265"
            self.vcodec_var.set(vcodec)
            # Combobox'ta göster
            for item in self.vcodec_combo.cget("values"):
                if item.startswith(vcodec):
                    self.vcodec_combo.set(item)
                    break

        if "acodec" in preset and preset["acodec"]:
            acodec = preset["acodec"]
            self.acodec_var.set(acodec)
            for item in self.acodec_combo.cget("values"):
                if item.startswith(acodec):
                    self.acodec_combo.set(item)
                    break

        if "bitrate" in preset and preset["bitrate"]:
            br = str(preset["bitrate"]).replace("k", "").replace("K", "")
            self.bitrate_var.set(br)

        if "audio_bitrate" in preset and preset["audio_bitrate"]:
            abr = str(preset["audio_bitrate"]).replace("k", "").replace("K", "")
            self.audio_bitrate_var.set(abr)

        if "preset" in preset and preset["preset"]:
            self.preset_var.set(preset["preset"])

        if "speed" in preset:
            self._set_speed(preset["speed"])
        else:
            self.speed_enabled_var.set(False)
            self._toggle_speed()

        self._on_setting_change()

    def get_settings(self) -> Dict[str, Any]:
        """Mevcut ayarları al"""
        vcodec = self.vcodec_var.get()
        acodec = self.acodec_var.get()

        settings = {
            "vcodec": vcodec,
            "acodec": acodec,
            "bitrate": f"{self.bitrate_var.get()}k",
            "audio_bitrate": f"{self.audio_bitrate_var.get()}k",
            "preset": self.preset_var.get(),
            "gpu": "nvenc" in vcodec,
            "copy_mode": vcodec == "copy" and acodec == "copy"
        }

        # Copy modunda bitrate vs. gereksiz
        if vcodec == "copy":
            settings["bitrate"] = None
            settings["preset"] = None

        if acodec == "copy":
            settings["audio_bitrate"] = None

        # Çözünürlük
        res = self.resolution_var.get()
        if res != "Orijinal":
            settings["resolution"] = RESOLUTIONS.get(res)

        # FPS
        fps = self.fps_var.get()
        if fps != "Orijinal":
            settings["fps"] = FPS_OPTIONS.get(fps)

        # Hız
        if self.speed_enabled_var.get():
            settings["speed"] = round(self.speed_var.get(), 2)

        # Renk
        if self.color_enabled_var.get():
            settings["brightness"] = round(self.brightness_var.get(), 2)
            settings["contrast"] = round(self.contrast_var.get(), 2)
            settings["saturation"] = round(self.saturation_var.get(), 2)

        return settings

    def set_audio_only(self, audio_only: bool):
        """Sadece ses modunu ayarla"""
        if audio_only:
            self.gpu_radio.state(["disabled"])
            self.cpu_radio.state(["disabled"])
            self.copy_radio.state(["disabled"])
            self.vcodec_combo.state(["disabled"])
            self.bitrate_combo.state(["disabled"])
            self.preset_combo.state(["disabled"])
            self.resolution_combo.state(["disabled"])
            self.fps_combo.state(["disabled"])
            self.speed_check.state(["disabled"])
            self.color_check.state(["disabled"])
        else:
            if self.nvenc_available:
                self.gpu_radio.state(["!disabled"])
            self.cpu_radio.state(["!disabled"])
            self.copy_radio.state(["!disabled"])
            self.vcodec_combo.state(["!disabled"])
            self.bitrate_combo.state(["!disabled"])
            self.preset_combo.state(["!disabled"])
            self.resolution_combo.state(["!disabled"])
            self.fps_combo.state(["!disabled"])
            self.speed_check.state(["!disabled"])
            self.color_check.state(["!disabled"])
