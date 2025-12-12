"""Dosya boyutu ve süre tahmini"""
from typing import Dict, Optional, Tuple


class Estimator:
    """Dönüştürme tahmini hesaplama"""

    # Ortalama encoding hızları (x gerçek zamanlı)
    # CPU encoding ortalama hızları
    CPU_SPEEDS = {
        "ultrafast": 15.0,
        "superfast": 10.0,
        "veryfast": 7.0,
        "faster": 5.0,
        "fast": 3.5,
        "medium": 2.5,
        "slow": 1.2,
        "slower": 0.6,
        "veryslow": 0.3
    }

    # GPU (NVENC) encoding ortalama hızları
    GPU_SPEEDS = {
        "p1": 50.0,
        "p2": 40.0,
        "p3": 30.0,
        "p4": 20.0,
        "p5": 15.0,
        "p6": 10.0,
        "p7": 7.0,
        "fast": 30.0,
        "medium": 20.0,
        "slow": 10.0
    }

    @staticmethod
    def estimate_file_size(
        duration: float,
        video_bitrate: int,
        audio_bitrate: int = 192,
        audio_only: bool = False,
        copy_mode: bool = False
    ) -> int:
        """
        Tahmini dosya boyutu hesapla

        Args:
            duration: Video süresi (saniye)
            video_bitrate: Video bitrate (kbps)
            audio_bitrate: Audio bitrate (kbps)
            audio_only: Sadece ses mi
            copy_mode: Sadece format değiştirme (codec kopyalama)

        Returns:
            Tahmini boyut (byte)
        """
        # Copy modunda orijinal boyut korunur (tahmin yapılamaz)
        if copy_mode:
            return 0  # Bilinmiyor

        # None değerleri varsayılana çevir
        if video_bitrate is None:
            video_bitrate = 0
        if audio_bitrate is None:
            audio_bitrate = 192

        if audio_only:
            # Sadece ses: bitrate * süre / 8 (bit -> byte)
            size_bytes = (audio_bitrate * 1000 * duration) / 8
        else:
            # Video + Ses
            total_bitrate = video_bitrate + audio_bitrate  # kbps
            size_bytes = (total_bitrate * 1000 * duration) / 8

        # %5 overhead ekle (container, metadata vs.)
        size_bytes *= 1.05

        return int(size_bytes)

    @staticmethod
    def estimate_duration(
        video_duration: float,
        preset: str,
        is_gpu: bool,
        speed_factor: float = 1.0
    ) -> float:
        """
        Tahmini dönüştürme süresi hesapla

        Args:
            video_duration: Video süresi (saniye)
            preset: Encoding preset
            is_gpu: GPU kullanılıyor mu
            speed_factor: Video hız faktörü (2x hızlandırma = 0.5 süre)

        Returns:
            Tahmini süre (saniye)
        """
        if is_gpu:
            speed = Estimator.GPU_SPEEDS.get(preset, 20.0)
        else:
            speed = Estimator.CPU_SPEEDS.get(preset, 2.5)

        # Temel süre: video süresi / encoding hızı
        base_duration = video_duration / speed

        # Hız faktörü uygula (hızlandırma daha az veri = daha hızlı)
        if speed_factor > 1:
            base_duration /= speed_factor

        return base_duration

    @staticmethod
    def format_estimate(
        file_size: int,
        duration: float,
        video_info: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Tahminleri okunabilir formatta döndür

        Returns:
            {"size": "2.5 GB", "duration": "15 dk 30 sn", "info": "..."}
        """
        result = {}

        # Boyut formatla
        if file_size == 0:
            result["size"] = "~Ayni (kopyalama)"
        elif file_size >= 1024**3:
            result["size"] = f"{file_size / (1024**3):.2f} GB"
        elif file_size >= 1024**2:
            result["size"] = f"{file_size / (1024**2):.1f} MB"
        else:
            result["size"] = f"{file_size / 1024:.0f} KB"

        # Süre formatla
        if duration >= 3600:
            hours = int(duration // 3600)
            mins = int((duration % 3600) // 60)
            secs = int(duration % 60)
            result["duration"] = f"{hours} sa {mins} dk {secs} sn"
        elif duration >= 60:
            mins = int(duration // 60)
            secs = int(duration % 60)
            result["duration"] = f"{mins} dk {secs} sn"
        else:
            result["duration"] = f"{int(duration)} sn"

        # Ek bilgi
        if video_info:
            original_size = video_info.get("size", 0)
            if original_size > 0:
                ratio = file_size / original_size
                if ratio < 1:
                    result["info"] = f"~%{int((1-ratio)*100)} küçültme"
                elif ratio > 1:
                    result["info"] = f"~%{int((ratio-1)*100)} büyüme"
                else:
                    result["info"] = "~Aynı boyut"

        return result

    @staticmethod
    def calculate_speed_effect(speed: float, duration: float) -> Tuple[float, float]:
        """
        Hız değişikliğinin etkisini hesapla

        Args:
            speed: Hız faktörü (2.0 = 2x hızlı, 0.5 = yarı hız)
            duration: Orijinal süre

        Returns:
            (yeni_süre, frame_drop_oranı)
        """
        new_duration = duration / speed

        # Frame drop oranı (yüksek hızlarda frame atlanır)
        if speed > 1:
            frame_drop = 1 - (1 / speed)
        else:
            frame_drop = 0

        return new_duration, frame_drop

    @staticmethod
    def estimate_with_preset(
        video_info: Dict,
        preset_settings: Dict
    ) -> Dict[str, str]:
        """
        Preset ile tam tahmin yap

        Args:
            video_info: Video bilgisi (duration, size, bitrate vs.)
            preset_settings: Preset ayarları

        Returns:
            Formatlanmış tahmin
        """
        duration = video_info.get("duration", 0)
        audio_only = preset_settings.get("audio_only", False)
        speed = preset_settings.get("speed", 1.0)

        # Bitrate parse et
        bitrate_str = preset_settings.get("bitrate", "5000k")
        if isinstance(bitrate_str, str):
            video_bitrate = int(bitrate_str.replace("k", "").replace("K", ""))
        else:
            video_bitrate = bitrate_str

        audio_bitrate_str = preset_settings.get("audio_bitrate", "192k")
        if isinstance(audio_bitrate_str, str):
            audio_bitrate = int(audio_bitrate_str.replace("k", "").replace("K", ""))
        else:
            audio_bitrate = audio_bitrate_str

        # Hız etkisi
        if speed != 1.0:
            duration = duration / speed

        # Copy mode kontrolü
        vcodec = preset_settings.get("vcodec", "")
        copy_mode = (
            vcodec == "copy" or
            preset_settings.get("category") == "copy" or
            preset_settings.get("copy_mode", False)
        )

        # Boyut tahmini
        file_size = Estimator.estimate_file_size(
            duration, video_bitrate, audio_bitrate, audio_only, copy_mode
        )

        # Süre tahmini
        if copy_mode:
            # Copy modunda sadece kopyalama yapılır, çok hızlı
            # Tahmini: 100 MB/s I/O hızı varsayarak
            file_size_mb = video_info.get("size", 0) / (1024 * 1024)
            encoding_duration = max(1, file_size_mb / 100)  # En az 1 saniye
        else:
            is_gpu = preset_settings.get("gpu", False)
            preset_name = preset_settings.get("preset", "medium")
            encoding_duration = Estimator.estimate_duration(
                video_info.get("duration", 0),
                preset_name or "medium",
                is_gpu,
                speed
            )

        return Estimator.format_estimate(file_size, encoding_duration, video_info)
