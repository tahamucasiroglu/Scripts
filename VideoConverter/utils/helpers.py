"""Yardımcı fonksiyonlar"""
import os
from typing import Optional, Dict
from core.ffmpeg_utils import FFmpegUtils


def format_time(seconds: float) -> str:
    """Saniyeyi okunabilir formata çevir"""
    if seconds < 0:
        return "00:00"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_size(size_bytes: int) -> str:
    """Byte'ı okunabilir formata çevir"""
    if size_bytes < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"


def get_video_info(file_path: str) -> Optional[Dict]:
    """Video dosyası hakkında bilgi al"""
    return FFmpegUtils.get_video_info(file_path)


def generate_output_path(
    input_path: str,
    output_dir: str,
    output_format: str,
    suffix: str = "_converted"
) -> str:
    """Çıktı dosya yolunu oluştur"""
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_name = f"{base_name}{suffix}{output_format}"
    return os.path.join(output_dir, output_name)


def get_supported_formats() -> Dict[str, list]:
    """Desteklenen formatları döndür"""
    return {
        "video_input": [
            ".ts", ".m2ts", ".mp4", ".mkv", ".avi", ".mov",
            ".wmv", ".flv", ".webm", ".mpeg", ".mpg", ".3gp"
        ],
        "video_output": [
            ".mp4", ".mkv", ".avi", ".mov", ".webm"
        ],
        "audio_output": [
            ".mp3", ".wav", ".aac", ".m4a", ".flac", ".ogg"
        ]
    }


def is_video_file(file_path: str) -> bool:
    """Dosya video mu kontrol et"""
    ext = os.path.splitext(file_path)[1].lower()
    formats = get_supported_formats()
    return ext in formats["video_input"]


def validate_output_dir(output_dir: str) -> tuple:
    """Çıktı dizinini doğrula"""
    if not output_dir:
        return False, "Çıktı klasörü belirtilmedi"

    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            return True, "Klasör oluşturuldu"
        except Exception as e:
            return False, f"Klasör oluşturulamadı: {e}"

    if not os.path.isdir(output_dir):
        return False, "Belirtilen yol bir klasör değil"

    if not os.access(output_dir, os.W_OK):
        return False, "Klasöre yazma izni yok"

    return True, "OK"
