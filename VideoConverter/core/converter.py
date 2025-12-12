"""Video dönüştürme motoru"""
import subprocess
import threading
import os
from typing import Dict, Any, Optional, Callable
from .ffmpeg_utils import FFmpegUtils
from .installer import Installer


class VideoConverter:
    """FFmpeg tabanlı video dönüştürücü"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.is_cancelled = False
        self._progress_callback: Optional[Callable] = None
        self._complete_callback: Optional[Callable] = None
        self._error_callback: Optional[Callable] = None
        self.ffmpeg_path = Installer.get_ffmpeg_path()

    def set_callbacks(
        self,
        progress: Optional[Callable] = None,
        complete: Optional[Callable] = None,
        error: Optional[Callable] = None
    ):
        """Callback fonksiyonları ayarla"""
        self._progress_callback = progress
        self._complete_callback = complete
        self._error_callback = error

    def build_command(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any]
    ) -> list:
        """FFmpeg komutunu oluştur"""
        cmd = [self.ffmpeg_path, "-y", "-hide_banner"]

        # Girdi
        cmd.extend(["-i", input_path])

        # Video codec
        vcodec = settings.get("vcodec")
        if vcodec is None:
            cmd.extend(["-vn"])  # Video yok (sadece ses)
        elif vcodec == "copy":
            cmd.extend(["-c:v", "copy"])
        else:
            cmd.extend(["-c:v", vcodec])

            # Bitrate
            bitrate = settings.get("bitrate")
            if bitrate:
                cmd.extend(["-b:v", bitrate])

            # Preset
            preset = settings.get("preset")
            if preset:
                if "nvenc" in vcodec:
                    # NVENC preset mapping
                    nvenc_presets = {
                        "ultrafast": "p1",
                        "superfast": "p2",
                        "veryfast": "p3",
                        "faster": "p3",
                        "fast": "p4",
                        "medium": "p5",
                        "slow": "p6",
                        "slower": "p7",
                        "veryslow": "p7"
                    }
                    nvenc_preset = nvenc_presets.get(preset, preset)
                    cmd.extend(["-preset", nvenc_preset])
                else:
                    cmd.extend(["-preset", preset])

        # Ses codec
        acodec = settings.get("acodec")
        if acodec is None:
            cmd.extend(["-an"])  # Ses yok
        elif acodec == "copy":
            cmd.extend(["-c:a", "copy"])
        else:
            cmd.extend(["-c:a", acodec])

            # Ses bitrate
            audio_bitrate = settings.get("audio_bitrate")
            if audio_bitrate:
                cmd.extend(["-b:a", audio_bitrate])

        # Çözünürlük
        resolution = settings.get("resolution")
        if resolution:
            cmd.extend(["-vf", f"scale={resolution}"])

        # FPS
        fps = settings.get("fps")
        if fps:
            cmd.extend(["-r", str(fps)])

        # Hız değişikliği
        speed = settings.get("speed")
        if speed and speed != 1.0:
            video_filter = f"setpts={1/speed}*PTS"
            audio_filter = f"atempo={min(speed, 2.0)}"

            # Yüksek hızlar için atempo zincirleme
            if speed > 2.0:
                remaining = speed
                audio_filters = []
                while remaining > 2.0:
                    audio_filters.append("atempo=2.0")
                    remaining /= 2.0
                audio_filters.append(f"atempo={remaining}")
                audio_filter = ",".join(audio_filters)

            # Mevcut video filtresiyle birleştir
            existing_vf = None
            for i, arg in enumerate(cmd):
                if arg == "-vf":
                    existing_vf = i + 1
                    break

            if existing_vf:
                cmd[existing_vf] = f"{cmd[existing_vf]},{video_filter}"
            else:
                cmd.extend(["-vf", video_filter])

            cmd.extend(["-af", audio_filter])

        # Renk ayarları
        brightness = settings.get("brightness")
        contrast = settings.get("contrast")
        saturation = settings.get("saturation")

        color_filters = []
        if brightness is not None:
            color_filters.append(f"brightness={brightness}")
        if contrast is not None:
            color_filters.append(f"contrast={contrast}")
        if saturation is not None:
            color_filters.append(f"saturation={saturation}")

        if color_filters:
            eq_filter = f"eq={':'.join(color_filters)}"

            # Mevcut video filtresiyle birleştir
            existing_vf = None
            for i, arg in enumerate(cmd):
                if arg == "-vf":
                    existing_vf = i + 1
                    break

            if existing_vf:
                cmd[existing_vf] = f"{cmd[existing_vf]},{eq_filter}"
            else:
                cmd.extend(["-vf", eq_filter])

        # İlerleme bilgisi için
        cmd.extend(["-progress", "pipe:1"])

        # Çıktı
        cmd.append(output_path)

        return cmd

    def convert(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any],
        duration: float = 0
    ):
        """
        Dönüştürmeyi başlat (async thread'de)

        Args:
            input_path: Girdi dosya yolu
            output_path: Çıktı dosya yolu
            settings: Dönüştürme ayarları
            duration: Video süresi (ilerleme hesaplama için)
        """
        self.is_running = True
        self.is_cancelled = False

        thread = threading.Thread(
            target=self._convert_thread,
            args=(input_path, output_path, settings, duration)
        )
        thread.daemon = True
        thread.start()

    def _convert_thread(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any],
        duration: float
    ):
        """Dönüştürme thread'i"""
        try:
            cmd = self.build_command(input_path, output_path, settings)

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            for line in self.process.stdout:
                if self.is_cancelled:
                    self.process.terminate()
                    break

                # İlerleme parse et
                progress = FFmpegUtils.parse_progress(line, duration)
                if progress and self._progress_callback:
                    self._progress_callback(progress)

            self.process.wait()

            if self.is_cancelled:
                # İptal edildiyse çıktı dosyasını sil
                if os.path.exists(output_path):
                    os.remove(output_path)
                if self._error_callback:
                    self._error_callback("Dönüştürme iptal edildi")
            elif self.process.returncode == 0:
                if self._complete_callback:
                    self._complete_callback(output_path)
            else:
                if self._error_callback:
                    self._error_callback(f"FFmpeg hatası (kod: {self.process.returncode})")

        except Exception as e:
            if self._error_callback:
                self._error_callback(str(e))
        finally:
            self.is_running = False
            self.process = None

    def cancel(self):
        """Dönüştürmeyi iptal et"""
        self.is_cancelled = True
        if self.process:
            self.process.terminate()

    def convert_sync(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any]
    ) -> tuple:
        """
        Senkron dönüştürme (test/CLI için)

        Returns:
            (success: bool, message: str)
        """
        try:
            cmd = self.build_command(input_path, output_path, settings)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return True, "Dönüştürme başarılı"
            else:
                return False, result.stderr

        except Exception as e:
            return False, str(e)


class BatchConverter:
    """Toplu video dönüştürücü"""

    def __init__(self):
        self.converter = VideoConverter()
        self.queue: list = []
        self.current_index = 0
        self.is_running = False
        self._batch_progress_callback: Optional[Callable] = None
        self._batch_complete_callback: Optional[Callable] = None

    def add_to_queue(
        self,
        input_path: str,
        output_path: str,
        settings: Dict[str, Any]
    ):
        """Kuyruğa ekle"""
        self.queue.append({
            "input": input_path,
            "output": output_path,
            "settings": settings,
            "status": "pending"
        })

    def clear_queue(self):
        """Kuyruğu temizle"""
        self.queue.clear()
        self.current_index = 0

    def start(self):
        """Toplu dönüştürmeyi başlat"""
        if not self.queue:
            return

        self.is_running = True
        self.current_index = 0
        self._process_next()

    def _process_next(self):
        """Sıradaki dosyayı işle"""
        if self.current_index >= len(self.queue):
            self.is_running = False
            if self._batch_complete_callback:
                self._batch_complete_callback(self.queue)
            return

        item = self.queue[self.current_index]
        item["status"] = "processing"

        def on_complete(output):
            item["status"] = "completed"
            self.current_index += 1
            if self._batch_progress_callback:
                self._batch_progress_callback(self.current_index, len(self.queue))
            self._process_next()

        def on_error(error):
            item["status"] = "failed"
            item["error"] = error
            self.current_index += 1
            if self._batch_progress_callback:
                self._batch_progress_callback(self.current_index, len(self.queue))
            self._process_next()

        self.converter.set_callbacks(complete=on_complete, error=on_error)

        # Video bilgisi al
        info = FFmpegUtils.get_video_info(item["input"])
        duration = info.get("duration", 0) if info else 0

        self.converter.convert(
            item["input"],
            item["output"],
            item["settings"],
            duration
        )

    def cancel(self):
        """Toplu dönüştürmeyi iptal et"""
        self.converter.cancel()
        self.is_running = False
