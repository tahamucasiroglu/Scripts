"""Hazır dönüştürme profilleri"""
from typing import Dict, Any, Optional

# Preset yapısı
PRESETS: Dict[str, Dict[str, Any]] = {
    # ==================== SADECE FORMAT DEĞİŞTİR (EN HIZLI) ====================
    "Format Degistir (Kalite Korunur)": {
        "description": "Sadece kapsayici degisir, video/ses ayni kalir - ANINDA",
        "category": "copy",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "copy",
        "acodec": "copy",
        "gpu": False
    },
    "TS -> MP4 (Kalite Korunur)": {
        "description": "TS'den MP4'e kalite kaybi olmadan - ANINDA",
        "category": "copy",
        "input_formats": [".ts", ".m2ts"],
        "output_format": ".mp4",
        "vcodec": "copy",
        "acodec": "copy",
        "gpu": False
    },
    "MKV -> MP4 (Kalite Korunur)": {
        "description": "MKV'den MP4'e kalite kaybi olmadan - ANINDA",
        "category": "copy",
        "input_formats": [".mkv"],
        "output_format": ".mp4",
        "vcodec": "copy",
        "acodec": "copy",
        "gpu": False
    },
    "AVI -> MP4 (Kalite Korunur)": {
        "description": "AVI'den MP4'e kalite kaybi olmadan",
        "category": "copy",
        "input_formats": [".avi"],
        "output_format": ".mp4",
        "vcodec": "copy",
        "acodec": "copy",
        "gpu": False
    },

    # ==================== GPU İLE DÖNÜŞÜM (HIZLI) ====================
    "MP4 Donustur (GPU - Hizli)": {
        "description": "NVIDIA GPU ile hizli MP4 donusumu",
        "category": "video",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "5000k",
        "audio_bitrate": "192k",
        "preset": "fast",
        "gpu": True
    },
    "MP4 Donustur (GPU - Kaliteli)": {
        "description": "NVIDIA GPU ile kaliteli MP4 donusumu",
        "category": "video",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "8000k",
        "audio_bitrate": "256k",
        "preset": "slow",
        "gpu": True
    },
    "HEVC/H.265 (GPU - Kucuk Boyut)": {
        "description": "Yarisina kadar kucuk dosya boyutu",
        "category": "video",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "hevc_nvenc",
        "acodec": "aac",
        "bitrate": "4000k",
        "audio_bitrate": "192k",
        "preset": "fast",
        "gpu": True
    },

    # ==================== CPU İLE DÖNÜŞÜM (UYUMLU) ====================
    "MP4 Donustur (CPU - Standart)": {
        "description": "CPU ile standart MP4 donusumu",
        "category": "video",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "libx264",
        "acodec": "aac",
        "bitrate": "5000k",
        "audio_bitrate": "192k",
        "preset": "medium",
        "gpu": False
    },
    "MP4 Donustur (CPU - Hizli)": {
        "description": "CPU ile hizli MP4 donusumu (dusuk kalite)",
        "category": "video",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "libx264",
        "acodec": "aac",
        "bitrate": "4000k",
        "audio_bitrate": "192k",
        "preset": "veryfast",
        "gpu": False
    },
    "MP4 Donustur (CPU - Kaliteli)": {
        "description": "CPU ile yuksek kalite MP4 (yavas)",
        "category": "video",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "libx264",
        "acodec": "aac",
        "bitrate": "10000k",
        "audio_bitrate": "320k",
        "preset": "slow",
        "gpu": False
    },
    "HEVC/H.265 (CPU - Kucuk Boyut)": {
        "description": "CPU ile kucuk dosya boyutu (cok yavas)",
        "category": "video",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "libx265",
        "acodec": "aac",
        "bitrate": "3000k",
        "audio_bitrate": "192k",
        "preset": "medium",
        "gpu": False
    },
    "WebM/VP9 (Web icin)": {
        "description": "Web tarayicilari icin optimize",
        "category": "video",
        "input_formats": ["*"],
        "output_format": ".webm",
        "vcodec": "libvpx-vp9",
        "acodec": "libopus",
        "bitrate": "3000k",
        "audio_bitrate": "128k",
        "preset": None,
        "gpu": False
    },
    "XVID/AVI (Eski Cihazlar)": {
        "description": "Eski DVD oynaticilar ve cihazlar icin",
        "category": "video",
        "input_formats": ["*"],
        "output_format": ".avi",
        "vcodec": "libxvid",
        "acodec": "libmp3lame",
        "bitrate": "4000k",
        "audio_bitrate": "192k",
        "preset": None,
        "gpu": False
    },

    # ==================== SES ÇIKARMA ====================
    "Ses Cikar -> MP3 (320kbps)": {
        "description": "Videodan yuksek kalite MP3 cikar",
        "category": "audio",
        "input_formats": ["*"],
        "output_format": ".mp3",
        "vcodec": None,
        "acodec": "libmp3lame",
        "audio_bitrate": "320k",
        "audio_only": True,
        "gpu": False
    },
    "Ses Cikar -> MP3 (192kbps)": {
        "description": "Videodan standart MP3 cikar",
        "category": "audio",
        "input_formats": ["*"],
        "output_format": ".mp3",
        "vcodec": None,
        "acodec": "libmp3lame",
        "audio_bitrate": "192k",
        "audio_only": True,
        "gpu": False
    },
    "Ses Cikar -> WAV (Kayipsiz)": {
        "description": "Videodan kayipsiz WAV cikar",
        "category": "audio",
        "input_formats": ["*"],
        "output_format": ".wav",
        "vcodec": None,
        "acodec": "pcm_s16le",
        "audio_only": True,
        "gpu": False
    },
    "Ses Cikar -> AAC": {
        "description": "Videodan AAC ses cikar",
        "category": "audio",
        "input_formats": ["*"],
        "output_format": ".m4a",
        "vcodec": None,
        "acodec": "aac",
        "audio_bitrate": "256k",
        "audio_only": True,
        "gpu": False
    },
    "Ses Cikar -> FLAC (Kayipsiz)": {
        "description": "Videodan kayipsiz FLAC cikar",
        "category": "audio",
        "input_formats": ["*"],
        "output_format": ".flac",
        "vcodec": None,
        "acodec": "flac",
        "audio_only": True,
        "gpu": False
    },

    # ==================== HIZLANDIRMA/YAVAŞLATMA ====================
    "Video Hizlandir (2x)": {
        "description": "Videoyu 2 kat hizlandir",
        "category": "speed",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "5000k",
        "audio_bitrate": "192k",
        "preset": "fast",
        "speed": 2.0,
        "gpu": True
    },
    "Video Hizlandir (4x)": {
        "description": "Videoyu 4 kat hizlandir",
        "category": "speed",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "5000k",
        "audio_bitrate": "192k",
        "preset": "fast",
        "speed": 4.0,
        "gpu": True
    },
    "Video Hizlandir (10x)": {
        "description": "Videoyu 10 kat hizlandir (timelapse)",
        "category": "speed",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "5000k",
        "audio_bitrate": "192k",
        "preset": "fast",
        "speed": 10.0,
        "gpu": True
    },
    "Video Yavaslar (0.5x)": {
        "description": "Videoyu yari hizda oynat",
        "category": "speed",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "5000k",
        "audio_bitrate": "192k",
        "preset": "fast",
        "speed": 0.5,
        "gpu": True
    },
    "Video Yavaslar (0.25x)": {
        "description": "Videoyu ceyrek hizda oynat (slow motion)",
        "category": "speed",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "5000k",
        "audio_bitrate": "192k",
        "preset": "fast",
        "speed": 0.25,
        "gpu": True
    },

    # ==================== ÇÖZÜNÜRLÜK DEĞİŞTİRME ====================
    "1080p'ye Donustur": {
        "description": "Full HD (1920x1080) cozunurluge cevir",
        "category": "resize",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "5000k",
        "audio_bitrate": "192k",
        "preset": "fast",
        "resolution": "1920:1080",
        "gpu": True
    },
    "720p'ye Kucult": {
        "description": "HD (1280x720) cozunurluge kucult",
        "category": "resize",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "3000k",
        "audio_bitrate": "192k",
        "preset": "fast",
        "resolution": "1280:720",
        "gpu": True
    },
    "480p'ye Kucult": {
        "description": "SD (854x480) cozunurluge kucult",
        "category": "resize",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "1500k",
        "audio_bitrate": "128k",
        "preset": "fast",
        "resolution": "854:480",
        "gpu": True
    },
    "4K'ya Buyut": {
        "description": "4K UHD (3840x2160) cozunurluge buyut",
        "category": "resize",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "h264_nvenc",
        "acodec": "aac",
        "bitrate": "20000k",
        "audio_bitrate": "256k",
        "preset": "fast",
        "resolution": "3840:2160",
        "gpu": True
    },

    # ==================== ÖZEL ====================
    "Ozel Ayarlar": {
        "description": "Tum ayarlari kendin belirle",
        "category": "custom",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": "libx264",
        "acodec": "aac",
        "bitrate": "5000k",
        "audio_bitrate": "192k",
        "preset": "medium",
        "gpu": False,
        "custom": True
    }
}

# Video codec preset'leri (encoding hızı/kalite dengesi)
VIDEO_PRESETS = [
    "ultrafast",    # En hizli, en dusuk kalite
    "superfast",
    "veryfast",
    "faster",
    "fast",         # Hizli, iyi kalite
    "medium",       # Dengeli (varsayilan)
    "slow",         # Yavas, yuksek kalite
    "slower",
    "veryslow"      # En yavas, en yuksek kalite
]

# Çözünürlükler
RESOLUTIONS = {
    "Orijinal": None,
    "4K (3840x2160)": "3840:2160",
    "1440p (2560x1440)": "2560:1440",
    "1080p (1920x1080)": "1920:1080",
    "720p (1280x720)": "1280:720",
    "480p (854x480)": "854:480",
    "360p (640x360)": "640:360"
}

# FPS seçenekleri
FPS_OPTIONS = {
    "Orijinal": None,
    "60 fps": 60,
    "30 fps": 30,
    "24 fps (Sinema)": 24,
    "15 fps": 15
}

# Bitrate seçenekleri (kbps)
VIDEO_BITRATES = [
    500, 1000, 1500, 2000, 2500, 3000, 4000, 5000,
    6000, 8000, 10000, 15000, 20000, 25000, 30000, 50000
]

AUDIO_BITRATES = [
    64, 96, 128, 160, 192, 224, 256, 320
]


def get_preset(name: str) -> Optional[Dict[str, Any]]:
    """Preset al"""
    return PRESETS.get(name)


def get_presets_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Kategoriye göre preset'leri filtrele"""
    return {k: v for k, v in PRESETS.items() if v.get("category") == category}


def get_all_preset_names() -> list:
    """Tüm preset isimlerini döndür"""
    return list(PRESETS.keys())


def create_custom_preset(
    vcodec: str,
    acodec: str,
    bitrate: str,
    audio_bitrate: str,
    preset: Optional[str] = None,
    resolution: Optional[str] = None,
    fps: Optional[int] = None,
    speed: Optional[float] = None,
    brightness: Optional[float] = None,
    contrast: Optional[float] = None,
    saturation: Optional[float] = None
) -> Dict[str, Any]:
    """Özel preset oluştur"""
    custom = {
        "description": "Ozel ayarlar",
        "category": "custom",
        "input_formats": ["*"],
        "output_format": ".mp4",
        "vcodec": vcodec,
        "acodec": acodec,
        "bitrate": bitrate,
        "audio_bitrate": audio_bitrate,
        "gpu": "nvenc" in vcodec.lower() if vcodec else False
    }

    if preset:
        custom["preset"] = preset
    if resolution:
        custom["resolution"] = resolution
    if fps:
        custom["fps"] = fps
    if speed:
        custom["speed"] = speed
    if brightness is not None:
        custom["brightness"] = brightness
    if contrast is not None:
        custom["contrast"] = contrast
    if saturation is not None:
        custom["saturation"] = saturation

    return custom
